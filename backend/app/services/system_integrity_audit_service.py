from __future__ import annotations

import ast
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Set

DATA_DIR = Path("data")
REPORT_FILE = DATA_DIR / "system_integrity_audit_report.json"

WORKFLOW_ALLOWED_EXACT = {
    "universal-total-test.yml",
    "build.yml",
    "android-apk-build.yml",
    "windows-exe-build.yml",
}
WORKFLOW_ALLOWED_TOKENS = ("prune", "apk", "android", "exe", "windows")


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

    def _is_allowed_workflow(self, path: Path) -> bool:
        name = path.name.lower()
        if name in WORKFLOW_ALLOWED_EXACT:
            return True
        return any(token in name for token in WORKFLOW_ALLOWED_TOKENS)

    def _scan_workflows(self) -> Dict[str, Any]:
        files = self._workflow_files()
        non_canonical = [self._rel(path) for path in files if not self._is_allowed_workflow(path)]
        canonical = [self._rel(path) for path in files if self._is_allowed_workflow(path)]
        return {
            "workflow_count": len(files),
            "canonical_workflows": canonical,
            "non_canonical_workflows": non_canonical,
            "non_canonical_count": len(non_canonical),
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
        doc_slugs = {path.stem.replace("-", "_") for path in docs}

        route_without_router = []
        route_without_docs = []
        frontend_without_docs = []
        service_without_singleton = []
        service_not_imported_by_routes = []
        syntax_errors = []

        imported_service_modules: Set[str] = set()
        for route in routes:
            text = self._safe_read(route)
            try:
                ast.parse(text)
            except SyntaxError as exc:
                syntax_errors.append({"path": self._rel(route), "error": str(exc)})
            if "APIRouter" not in text or "router =" not in text:
                route_without_router.append(self._rel(route))
            module_slug = route.stem.replace("_frontend", "")
            if module_slug not in doc_slugs and route.stem != "__init__":
                route_without_docs.append(self._rel(route))
            if route.stem.endswith("_frontend") and module_slug not in doc_slugs:
                frontend_without_docs.append(self._rel(route))
            for imported in self._extract_imports(route):
                if imported.startswith("app.services."):
                    imported_service_modules.add(imported.replace("app.services.", "", 1))

        for service in services:
            text = self._safe_read(service)
            try:
                ast.parse(text)
            except SyntaxError as exc:
                syntax_errors.append({"path": self._rel(service), "error": str(exc)})
            singleton_name = service.stem
            if not any(line.strip().startswith(f"{singleton_name.replace('_service', '')}") for line in text.splitlines()) and " = " not in text[-500:]:
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
            "route_without_router": route_without_router,
            "route_without_docs": route_without_docs,
            "frontend_without_docs": frontend_without_docs,
            "service_without_singleton": service_without_singleton,
            "service_not_imported_by_routes": service_not_imported_by_routes,
            "syntax_errors": syntax_errors,
        }

    def _scan_storage_patterns(self) -> Dict[str, Any]:
        services = self._py_files(Path("backend/app/services"))
        direct_json_writers = []
        data_store_files = []
        for service in services:
            text = self._safe_read(service)
            if "write_text" in text and "json" in text:
                direct_json_writers.append(self._rel(service))
            if "DATA_DIR" in text or "data/" in text:
                data_store_files.append(self._rel(service))
        return {
            "direct_json_writer_count": len(direct_json_writers),
            "direct_json_writers": direct_json_writers,
            "data_store_service_count": len(data_store_files),
            "data_store_services": data_store_files,
            "recommendation": "Criar camada comum de atomic JSON store com lock/backup antes de execução real concorrente.",
        }

    def run_audit(self) -> Dict[str, Any]:
        workflow_scan = self._scan_workflows()
        route_scan = self._scan_routes_services_docs()
        storage_scan = self._scan_storage_patterns()

        findings: List[Dict[str, Any]] = []
        if workflow_scan["non_canonical_count"]:
            findings.append({
                "severity": "high",
                "category": "workflow_policy",
                "title": "Workflows não-canónicos ainda existem",
                "count": workflow_scan["non_canonical_count"],
                "items": workflow_scan["non_canonical_workflows"],
            })
        if route_scan["syntax_errors"]:
            findings.append({
                "severity": "critical",
                "category": "syntax",
                "title": "Erros de sintaxe detetados",
                "count": len(route_scan["syntax_errors"]),
                "items": route_scan["syntax_errors"],
            })
        if route_scan["route_without_router"]:
            findings.append({
                "severity": "medium",
                "category": "routes",
                "title": "Route modules sem APIRouter claro",
                "count": len(route_scan["route_without_router"]),
                "items": route_scan["route_without_router"],
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
            "next_actions": [
                "Manter apenas workflows canónicos/prune/build.",
                "Extrair camada comum de JSON store atómico com lock e backup.",
                "Bloquear execução real se houver critical/high findings.",
                "Promover este relatório para o cockpit mobile antes de ações destrutivas ou deploys.",
            ],
        }
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        REPORT_FILE.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
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
            "route_count": report["route_service_doc_scan"]["route_count"],
            "service_count": report["route_service_doc_scan"]["service_count"],
            "doc_count": report["route_service_doc_scan"]["doc_count"],
            "findings": report["findings"],
            "next_actions": report["next_actions"],
        }

    def get_package(self) -> Dict[str, Any]:
        return {"ok": True, "mode": "system_integrity_audit_package", "package": {"status": self.get_status(), "dashboard": self.build_dashboard()}}


system_integrity_audit_service = SystemIntegrityAuditService()
