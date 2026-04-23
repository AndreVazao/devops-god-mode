from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

from app.services.deploy_execution_plan_service import deploy_execution_plan_service


class DeployTargetExecutionService:
    def __init__(self, execution_root: str = "data/deploy_target_execution") -> None:
        self.execution_root = Path(execution_root)
        self.execution_root.mkdir(parents=True, exist_ok=True)

    def get_status(self) -> Dict[str, Any]:
        manifest_count = len([p for p in self.execution_root.rglob("*.json")]) if self.execution_root.exists() else 0
        return {
            "ok": True,
            "mode": "deploy_target_execution_status",
            "execution_root": str(self.execution_root),
            "manifest_count": manifest_count,
            "status": "deploy_target_execution_ready",
        }

    def execute_plan(self, bundle_id: str, target_project: str, environment_name: str, dry_run: bool = True) -> Dict[str, Any]:
        plan = deploy_execution_plan_service.build_plan(
            bundle_id=bundle_id,
            target_project=target_project,
            environment_name=environment_name,
        )
        if not plan.get("ok"):
            return {
                "ok": False,
                "mode": "deploy_target_execution_result",
                "execution_status": "plan_failed",
                "bundle_id": bundle_id,
                "target_project": target_project,
                "environment_name": environment_name,
            }

        ready = bool(plan.get("ready"))
        executed_steps = []
        for step in plan.get("steps", []):
            step_status = "dry_run_ready" if dry_run and ready else ("executed" if ready else "blocked")
            executed_steps.append(
                {
                    "step": step.get("step"),
                    "status": step_status,
                    "details": step,
                }
            )

        manifest_path = self.execution_root / bundle_id / target_project / environment_name / "deploy-target-execution.json"
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        manifest_payload = {
            "bundle_id": bundle_id,
            "target_project": target_project,
            "environment_name": environment_name,
            "dry_run": dry_run,
            "ready": ready,
            "plan_manifest": plan.get("manifest_file"),
            "executed_steps": executed_steps,
        }
        manifest_path.write_text(json.dumps(manifest_payload, ensure_ascii=False, indent=2), encoding="utf-8")
        return {
            "ok": True,
            "mode": "deploy_target_execution_result",
            "execution_status": "dry_run_executed" if dry_run and ready else ("executed" if ready else "blocked"),
            "bundle_id": bundle_id,
            "target_project": target_project,
            "environment_name": environment_name,
            "dry_run": dry_run,
            "ready": ready,
            "step_count": len(executed_steps),
            "manifest_file": str(manifest_path),
            "executed_steps": executed_steps,
        }

    def get_package(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "mode": "deploy_target_execution_package",
            "package": {
                "status": self.get_status(),
                "package_status": "deploy_target_execution_ready",
            },
        }


deploy_target_execution_service = DeployTargetExecutionService()
