from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from app.services.intelligent_repo_merge_service import intelligent_repo_merge_service


class IntelligentRepoStateService:
    def __init__(self, inspection_root: str = "data/intelligent_repo_state") -> None:
        self.inspection_root = Path(inspection_root)
        self.inspection_root.mkdir(parents=True, exist_ok=True)

    def get_status(self) -> Dict[str, Any]:
        manifest_count = len([p for p in self.inspection_root.rglob("*.manifest.json")]) if self.inspection_root.exists() else 0
        return {
            "ok": True,
            "mode": "intelligent_repo_state_status",
            "inspection_root": str(self.inspection_root),
            "manifest_count": manifest_count,
            "status": "intelligent_repo_state_ready",
        }

    def inspect_merge_workspace(self, bundle_id: str, target_project: str) -> Dict[str, Any]:
        merge_dir = Path("data/intelligent_repo_merge") / bundle_id / target_project
        if not merge_dir.exists():
            return {
                "ok": False,
                "mode": "intelligent_repo_state_result",
                "inspection_status": "merge_workspace_not_found",
                "bundle_id": bundle_id,
                "target_project": target_project,
            }

        files: List[Dict[str, Any]] = []
        total_bytes = 0
        for path in sorted(merge_dir.rglob("*")):
            if not path.is_file() or path.name.endswith(".manifest.json"):
                continue
            size = path.stat().st_size
            total_bytes += size
            files.append(
                {
                    "relative_path": str(path.relative_to(merge_dir)),
                    "size_bytes": size,
                    "suffix": path.suffix.lower(),
                }
            )

        suffix_summary: Dict[str, int] = {}
        for item in files:
            suffix_summary[item["suffix"] or "<none>"] = suffix_summary.get(item["suffix"] or "<none>", 0) + 1

        manifest_path = self.inspection_root / bundle_id / target_project / "repo-state.manifest.json"
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        manifest_payload = {
            "bundle_id": bundle_id,
            "target_project": target_project,
            "merge_dir": str(merge_dir),
            "file_count": len(files),
            "total_bytes": total_bytes,
            "suffix_summary": suffix_summary,
            "files": files,
        }
        manifest_path.write_text(json.dumps(manifest_payload, ensure_ascii=False, indent=2), encoding="utf-8")
        return {
            "ok": True,
            "mode": "intelligent_repo_state_result",
            "inspection_status": "merge_workspace_inspected",
            "bundle_id": bundle_id,
            "target_project": target_project,
            "merge_dir": str(merge_dir),
            "manifest_file": str(manifest_path),
            "file_count": len(files),
            "total_bytes": total_bytes,
            "suffix_summary": suffix_summary,
        }

    def prepare_merge_with_inspection(
        self,
        bundle_id: str,
        target_project: str,
        desired_capabilities: List[str],
        overwrite_existing: bool = False,
    ) -> Dict[str, Any]:
        merge_result = intelligent_repo_merge_service.merge_applied_patch(
            bundle_id=bundle_id,
            target_project=target_project,
            desired_capabilities=desired_capabilities,
            overwrite_existing=overwrite_existing,
        )
        if not merge_result.get("ok"):
            return {
                "ok": False,
                "mode": "intelligent_repo_state_prepare_result",
                "prepare_status": "merge_failed",
                "bundle_id": bundle_id,
            }
        inspection = self.inspect_merge_workspace(bundle_id=bundle_id, target_project=target_project)
        return {
            "ok": True,
            "mode": "intelligent_repo_state_prepare_result",
            "prepare_status": "merge_and_inspection_ready",
            "merge": merge_result,
            "inspection": inspection,
        }

    def get_package(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "mode": "intelligent_repo_state_package",
            "package": {
                "status": self.get_status(),
                "package_status": "intelligent_repo_state_ready",
            },
        }


intelligent_repo_state_service = IntelligentRepoStateService()
