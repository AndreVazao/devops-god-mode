from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

from app.services.deployment_secret_binding_service import deployment_secret_binding_service
from app.services.guarded_deploy_promotion_service import guarded_deploy_promotion_service


class DeployExecutionPlanService:
    def __init__(self, plan_root: str = "data/deploy_execution_plan") -> None:
        self.plan_root = Path(plan_root)
        self.plan_root.mkdir(parents=True, exist_ok=True)

    def get_status(self) -> Dict[str, Any]:
        manifest_count = len([p for p in self.plan_root.rglob("*.json")]) if self.plan_root.exists() else 0
        return {
            "ok": True,
            "mode": "deploy_execution_plan_status",
            "plan_root": str(self.plan_root),
            "manifest_count": manifest_count,
            "status": "deploy_execution_plan_ready",
        }

    def build_plan(self, bundle_id: str, target_project: str, environment_name: str) -> Dict[str, Any]:
        promotion = guarded_deploy_promotion_service.prepare_promotion(
            bundle_id=bundle_id,
            target_project=target_project,
            environment_name=environment_name,
        )
        if not promotion.get("ok"):
            return {
                "ok": False,
                "mode": "deploy_execution_plan_result",
                "plan_status": "promotion_failed",
                "bundle_id": bundle_id,
                "target_project": target_project,
                "environment_name": environment_name,
            }

        bindings = deployment_secret_binding_service.build_deploy_secret_plan(
            target_name=target_project,
            environment_name=environment_name,
        )
        ready = bool(promotion.get("promotion_ready")) and bindings.get("binding_count", 0) > 0
        steps = []
        if ready:
            steps = [
                {"step": "validate_guarded_promotion", "status": "ready"},
                {"step": "inject_bound_secrets", "status": "ready", "secret_binding_count": bindings.get("binding_count", 0)},
                {"step": "execute_target_deploy", "status": "ready", "target_project": target_project, "environment_name": environment_name},
            ]
        else:
            steps = [
                {"step": "validate_guarded_promotion", "status": "blocked"},
                {"step": "inject_bound_secrets", "status": "blocked", "secret_binding_count": bindings.get("binding_count", 0)},
                {"step": "execute_target_deploy", "status": "blocked", "reason": "promotion_not_ready_or_missing_secret_bindings"},
            ]

        manifest_path = self.plan_root / bundle_id / target_project / environment_name / "deploy-execution-plan.json"
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        manifest_payload = {
            "bundle_id": bundle_id,
            "target_project": target_project,
            "environment_name": environment_name,
            "ready": ready,
            "promotion": promotion,
            "secret_bindings": bindings.get("bindings", []),
            "steps": steps,
        }
        manifest_path.write_text(json.dumps(manifest_payload, ensure_ascii=False, indent=2), encoding="utf-8")
        return {
            "ok": True,
            "mode": "deploy_execution_plan_result",
            "plan_status": "deploy_plan_ready" if ready else "deploy_plan_blocked",
            "bundle_id": bundle_id,
            "target_project": target_project,
            "environment_name": environment_name,
            "ready": ready,
            "step_count": len(steps),
            "secret_binding_count": bindings.get("binding_count", 0),
            "manifest_file": str(manifest_path),
            "steps": steps,
        }

    def get_package(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "mode": "deploy_execution_plan_package",
            "package": {
                "status": self.get_status(),
                "package_status": "deploy_execution_plan_ready",
            },
        }


deploy_execution_plan_service = DeployExecutionPlanService()
