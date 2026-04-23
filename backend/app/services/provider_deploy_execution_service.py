from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

from app.services.deploy_target_execution_service import deploy_target_execution_service


class ProviderDeployExecutionService:
    def __init__(self, execution_root: str = "data/provider_deploy_execution") -> None:
        self.execution_root = Path(execution_root)
        self.execution_root.mkdir(parents=True, exist_ok=True)

    def get_status(self) -> Dict[str, Any]:
        manifest_count = len([p for p in self.execution_root.rglob("*.json")]) if self.execution_root.exists() else 0
        return {
            "ok": True,
            "mode": "provider_deploy_execution_status",
            "execution_root": str(self.execution_root),
            "manifest_count": manifest_count,
            "status": "provider_deploy_execution_ready",
        }

    def _provider_steps(self, provider_name: str, target_project: str, environment_name: str) -> list[dict[str, Any]]:
        provider = provider_name.lower().strip()
        if provider == "github_actions":
            return [
                {"step": "resolve_repository_workflow", "provider": provider, "status": "ready", "target_project": target_project},
                {"step": "map_repository_secrets", "provider": provider, "status": "ready", "environment_name": environment_name},
                {"step": "dispatch_workflow_run", "provider": provider, "status": "ready"},
            ]
        if provider == "vercel":
            return [
                {"step": "resolve_vercel_project", "provider": provider, "status": "ready", "target_project": target_project},
                {"step": "map_vercel_environment_variables", "provider": provider, "status": "ready", "environment_name": environment_name},
                {"step": "trigger_vercel_deploy", "provider": provider, "status": "ready"},
            ]
        return [
            {"step": "resolve_provider_target", "provider": provider or "generic", "status": "ready", "target_project": target_project},
            {"step": "map_provider_secrets", "provider": provider or "generic", "status": "ready", "environment_name": environment_name},
            {"step": "trigger_provider_deploy", "provider": provider or "generic", "status": "ready"},
        ]

    def execute_provider_plan(
        self,
        bundle_id: str,
        target_project: str,
        environment_name: str,
        provider_name: str,
        dry_run: bool = True,
    ) -> Dict[str, Any]:
        target_execution = deploy_target_execution_service.execute_plan(
            bundle_id=bundle_id,
            target_project=target_project,
            environment_name=environment_name,
            dry_run=dry_run,
        )
        if not target_execution.get("ok"):
            return {
                "ok": False,
                "mode": "provider_deploy_execution_result",
                "execution_status": "target_execution_failed",
                "bundle_id": bundle_id,
                "target_project": target_project,
                "environment_name": environment_name,
                "provider_name": provider_name,
            }

        ready = bool(target_execution.get("ready"))
        provider_steps = []
        for step in self._provider_steps(provider_name=provider_name, target_project=target_project, environment_name=environment_name):
            provider_steps.append(
                {
                    **step,
                    "status": "dry_run_ready" if dry_run and ready else ("executed" if ready else "blocked"),
                }
            )

        manifest_path = self.execution_root / bundle_id / target_project / environment_name / f"{provider_name}-deploy-execution.json"
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        manifest_payload = {
            "bundle_id": bundle_id,
            "target_project": target_project,
            "environment_name": environment_name,
            "provider_name": provider_name,
            "dry_run": dry_run,
            "ready": ready,
            "target_execution_manifest": target_execution.get("manifest_file"),
            "provider_steps": provider_steps,
        }
        manifest_path.write_text(json.dumps(manifest_payload, ensure_ascii=False, indent=2), encoding="utf-8")
        return {
            "ok": True,
            "mode": "provider_deploy_execution_result",
            "execution_status": "dry_run_executed" if dry_run and ready else ("executed" if ready else "blocked"),
            "bundle_id": bundle_id,
            "target_project": target_project,
            "environment_name": environment_name,
            "provider_name": provider_name,
            "dry_run": dry_run,
            "ready": ready,
            "step_count": len(provider_steps),
            "manifest_file": str(manifest_path),
            "provider_steps": provider_steps,
        }

    def get_package(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "mode": "provider_deploy_execution_package",
            "package": {
                "status": self.get_status(),
                "package_status": "provider_deploy_execution_ready",
            },
        }


provider_deploy_execution_service = ProviderDeployExecutionService()
