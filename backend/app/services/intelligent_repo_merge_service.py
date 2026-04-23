from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from app.services.intelligent_patch_apply_service import intelligent_patch_apply_service


class IntelligentRepoMergeService:
    def __init__(self, merge_root: str = "data/intelligent_repo_merge") -> None:
        self.merge_root = Path(merge_root)
        self.merge_root.mkdir(parents=True, exist_ok=True)

    def get_status(self) -> Dict[str, Any]:
        manifest_count = len([p for p in self.merge_root.rglob("*.manifest.json")]) if self.merge_root.exists() else 0
        return {"ok": True, "mode": "intelligent_repo_merge_status", "merge_root": str(self.merge_root), "manifest_count": manifest_count, "status": "intelligent_repo_merge_ready"}

    def merge_applied_patch(self, bundle_id: str, target_project: str, desired_capabilities: List[str], overwrite_existing: bool = False) -> Dict[str, Any]:
        apply_result = intelligent_patch_apply_service.apply_synthesized_patch(bundle_id=bundle_id, target_project=target_project, desired_capabilities=desired_capabilities, overwrite_existing=True)
        if not apply_result.get("ok"):
            return {"ok": False, "mode": "intelligent_repo_merge_result", "merge_status": "apply_failed", "bundle_id": bundle_id}
        merge_dir = self.merge_root / bundle_id / target_project
        merge_dir.mkdir(parents=True, exist_ok=True)
        merged_files: List[Dict[str, Any]] = []
        skipped_files: List[str] = []
        for item in apply_result.get("applied_files", []):
            source_path = Path(item["applied_file"])
            destination_path = merge_dir / item["destination_path"]
            destination_path.parent.mkdir(parents=True, exist_ok=True)
            if destination_path.exists() and not overwrite_existing:
                skipped_files.append(item["destination_path"])
                continue
            destination_path.write_text(source_path.read_text(encoding="utf-8"), encoding="utf-8")
            merged_files.append({"destination_path": item["destination_path"], "merged_file": str(destination_path), "provider": item.get("provider") or "unknown", "confidence_score": item.get("confidence_score") or 0})
        manifest_path = merge_dir / "intelligent-repo-merge.manifest.json"
        manifest_payload = {"bundle_id": bundle_id, "target_project": target_project, "desired_capabilities": desired_capabilities, "apply_manifest": apply_result.get("manifest_file"), "merged_files": merged_files, "skipped_files": skipped_files}
        manifest_path.write_text(json.dumps(manifest_payload, ensure_ascii=False, indent=2), encoding="utf-8")
        return {"ok": True, "mode": "intelligent_repo_merge_result", "merge_status": "merged_to_controlled_repo_workspace", "bundle_id": bundle_id, "target_project": target_project, "merge_dir": str(merge_dir), "manifest_file": str(manifest_path), "merged_count": len(merged_files), "skipped_count": len(skipped_files), "merged_files": merged_files}

    def get_package(self) -> Dict[str, Any]:
        return {"ok": True, "mode": "intelligent_repo_merge_package", "package": {"status": self.get_status(), "package_status": "intelligent_repo_merge_ready"}}


intelligent_repo_merge_service = IntelligentRepoMergeService()
