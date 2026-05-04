from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

PROJECT_ID = "GOD_MODE"
ROOT = Path(".")
ROUTES_DIR = ROOT / "backend" / "app" / "routes"
SERVICES_DIR = ROOT / "backend" / "app" / "services"
TREE_PATH = ROOT / "docs" / "project-tree" / "GOD_MODE_TREE.md"
MAX_ITEMS_PER_CATEGORY = 80

CATEGORY_RULES: list[tuple[str, tuple[str, ...]]] = [
    ("cockpit_home_mobile", ("home", "cockpit", "mobile", "apk", "operator", "approval")),
    ("github_repo_patch_build", ("github", "repo", "patch", "build", "artifact", "release", "merge")),
    ("memory_knowledge_rag", ("memory", "andreos", "obsidian", "rag", "knowledge", "context")),
    ("provider_ai_browser", ("provider", "ai", "browser", "chat", "ollama", "handoff")),
    ("local_pc_runtime", ("local", "pc", "desktop", "runtime", "install", "bootstrap")),
    ("self_update_vault_security", ("self_update", "update", "vault", "secret", "security", "guard", "rollback")),
    ("project_recovery_portfolio", ("project", "portfolio", "recovery", "intake", "classification")),
    ("orchestration_execution", ("orchestration", "pipeline", "playbook", "execution", "queue", "planner", "agent")),
    ("money_deploy_delivery", ("money", "revenue", "monetization", "deploy", "delivery", "publish")),
]


class ModuleRegistrySnapshotService:
    """Scans existing route/service modules and produces a categorized snapshot.

    Phase 178 prevents duplicate implementations by making the real module
    surface visible to the backend/cockpit before new work is started.
    """

    SERVICE_ID = "module_registry_snapshot"
    VERSION = "phase_178_v1"

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def status(self) -> Dict[str, Any]:
        snapshot = self.snapshot(include_items=False)
        return {
            "ok": True,
            "service": self.SERVICE_ID,
            "version": self.VERSION,
            "project_id": PROJECT_ID,
            "generated_at": self._now(),
            "route_module_count": snapshot["totals"]["routes"],
            "service_module_count": snapshot["totals"]["services"],
            "category_count": len(snapshot["categories"]),
            "official_tree_path": str(TREE_PATH),
            "official_tree_present": TREE_PATH.exists(),
        }

    def tree_status(self) -> Dict[str, Any]:
        if not TREE_PATH.exists():
            return {
                "ok": False,
                "project_id": PROJECT_ID,
                "tree_path": str(TREE_PATH),
                "status": "missing_until_autorefresh_runs",
                "next_action": "Run Project Tree Autorefresh workflow or push to main.",
            }
        text = TREE_PATH.read_text(encoding="utf-8")
        return {
            "ok": True,
            "project_id": PROJECT_ID,
            "tree_path": str(TREE_PATH),
            "status": "present",
            "line_count": len(text.splitlines()),
            "starts_with_project_name": "GOD_MODE/" in text,
            "preview": text.splitlines()[:40],
        }

    def snapshot(self, include_items: bool = True) -> Dict[str, Any]:
        routes = self._module_files(ROUTES_DIR, suffix=".py")
        services = self._module_files(SERVICES_DIR, suffix=".py")
        categories: Dict[str, Dict[str, Any]] = {}
        for category, _ in CATEGORY_RULES:
            categories[category] = {"routes": [], "services": [], "route_count": 0, "service_count": 0}
        categories["uncategorized"] = {"routes": [], "services": [], "route_count": 0, "service_count": 0}

        for item in routes:
            category = self._category_for(item)
            categories[category]["route_count"] += 1
            if include_items and len(categories[category]["routes"]) < MAX_ITEMS_PER_CATEGORY:
                categories[category]["routes"].append(item)

        for item in services:
            category = self._category_for(item)
            categories[category]["service_count"] += 1
            if include_items and len(categories[category]["services"]) < MAX_ITEMS_PER_CATEGORY:
                categories[category]["services"].append(item)

        return {
            "ok": True,
            "service": self.SERVICE_ID,
            "version": self.VERSION,
            "project_id": PROJECT_ID,
            "generated_at": self._now(),
            "official_tree": self.tree_status(),
            "totals": {
                "routes": len(routes),
                "services": len(services),
                "combined": len(routes) + len(services),
            },
            "categories": categories,
            "reuse_first_rules": [
                "Search this snapshot before creating a new module.",
                "Prefer extending existing route/service pairs over adding duplicates.",
                "Use GOD_MODE_TREE.md as the stable tree artifact for handoff/context.",
                "When main advances manually, confirm HEAD and refresh this snapshot.",
            ],
        }

    def category_summary(self) -> Dict[str, Any]:
        snap = self.snapshot(include_items=False)
        compact = []
        for name, data in snap["categories"].items():
            compact.append({
                "category": name,
                "routes": data["route_count"],
                "services": data["service_count"],
                "total": data["route_count"] + data["service_count"],
            })
        compact.sort(key=lambda item: item["total"], reverse=True)
        return {"ok": True, "project_id": PROJECT_ID, "categories": compact, "totals": snap["totals"]}

    def search_modules(self, query: str, limit: int = 50) -> Dict[str, Any]:
        needle = (query or "").strip().lower()
        limit = max(1, min(int(limit), 200))
        matches: List[Dict[str, Any]] = []
        if not needle:
            return {"ok": False, "error": "query_required", "matches": []}
        for kind, directory in (("route", ROUTES_DIR), ("service", SERVICES_DIR)):
            for item in self._module_files(directory, suffix=".py"):
                if needle in item.lower():
                    matches.append({"kind": kind, "module": item, "category": self._category_for(item)})
                    if len(matches) >= limit:
                        return {"ok": True, "query": query, "matches": matches, "count": len(matches)}
        return {"ok": True, "query": query, "matches": matches, "count": len(matches)}

    def package(self) -> Dict[str, Any]:
        return {
            "status": self.status(),
            "tree": self.tree_status(),
            "summary": self.category_summary(),
            "snapshot": self.snapshot(include_items=True),
        }

    def _module_files(self, directory: Path, suffix: str) -> List[str]:
        if not directory.exists():
            return []
        result = []
        for path in sorted(directory.glob(f"*{suffix}"), key=lambda item: item.name.lower()):
            if path.name == "__init__.py" or path.name.startswith("_"):
                continue
            result.append(path.stem)
        return result

    def _category_for(self, module_name: str) -> str:
        lower = module_name.lower()
        for category, tokens in CATEGORY_RULES:
            if any(token in lower for token in tokens):
                return category
        return "uncategorized"


module_registry_snapshot_service = ModuleRegistrySnapshotService()
