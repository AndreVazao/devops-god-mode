from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from app.services.capability_reuse_service import capability_reuse_service
from app.services.conversation_bundle_service import conversation_bundle_service
from app.services.conversation_reconciliation_service import conversation_reconciliation_service
from app.services.intelligent_completion_planner_service import intelligent_completion_planner_service


class IntelligentPatchSynthesisService:
    def __init__(self, storage_root: str = "data/intelligent_patch_synthesis") -> None:
        self.storage_root = Path(storage_root)
        self.storage_root.mkdir(parents=True, exist_ok=True)

    def get_status(self) -> Dict[str, Any]:
        file_count = len([p for p in self.storage_root.rglob("*.json")]) if self.storage_root.exists() else 0
        return {
            "ok": True,
            "mode": "intelligent_patch_synthesis_status",
            "storage_root": str(self.storage_root),
            "artifact_count": file_count,
            "status": "intelligent_patch_synthesis_ready",
        }

    def _build_reuse_notes(self, desired_capabilities: List[str], target_project: str) -> List[Dict[str, Any]]:
        notes: List[Dict[str, Any]] = []
        for capability_name in desired_capabilities:
            suggestion = capability_reuse_service.suggest_reuse_plan(
                capability_name=capability_name,
                target_project=target_project,
            )
            notes.append(
                {
                    "capability_name": capability_name,
                    "reuse_candidate_count": suggestion.get("reuse_candidate_count", 0),
                    "top_candidates": suggestion.get("plan_items", [])[:3],
                }
            )
        return notes

    def synthesize_bundle_patch(
        self,
        bundle_id: str,
        target_project: str,
        desired_capabilities: List[str],
    ) -> Dict[str, Any]:
        bundle = conversation_bundle_service.get_bundle(bundle_id)
        if not bundle:
            return {
                "ok": False,
                "mode": "intelligent_patch_synthesis_result",
                "patch_status": "bundle_not_found",
                "bundle_id": bundle_id,
            }

        reconciliation = conversation_reconciliation_service.get_report(bundle_id)
        if not reconciliation.get("ok"):
            reconciliation = conversation_reconciliation_service.reconcile_bundle(bundle_id)
        if not reconciliation.get("ok"):
            return {
                "ok": False,
                "mode": "intelligent_patch_synthesis_result",
                "patch_status": "reconciliation_failed",
                "bundle_id": bundle_id,
            }

        completion_plan = intelligent_completion_planner_service.build_completion_plan(
            bundle_id=bundle_id,
            target_project=target_project,
            desired_capabilities=desired_capabilities,
        )
        if not completion_plan.get("ok"):
            return {
                "ok": False,
                "mode": "intelligent_patch_synthesis_result",
                "patch_status": "completion_plan_failed",
                "bundle_id": bundle_id,
            }

        report = reconciliation["report"]
        reuse_notes = self._build_reuse_notes(
            desired_capabilities=desired_capabilities,
            target_project=target_project,
        )
        synthesized_files: List[Dict[str, Any]] = []
        for block in report.get("deduplicated_blocks", []):
            destination_path = str(block.get("destination_path") or block.get("path_hint") or "generated/unknown.txt")
            header = (
                "# synthesized_patch_candidate\n"
                f"# bundle_id: {bundle_id}\n"
                f"# target_project: {target_project}\n"
                f"# provider: {block.get('provider') or 'unknown'}\n"
                f"# confidence_score: {block.get('confidence_score') or 0}\n"
                f"# source_status: {block.get('source_status') or 'unknown'}\n"
            )
            capability_comment = "\n".join(
                [
                    f"# capability_hint: {item['capability_name']} reuse_candidates={item['reuse_candidate_count']}"
                    for item in reuse_notes
                ]
            )
            synthesized_content = f"{header}{capability_comment}\n\n{block.get('code') or ''}\n"
            synthesized_files.append(
                {
                    "destination_path": destination_path,
                    "provider": block.get("provider") or "unknown",
                    "confidence_score": block.get("confidence_score") or 0,
                    "source_status": block.get("source_status") or "unknown",
                    "synthesized_content": synthesized_content,
                }
            )

        bundle_dir = self.storage_root / bundle_id
        bundle_dir.mkdir(parents=True, exist_ok=True)
        patch_manifest_path = bundle_dir / "intelligent-patch.manifest.json"
        patch_manifest = {
            "bundle_id": bundle_id,
            "target_project": target_project,
            "desired_capabilities": desired_capabilities,
            "completion_plan": completion_plan["plan"],
            "reuse_notes": reuse_notes,
            "files": [
                {
                    "destination_path": item["destination_path"],
                    "provider": item["provider"],
                    "confidence_score": item["confidence_score"],
                    "source_status": item["source_status"],
                }
                for item in synthesized_files
            ],
        }
        patch_manifest_path.write_text(json.dumps(patch_manifest, ensure_ascii=False, indent=2), encoding="utf-8")

        written_files: List[Dict[str, Any]] = []
        for item in synthesized_files:
            output_path = bundle_dir / item["destination_path"]
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(item["synthesized_content"], encoding="utf-8")
            written_files.append(
                {
                    "destination_path": item["destination_path"],
                    "output_file": str(output_path),
                    "provider": item["provider"],
                    "confidence_score": item["confidence_score"],
                }
            )

        return {
            "ok": True,
            "mode": "intelligent_patch_synthesis_result",
            "patch_status": "patch_synthesized",
            "bundle_id": bundle_id,
            "target_project": target_project,
            "manifest_file": str(patch_manifest_path),
            "file_count": len(written_files),
            "files": written_files,
        }

    def get_package(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "mode": "intelligent_patch_synthesis_package",
            "package": {
                "status": self.get_status(),
                "package_status": "intelligent_patch_synthesis_ready",
            },
        }


intelligent_patch_synthesis_service = IntelligentPatchSynthesisService()
