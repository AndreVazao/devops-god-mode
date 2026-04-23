from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from app.services.intelligent_patch_synthesis_service import intelligent_patch_synthesis_service


class IntelligentPatchApplyService:
    def __init__(self, apply_root: str = "data/intelligent_patch_apply") -> None:
        self.apply_root = Path(apply_root)
        self.apply_root.mkdir(parents=True, exist_ok=True)

    def get_status(self) -> Dict[str, Any]:
        manifest_count = len([p for p in self.apply_root.rglob("*.manifest.json")]) if self.apply_root.exists() else 0
        return {
            "ok": True,
            "mode": "intelligent_patch_apply_status",
            "apply_root": str(self.apply_root),
            "manifest_count": manifest_count,
            "status": "intelligent_patch_apply_ready",
        }

    def apply_synthesized_patch(
        self,
        bundle_id: str,
        target_project: str,
        desired_capabilities: List[str],
        overwrite_existing: bool = True,
    ) -> Dict[str, Any]:
        patch_result = intelligent_patch_synthesis_service.synthesize_bundle_patch(
            bundle_id=bundle_id,
            target_project=target_project,
            desired_capabilities=desired_capabilities,
        )
        if not patch_result.get("ok"):
            return {
                "ok": False,
                "mode": "intelligent_patch_apply_result",
                "apply_status": "patch_synthesis_failed",
                "bundle_id": bundle_id,
            }

        apply_dir = self.apply_root / bundle_id / target_project
        apply_dir.mkdir(parents=True, exist_ok=True)
        applied_files: List[Dict[str, Any]] = []
        skipped_files: List[str] = []
        for item in patch_result.get("files", []):
            source_path = Path(item["output_file"])
            destination_path = apply_dir / item["destination_path"]
            destination_path.parent.mkdir(parents=True, exist_ok=True)
            if destination_path.exists() and not overwrite_existing:
                skipped_files.append(item["destination_path"])
                continue
            destination_path.write_text(source_path.read_text(encoding="utf-8"), encoding="utf-8")
            applied_files.append(
                {
                    "destination_path": item["destination_path"],
                    "applied_file": str(destination_path),
                    "provider": item.get("provider") or "unknown",
                    "confidence_score": item.get("confidence_score") or 0,
                }
            )

        manifest_path = apply_dir / "intelligent-apply.manifest.json"
        manifest_payload = {
            "bundle_id": bundle_id,
            "target_project": target_project,
            "desired_capabilities": desired_capabilities,
            "patch_manifest": patch_result.get("manifest_file"),
            "applied_files": applied_files,
            "skipped_files": skipped_files,
        }
        manifest_path.write_text(json.dumps(manifest_payload, ensure_ascii=False, indent=2), encoding="utf-8")
        return {
            "ok": True,
            "mode": "intelligent_patch_apply_result",
            "apply_status": "patch_applied_to_local_workspace",
            "bundle_id": bundle_id,
            "target_project": target_project,
            "apply_dir": str(apply_dir),
            "manifest_file": str(manifest_path),
            "applied_count": len(applied_files),
            "skipped_count": len(skipped_files),
            "applied_files": applied_files,
        }

    def get_package(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "mode": "intelligent_patch_apply_package",
            "package": {
                "status": self.get_status(),
                "package_status": "intelligent_patch_apply_ready",
            },
        }


intelligent_patch_apply_service = IntelligentPatchApplyService()
