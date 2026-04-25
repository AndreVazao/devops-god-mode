from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List

from app.utils.atomic_json_store import AtomicJsonStore

DATA_DIR = Path("data")
AUTORFRESH_FILE = DATA_DIR / "project_tree_autorefresh.json"
AUTORFRESH_STORE = AtomicJsonStore(
    AUTORFRESH_FILE,
    default_factory=lambda: {"snapshots": [], "reports": []},
)

ROOT = Path(".")
PROJECT_TREE_PATH = ROOT / "PROJECT_TREE.txt"
EXCLUDE_DIRS = {
    ".git",
    ".github/.cache",
    ".pytest_cache",
    "__pycache__",
    ".mypy_cache",
    ".ruff_cache",
    "node_modules",
    "dist",
    "build",
    ".venv",
    "venv",
    "data",
}
EXCLUDE_SUFFIXES = {".pyc", ".pyo", ".log", ".tmp", ".lock"}
MAX_FILES = 4000


class ProjectTreeAutorefreshService:
    """Generates and validates PROJECT_TREE.txt so phase work does not drift."""

    def get_status(self) -> Dict[str, Any]:
        store = self._load_store()
        return {
            "ok": True,
            "mode": "project_tree_autorefresh_status",
            "status": "project_tree_autorefresh_ready",
            "tree_file": str(PROJECT_TREE_PATH),
            "store_file": str(AUTORFRESH_FILE),
            "snapshot_count": len(store.get("snapshots", [])),
            "report_count": len(store.get("reports", [])),
        }

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def _normalize_store(self, store: Dict[str, Any]) -> Dict[str, Any]:
        if not isinstance(store, dict):
            return {"snapshots": [], "reports": []}
        store.setdefault("snapshots", [])
        store.setdefault("reports", [])
        return store

    def _load_store(self) -> Dict[str, Any]:
        return self._normalize_store(AUTORFRESH_STORE.load())

    def _ignored(self, path: Path) -> bool:
        parts = path.as_posix().split("/")
        if any(part in EXCLUDE_DIRS for part in parts):
            return True
        text = path.as_posix()
        if any(text == item or text.startswith(f"{item}/") for item in EXCLUDE_DIRS):
            return True
        return path.suffix in EXCLUDE_SUFFIXES

    def _iter_entries(self) -> Iterable[Path]:
        count = 0
        for path in sorted(ROOT.rglob("*"), key=lambda item: item.as_posix().lower()):
            rel = path.relative_to(ROOT)
            if self._ignored(rel):
                continue
            if rel.as_posix() == ".gitignore":
                yield rel
                continue
            if path.is_file() or path.is_dir():
                yield rel
                count += 1
                if count >= MAX_FILES:
                    break

    def build_flat_index(self) -> List[str]:
        return [entry.as_posix() + ("/" if (ROOT / entry).is_dir() else "") for entry in self._iter_entries()]

    def build_tree_text(self) -> str:
        lines = ["devops-god-mode/"]
        entries = self.build_flat_index()
        tree: Dict[str, Any] = {}
        for entry in entries:
            clean = entry.rstrip("/")
            parts = clean.split("/")
            cursor = tree
            for part in parts:
                cursor = cursor.setdefault(part, {})

        def emit(node: Dict[str, Any], prefix: str = "") -> None:
            names = sorted(node.keys(), key=lambda item: (not node[item], item.lower()))
            for idx, name in enumerate(names):
                is_last = idx == len(names) - 1
                connector = "└─ " if is_last else "├─ "
                child_prefix = "   " if is_last else "│  "
                lines.append(f"{prefix}{connector}{name}")
                if node[name]:
                    emit(node[name], prefix + child_prefix)

        emit(tree)
        return "\n".join(lines) + "\n"

    def read_current_tree(self) -> Dict[str, Any]:
        if not PROJECT_TREE_PATH.exists():
            return {"ok": False, "error": "project_tree_missing", "path": str(PROJECT_TREE_PATH)}
        return {"ok": True, "mode": "project_tree_autorefresh_read", "content": PROJECT_TREE_PATH.read_text(encoding="utf-8"), "path": str(PROJECT_TREE_PATH)}

    def compare_tree(self) -> Dict[str, Any]:
        generated = self.build_tree_text()
        current = PROJECT_TREE_PATH.read_text(encoding="utf-8") if PROJECT_TREE_PATH.exists() else ""
        generated_lines = set(generated.splitlines())
        current_lines = set(current.splitlines())
        missing_lines = sorted(generated_lines - current_lines)[:200]
        obsolete_lines = sorted(current_lines - generated_lines)[:200]
        report = {
            "created_at": self._now(),
            "in_sync": generated == current,
            "generated_line_count": len(generated.splitlines()),
            "current_line_count": len(current.splitlines()),
            "missing_line_count": len(generated_lines - current_lines),
            "obsolete_line_count": len(current_lines - generated_lines),
            "missing_lines_preview": missing_lines,
            "obsolete_lines_preview": obsolete_lines,
        }

        def mutate(store: Dict[str, Any]) -> Dict[str, Any]:
            store = self._normalize_store(store)
            store["reports"].append(report)
            store["reports"] = store["reports"][-100:]
            return store

        AUTORFRESH_STORE.update(mutate)
        return {"ok": True, "mode": "project_tree_autorefresh_compare", "report": report}

    def write_generated_tree(self, allow_overwrite: bool = False) -> Dict[str, Any]:
        generated = self.build_tree_text()
        if PROJECT_TREE_PATH.exists() and not allow_overwrite:
            return {"ok": False, "error": "overwrite_requires_explicit_allow", "path": str(PROJECT_TREE_PATH)}
        PROJECT_TREE_PATH.write_text(generated, encoding="utf-8")
        snapshot = {"created_at": self._now(), "path": str(PROJECT_TREE_PATH), "line_count": len(generated.splitlines())}

        def mutate(store: Dict[str, Any]) -> Dict[str, Any]:
            store = self._normalize_store(store)
            store["snapshots"].append(snapshot)
            store["snapshots"] = store["snapshots"][-100:]
            return store

        AUTORFRESH_STORE.update(mutate)
        return {"ok": True, "mode": "project_tree_autorefresh_write", "snapshot": snapshot}

    def build_dashboard(self) -> Dict[str, Any]:
        comparison = self.compare_tree()
        return {
            "ok": True,
            "mode": "project_tree_autorefresh_dashboard",
            "status": "in_sync" if comparison["report"]["in_sync"] else "needs_refresh",
            "comparison": comparison["report"],
            "quick_rules": [
                "Criar branch a partir do main mais recente.",
                "Apagar workflow temporário da fase anterior antes de criar o novo.",
                "Ao adicionar/remover ficheiros, regenerar PROJECT_TREE.txt na mesma PR.",
                "Não substituir PROJECT_TREE.txt sem validação explícita.",
            ],
        }

    def get_package(self) -> Dict[str, Any]:
        return {"ok": True, "mode": "project_tree_autorefresh_package", "package": {"status": self.get_status(), "dashboard": self.build_dashboard()}}


project_tree_autorefresh_service = ProjectTreeAutorefreshService()
