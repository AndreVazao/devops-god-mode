from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

PROJECT_TREE_FILE = Path("PROJECT_TREE.txt")
IGNORED_DIRS = {".git", "__pycache__", ".pytest_cache", "node_modules", "dist", "build", ".venv", "venv"}


class ProjectTreeSyncGuardService:
    """Keeps PROJECT_TREE.txt honest after each structural change.

    PROJECT_TREE.txt is the operator-facing map used to understand the repository
    before planning repairs. This guard can generate a deterministic tree and
    compare it with the committed file so PRs do not silently drift.
    """

    def get_status(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "mode": "project_tree_sync_guard_status",
            "status": "project_tree_sync_guard_ready",
            "project_tree_file": str(PROJECT_TREE_FILE),
        }

    def _is_visible(self, path: Path) -> bool:
        return path.name not in IGNORED_DIRS and not path.name.endswith((".pyc", ".tmp", ".bak", ".lock"))

    def _sorted_children(self, path: Path) -> List[Path]:
        children = [child for child in path.iterdir() if self._is_visible(child)]
        return sorted(children, key=lambda item: (not item.is_dir(), item.name.lower()))

    def generate_tree(self, root: Path | None = None) -> str:
        base = root or Path.cwd()
        lines = [f"{base.name}/"]

        def walk(folder: Path, prefix: str = "") -> None:
            children = self._sorted_children(folder)
            for index, child in enumerate(children):
                connector = "└─ " if index == len(children) - 1 else "├─ "
                lines.append(f"{prefix}{connector}{child.name}{'/' if child.is_dir() else ''}")
                if child.is_dir():
                    extension = "   " if index == len(children) - 1 else "│  "
                    walk(child, prefix + extension)

        walk(base)
        return "\n".join(lines) + "\n"

    def read_committed_tree(self) -> str:
        if not PROJECT_TREE_FILE.exists():
            return ""
        return PROJECT_TREE_FILE.read_text(encoding="utf-8")

    def check_sync(self) -> Dict[str, Any]:
        generated = self.generate_tree()
        committed = self.read_committed_tree()
        generated_lines = generated.splitlines()
        committed_lines = committed.splitlines()
        missing_from_committed = [line for line in generated_lines if line not in committed_lines]
        stale_in_committed = [line for line in committed_lines if line not in generated_lines]
        return {
            "ok": True,
            "mode": "project_tree_sync_check",
            "in_sync": generated == committed,
            "generated_line_count": len(generated_lines),
            "committed_line_count": len(committed_lines),
            "missing_from_committed_count": len(missing_from_committed),
            "stale_in_committed_count": len(stale_in_committed),
            "missing_from_committed": missing_from_committed[:200],
            "stale_in_committed": stale_in_committed[:200],
        }

    def build_dashboard(self) -> Dict[str, Any]:
        check = self.check_sync()
        return {
            "ok": True,
            "mode": "project_tree_sync_guard_dashboard",
            "project_tree_exists": PROJECT_TREE_FILE.exists(),
            "in_sync": check["in_sync"],
            "generated_line_count": check["generated_line_count"],
            "committed_line_count": check["committed_line_count"],
            "missing_from_committed_count": check["missing_from_committed_count"],
            "stale_in_committed_count": check["stale_in_committed_count"],
            "check": check,
            "rules": [
                "Whenever a file is created, deleted or moved, PROJECT_TREE.txt must be updated in the same PR.",
                "Temporary phase workflows must be removed at the start of the next phase.",
                "The tree is a structural memory file and should stay deterministic.",
            ],
        }

    def get_package(self) -> Dict[str, Any]:
        return {"ok": True, "mode": "project_tree_sync_guard_package", "package": {"status": self.get_status(), "dashboard": self.build_dashboard()}}


project_tree_sync_guard_service = ProjectTreeSyncGuardService()
