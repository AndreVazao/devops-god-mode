from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from app.services.deployment_secret_binding_service import deployment_secret_binding_service
from app.services.intelligent_merge_guard_service import intelligent_merge_guard_service


class GuardedDeployPromotionService:
    def __init__(self, promotion_root: str = "data/guarded_deploy_promotion") -> None:
        self.promotion_root = Path(promotion_root)
        self.promotion_root.mkdir(parents=True, exist_ok=True)

    def get_status(self) -> Dict[str, Any]:
        manifest_count = len([p for p in self.promotion_root.rglob("*.json")]) if self.promotion_root.exists() else 0
        return {
            "ok": True,
            "mode": "guarded_deploy_promotion_status",
            "promotion_root": str(self.promotion_root),
            "manifest_count": manifest_count,
            "status": "guarded_deploy_promotion_ready",
        }

    def prepare_promotion(
        self,
        bundle_id: str,
        target_project: str,
        environment_name: str,
    ) -> Dict[str, Any]:
        guard = intelligent_merge_guard_service.evaluate_merge_workspace(
            bundle_id=bundle_id,
            target_project=target_project,
        )
        if not guard.get("ok"):
            return {
                "ok": False,
                "mode": "guarded_deploy_promotion_result",
                "promotion_status": "merge_guard_failed",
                "bundle_id": bundle_id,
                "target_project": target_project,
                "environment_name": environment_name,
            }

        binding_plan = deployment_secret_binding_service.build_deploy_secret_plan(
            target_name=target_project,
            environment_name=environment_name,
        )
        auto_files = [item for item in guard.get("decisions", []) if item.get("guard_action") == "auto_merge_candidate"]
        review_files = [item for item in guard.get("decisions", []) if item.get("guard_action") == "review_required"]
        blocked_files = [item for item in guard.get("decisions", []) if item.get("guard_action") == "blocked"]
        promotion_ready = bool(auto_files) and not blocked_files and binding_plan.get("binding_count", 0) > 0

        manifest_path = self.promotion_root / bundle_id / target_project / environment_name / "guarded-promotion.manifest.json"
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        manifest_payload = {
            "bundle_id": bundle_id,
            "target_project": target_project,
            "environment_name": environment_name,
            "promotion_ready": promotion_ready,
            "auto_merge_candidates": auto_files,
            "review_required": review_files,
            "blocked": blocked_files,
            "secret_bindings": binding_plan.get("bindings", []),
        }
        manifest_path.write_text(json.dumps(manifest_payload, ensure_ascii=False, indent=2), encoding="utf-8")
        return {
            "ok": True,
            "mode": "guarded_deploy_promotion_result",
            "promotion_status": "promotion_ready" if promotion_ready else "promotion_blocked_or_review_required",
            "bundle_id": bundle_id,
            "target_project": target_project,
            "environment_name": environment_name,
            "promotion_ready": promotion_ready,
            "manifest_file": str(manifest_path),
            "auto_merge_count": len(auto_files),
            "review_required_count": len(review_files),
            "blocked_count": len(blocked_files),
            "secret_binding_count": binding_plan.get("binding_count", 0),
        }

    def get_package(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "mode": "guarded_deploy_promotion_package",
            "package": {
                "status": self.get_status(),
                "package_status": "guarded_deploy_promotion_ready",
            },
        }


guarded_deploy_promotion_service = GuardedDeployPromotionService()
