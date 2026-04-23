from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from app.services.intelligent_repo_state_service import intelligent_repo_state_service


class IntelligentMergeGuardService:
    def __init__(self, guard_root: str = "data/intelligent_merge_guard") -> None:
        self.guard_root = Path(guard_root)
        self.guard_root.mkdir(parents=True, exist_ok=True)
        self.sensitive_suffixes = {".env", ".db", ".sqlite", ".sqlite3", ".pem", ".key"}
        self.review_suffixes = {".yml", ".yaml", ".json", ".md"}
        self.safe_suffixes = {".py", ".ts", ".tsx", ".js", ".jsx", ".css", ".html"}

    def get_status(self) -> Dict[str, Any]:
        manifest_count = len([p for p in self.guard_root.rglob("*.manifest.json")]) if self.guard_root.exists() else 0
        return {
            "ok": True,
            "mode": "intelligent_merge_guard_status",
            "guard_root": str(self.guard_root),
            "manifest_count": manifest_count,
            "status": "intelligent_merge_guard_ready",
        }

    def _classify_suffix(self, suffix: str) -> str:
        if suffix in self.sensitive_suffixes:
            return "blocked"
        if suffix in self.safe_suffixes:
            return "auto_merge_candidate"
        if suffix in self.review_suffixes:
            return "review_required"
        return "review_required"

    def evaluate_merge_workspace(self, bundle_id: str, target_project: str) -> Dict[str, Any]:
        inspection = intelligent_repo_state_service.inspect_merge_workspace(bundle_id=bundle_id, target_project=target_project)
        if not inspection.get("ok"):
            return {
                "ok": False,
                "mode": "intelligent_merge_guard_result",
                "guard_status": "inspection_failed",
                "bundle_id": bundle_id,
                "target_project": target_project,
            }

        manifest_path = Path(inspection["manifest_file"])
        manifest_payload = json.loads(manifest_path.read_text(encoding="utf-8"))
        decisions: List[Dict[str, Any]] = []
        counts = {"blocked": 0, "review_required": 0, "auto_merge_candidate": 0}
        for item in manifest_payload.get("files", []):
            suffix = str(item.get("suffix") or "")
            action = self._classify_suffix(suffix)
            counts[action] += 1
            decisions.append(
                {
                    "relative_path": item.get("relative_path"),
                    "suffix": suffix,
                    "size_bytes": item.get("size_bytes"),
                    "guard_action": action,
                }
            )

        output_path = self.guard_root / bundle_id / target_project / "merge-guard.manifest.json"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_payload = {
            "bundle_id": bundle_id,
            "target_project": target_project,
            "inspection_manifest": inspection["manifest_file"],
            "counts": counts,
            "decisions": decisions,
        }
        output_path.write_text(json.dumps(output_payload, ensure_ascii=False, indent=2), encoding="utf-8")
        return {
            "ok": True,
            "mode": "intelligent_merge_guard_result",
            "guard_status": "merge_guard_evaluated",
            "bundle_id": bundle_id,
            "target_project": target_project,
            "manifest_file": str(output_path),
            "counts": counts,
            "decisions": decisions,
        }

    def get_package(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "mode": "intelligent_merge_guard_package",
            "package": {
                "status": self.get_status(),
                "package_status": "intelligent_merge_guard_ready",
            },
        }


intelligent_merge_guard_service = IntelligentMergeGuardService()
