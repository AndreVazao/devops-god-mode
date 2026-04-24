from __future__ import annotations

import ast
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Set

from app.utils.atomic_json_store import AtomicJsonStore

DATA_DIR = Path("data")
REPORT_FILE = DATA_DIR / "system_integrity_audit_report.json"
REPORT_STORE = AtomicJsonStore(REPORT_FILE, default_factory=dict)

WORKFLOW_ALLOWED_EXACT = {
    "universal-total-test.yml",
    "build.yml",
    "android-apk-build.yml",
    "windows-exe-build.yml",
}
WORKFLOW_ALLOWED_TOKENS = ("prune", "apk", "android", "exe", "windows")
CRITICAL_ROUTE_NAMES = {
    "system_integrity_audit",
    "operator_command_intake",
    "multi_ai_conversation_inventory",
    "repo_relationship_graph",
    "vault_deploy_env_planner",
    "mobile_approval_cockpit_v2",
    "approved_card_execution_queue",
}


class SystemIntegrityAuditService:
    """Self-audit layer for the God Mode repository.

    The audit is local/read-only. It scans the checked-out repository structure,
    detects likely orphan routes/services/docs/workflows, and writes a report that
    the mobile cockpit can review before the project moves into real executors.
    """

    def get_status(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "mode": "system_integrity_audit_status",
            "status": "system_integrity_audit_ready",
            "report_file": str(REPORT_FILE),
            "atomic_store_enabled": True,
        }

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def _rel(self, path: Path) -> str:
        try:
            return str(path.relative_to(Path.cwd())).replace("\\", "/")
        except ValueError:
            return str(path).replace("\\", "/")

    def _py_files(self, folder: Path) -> List[Path]:
        if not folder.exists():
            return []
        return sorted(path for path in folder.rglob("*.py") if "__pycache__" not in path.parts)

    def _workflow_files(self) -> List[Path]:
        folder = Path(".github/workflows")
        if not folder.exists():
            return []
        return sorted(path for path in folder.glob("*.yml")) + sorted(path for path in folder.glob("*.yaml"))

    def _safe_read(self, path: Path) -> str:
        try:
            return path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            return path.read_text(encoding="utf-8", errors="ignore")
        except FileNotFoundError:
            return ""

    def _module_names(self, files: List[Path], base_folder: Path) -> Set[str]:
        names = set()
        for path in files:
            if path.name == "__init__.py":
                continue
            names.add(path.relative_to(base_folder).with_suffix("").as_posix().replace("/", "."))
        return names

    def _doc_slug_candidates(self, module_stem: str) -> Set[str]:
        clean = module_stem.replace("_frontend", "")
        dashed = clean.replace("_", "-")
        return {
            clean,
            dashed,
            f"{dashed}-cockpit",
            f"{dashed}-api",
            f"{dashed}-runtime-ui",
            f"{dashed}-runtime-snapshot-api",
        }

    def _extract_imports(self, path: Path) -> Set[str]:
        imports: Set[str] = set()
        try:
            tree = ast.parse(self._safe_read(path))
        except SyntaxError:
            return imports
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.add(alias.name)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imports.add(node.module)
        return imports

    def _extract_route_paths(self, path: Path) -> List[str]:
        text = self._safe_read(path)
        paths: List[str] = []
        prefix_match = re.search(r"APIRouter\(\s*prefix\s*=\s*['\"]([^'\"]+)['\"]", text)
        prefix = prefix_match.group(1) if prefix_match else ""
        for match in re.finditer(r"@router\.(?:get|post|put|patch|delete)\(\s*['\"]([^'\"]+)['\"]", text):
            suffix = match.group(1)
            if suffix.startswith("/"):
                paths.append(f"{prefix}{suffix}")
        return sorted(set(paths))

    def _is_allowed_workflow(self, path: Path) -> bool:
        name = path.name.lower()
        if name in WORKFLOW_ALLOWED_EXACT:
            return True
        return any(token in name for token in WORKFLOW_ALLOWED_TOKENS)

    def _scan_workflows(self) -> Dict[str, Any]:
        files = self._workflow_files()
        non_canonical = [self._rel(path) for path in files if not self._is_allowed_workflow(path)]
        canonical = [self._rel(path) for path in files if self._is_allowed_workflow(path)]
        phase_like = [self._rel(path) for path in files if re.search(r"phase\d+|cockpit-test|planner-test|queue-test|inventory-test|graph-test", path.name.lower())]
        return {
            "workflow_count": len(files),
            "canonical_workflows": canonical,
            "non_canonical_workflows": non_canonical,
            "non_canonical_count": len(non_canonical),
            "phase_like_workflows": phase_like,
            "phase_like_count": len(phase_like),
        }

    def _scan_routes_services_docs(self) -> Dict[str, Any]:
        route_folder = Path("backend/app/routes")
        service_folder = Path("backend/app/services")
        docs_folder = Path("docs/frontend")
        routes = self._py_files(route_folder)
        services = self._py_files(service_folder)
        docs = sorted(docs_folder.glob("*.md")) if docs_folder.exists() else []

        route_modules = self._module_names(routes, route_folder)
        service_modules = self._module_names(services, service_folder)
        doc_stems = {path.stem for path in docs}
        service_stems = {path.stem for path in services}
        route_stems = {path.stem for path in routes}

        route_without_router = []
        route_without_docs = []
        frontend_without_docs = []
        service_without_singleton = []
        service_not_imported_by_routes = []
        syntax_errors = []
        missing_critical_routes = []
        missing_critical_services = []
        route_paths: Dict[str, List[str]] = {}
        duplicate_route_paths: Dict[str, List[str]] = {}

        imported_service_modules: Set[str] = set()
        route_path_owners: Dict[str, List[str]] = {}
        for route in routes:
            text = self._safe_read(route)
            try:
                ast.parse(text)
            except SyntaxError as exc:
                syntax_errors.append({"path": self._rel(route), "error": str(exc)})
            if route.name != "__init__.py" and ("APIRouter" not in text or "router =" not in text):
                route_without_router.append(self._rel(route))
            if route.name != "__init__.py" and not self._doc_slug_candidates(route.stem).intersection(doc_stems):
                route_without_docs.append(self._rel(route))
            if route.stem.endswith("_frontend") and not self._doc_slug_candidates(route.stem).intersection(doc_stems):
                frontend_without_docs.append(self._rel(route))
            for imported in self._extract_imports(route):
                if imported.startswith("app.services."):
                    imported_service_modules.add(imported.replace("app.services.", "", 1))
            extracted_paths = self._extract_route_paths(route)
            route_paths[self._rel(route)] = extracted_paths
            for route_path in extracted_paths:
                route_path_owners.setdefault(route_path, []).append(self._rel(route))

        duplicate_route_paths = {route_path: owners for route_path, owners in route_path_owners.items() if len(owners) > 1}

        for critical in CRITICAL_ROUTE_NAMES:
            if critical not in route_stems:
                missing_critical_routes.append(f"backend/app/routes/{critical}.py")
            if f"{critical}_frontend" not in route_stems:
                missing_critical_routes.append(f"backend/app/routes/{critical}_frontend.py")
            if f"{critical}_service" not in service_stems:
                missing_critical_services.append(f"backend/app/services/{critical}_service.py")

        for service in services:
            text = self._safe_read(service)
            try:
                ast.parse(text)
            except SyntaxError as exc:
                syntax_errors.append({"path": self._rel(service), "error": str(exc)})
            expected_singleton = f"{service.stem} = "
            if service.name != "__init__.py" and service.stem.endswith("_service") and expected_singleton not in text:
                service_without_singleton.append(self._rel(service))
            module_name = service.relative_to(service_folder).with_suffix("").as_posix().replace("/", ".")
            if module_name not in imported_service_modules and service.stem not in {"__init__"}:
                service_not_imported_by_routes.append(self._rel(service))

        return {
            "route_count": len([path for path in routes if path.name != "__init__.py"]),
            "service_count": len([path for path in services if path.name != "__init__.py"]),
            "doc_count": len(docs),
            "route_modules": sorted(route_modules),
            "service_modules": sorted(service_modules),
            "route_paths": route_paths,
            "duplicate_route_paths": duplicate_route_paths,
            "duplicate_route_path_count": len(duplicate_route_paths),
            "route_without_router": route_without_router,
            "route_without_docs": route_without_docs,
            "frontend_without_docs": frontend_without_docs,
            "service_without_singleton": service_without_singleton,
            "service_not_imported_by_routes": service_not_imported_by_routes,
            "missing_critical_routes": missing_critical_routes,
            "missing_critical_services": missing_critical_services,
            "syntax_errors": syntax_errors,
        }

    def _scan_storage_patterns(self) -> Dict[str, Any]:
        services = self._py_files(Path("backend/app/services"))
        direct_json_writers = []
        data_store_files = []
        missing_atomic_write = []
        for service in services:
            text = self._safe_read(service)
            if "write_text" in text and "json" in text:
                direct_json_writers.append(self._rel(service))
                if "AtomicJsonStore" not in text and ".tmp" not in text and "replace(" not in text:
                    missing_atomic_write.append(self._rel(service))
            if "DATA_DIR" in text or "data/" in text:
                data_store_files.append(self._rel(service))
        return {
            "direct_json_writer_count": len(direct_json_writers),
            "direct_json_writers": direct_json_writers,
            "missing_atomic_write_count": len(missing_atomic_write),
            "missing_atomic_write": missing_atomic_write,
            "data_store_service_count": len(data_store_files),
            "data_store_services": data_store_files,
            "recommendation": "Criar camada comum de atomic JSON store com lock/backup antes de execução real concorrente.",
        }

    def _scan_expected_files(self) -> Dict[str, Any]:
        expected = [
            "backend/main.py",
            "backend/app/utils/__init__.py",
            "backend/app/utils/atomic_json_store.py",
            "backend/app/routes/system_integrity_audit.py",
            "backend/app/routes/system_integrity_audit_frontend.py",
            "backend/app/services/system_integrity_audit_service.py",
            "backend/app/routes/operator_command_intake.py",
            "backend/app/routes/multi_ai_conversation_inventory.py",
            "backend/app/routes/repo_relationship_graph.py",
            "backend/app/routes/vault_deploy_env_planner.py",
            "backend/app/routes/mobile_approval_cockpit_v2.py",
            "backend/app/routes/approved_card_execution_queue.py",
            "docs/frontend/system-integrity-audit.md",
            ".github/workflows/universal-total-test.yml",
        ]
        missing = [path for path in expected if not Path(path).exists()]
        return {"expected_file_count": len(expected), "missing_expected_files": missing, "missing_expected_file_count": len(missing)}

    def run_audit(self) -> Dict[str, Any]:
        workflow_scan = self._scan_workflows()
        route_scan = self._scan_routes_services_docs()
        storage_scan = self._scan_storage_patterns()
        expected_scan = self._scan_expected_files()

        findings: List[Dict[str, Any]] = []
        if workflow_scan["non_canonical_count"]:
            findings.append({
                "severity": "high",
                "category": "workflow_policy",
                "title": "Workflows não-canónicos ainda existem",
                "count": workflow_scan["non_canonical_count"],
                "items": workflow_scan["non_canonical_workflows"],
            })
        if workflow_scan["phase_like_count"]:
            findings.append({
                "severity": "high",
                "category": "workflow_policy",
                "title": "Workflows antigos de fase ainda existem",
                "count": workflow_scan["phase_like_count"],
                "items": workflow_scan["phase_like_workflows"],
            })
        if route_scan["syntax_errors"]:
            findings.append({
                "severity": "critical",
                "category": "syntax",
                "title": "Erros de sintaxe detetados",
                "count": len(route_scan["syntax_errors"]),
                "items": route_scan["syntax_errors"],
            })
        if expected_scan["missing_expected_file_count"]:
            findings.append({
                "severity": "critical",
                "category": "expected_files",
                "title": "Ficheiros críticos esperados estão em falta",
                "count": expected_scan["missing_expected_file_count"],
                "items": expected_scan["missing_expected_files"],
            })
        if route_scan["missing_critical_routes"] or route_scan["missing_critical_services"]:
            findings.append({
                "severity": "critical",
                "category": "critical_modules",
                "title": "Módulos críticos recentes estão em falta",
                "count": len(route_scan["missing_critical_routes"]) + len(route_scan["missing_critical_services"]),
                "items": route_scan["missing_critical_routes"] + route_scan["missing_critical_services"],
            })
        if route_scan["duplicate_route_path_count"]:
            findings.append({
                "severity": "high",
                "category": "routes",
                "title": "Rotas HTTP duplicadas detetadas",
                "count": route_scan["duplicate_route_path_count"],
                "items": route_scan["duplicate_route_paths"],
            })
        if route_scan["route_without_router"]:
            findings.append({
                "severity": "medium",
                "category": "routes",
                "title": "Route modules sem APIRouter claro",
                "count": len(route_scan["route_without_router"]),
                "items": route_scan["route_without_router"],
            })
        if route_scan["service_without_singleton"]:
            findings.append({
                "severity": "medium",
                "category": "services",
                "title": "Services sem singleton exportado no padrão *_service",
                "count": len(route_scan["service_without_singleton"]),
                "items": route_scan["service_without_singleton"],
            })
        if route_scan["frontend_without_docs"]:
            findings.append({
                "severity": "low",
                "category": "documentation",
                "title": "Frontends sem documentação correspondente",
                "count": len(route_scan["frontend_without_docs"]),
                "items": route_scan["frontend_without_docs"],
            })
        if storage_scan["direct_json_writer_count"]:
            findings.append({
                "severity": "medium",
                "category": "storage",
                "title": "Services com escrita JSON direta",
                "count": storage_scan["direct_json_writer_count"],
                "items": storage_scan["direct_json_writers"],
            })
        if storage_scan["missing_atomic_write_count"]:
            findings.append({
                "severity": "medium",
                "category": "storage",
                "title": "Writers JSON sem escrita atómica explícita",
                "count": storage_scan["missing_atomic_write_count"],
                "items": storage_scan["missing_atomic_write"],
            })

        critical_count = sum(1 for item in findings if item["severity"] == "critical")
        high_count = sum(1 for item in findings if item["severity"] == "high")
        medium_count = sum(1 for item in findings if item["severity"] == "medium")
        readiness_score = max(0, 100 - critical_count * 40 - high_count * 20 - medium_count * 8)
        report = {
            "ok": True,
            "mode": "system_integrity_audit_report",
            "created_at": self._now(),
            "status": "blocked" if critical_count or high_count else "ready_with_attention" if medium_count else "clean",
            "readiness_score": readiness_score,
            "finding_count": len(findings),
            "critical_count": critical_count,
            "high_count": high_count,
            "medium_count": medium_count,
            "findings": findings,
            "workflow_scan": workflow_scan,
            "route_service_doc_scan": route_scan,
            "storage_scan": storage_scan,
            "expected_file_scan": expected_scan,
            "next_actions": [
                "Manter apenas workflows canónicos/prune/build.",
                "Migrar todos os stores JSON críticos para AtomicJsonStore.",
                "Bloquear execução real se houver critical/high findings.",
                "Promover este relatório para o cockpit mobile antes de ações destrutivas ou deploys.",
            ],
        }
        REPORT_STORE.save(report)
        return report

    def build_dashboard(self) -> Dict[str, Any]:
        report = self.run_audit()
        return {
            "ok": True,
            "mode": "system_integrity_audit_dashboard",
            "status": report["status"],
            "readiness_score": report["readiness_score"],
            "finding_count": report["finding_count"],
            "critical_count": report["critical_count"],
            "high_count": report["high_count"],
            "medium_count": report["medium_count"],
            "workflow_count": report["workflow_scan"]["workflow_count"],
            "non_canonical_workflow_count": report["workflow_scan"]["non_canonical_count"],
            "phase_like_workflow_count": report["workflow_scan"]["phase_like_count"],
            "route_count": report["route_service_doc_scan"]["route_count"],
            "service_count": report["route_service_doc_scan"]["service_count"],
            "doc_count": report["route_service_doc_scan"]["doc_count"],
            "duplicate_route_path_count": report["route_service_doc_scan"]["duplicate_route_path_count"],
            "missing_expected_file_count": report["expected_file_scan"]["missing_expected_file_count"],
            "missing_atomic_write_count": report["storage_scan"]["missing_atomic_write_count"],
            "findings": report["findings"],
            "next_actions": report["next_actions"],
        }

    def get_package(self) -> Dict[str, Any]:
        return {"ok": True, "mode": "system_integrity_audit_package", "package": {"status": self.get_status(), "dashboard": self.build_dashboard()}}


system_integrity_audit_service = SystemIntegrityAuditService()
