from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

from app.services.provider_secret_sync_service import provider_secret_sync_service


class GitHubActionsConnectorService:
    def __init__(self, plan_root: str = "data/github_actions_connector") -> None:
        self.plan_root = Path(plan_root)
        self.plan_root.mkdir(parents=True, exist_ok=True)

    def get_status(self) -> Dict[str, Any]:
        manifest_count = len([p for p in self.plan_root.rglob("*.json")]) if self.plan_root.exists() else 0
        return {
            "ok": True,
            "mode": "github_actions_connector_status",
            "plan_root": str(self.plan_root),
            "manifest_count": manifest_count,
            "status": "github_actions_connector_ready",
        }

    def build_connector_plan(
        self,
        repository_full_name: str,
        target_project: str,
        environment_name: str,
        workflow_file_path: str,
        branch_name: str = "main",
    ) -> Dict[str, Any]:
        secret_sync = provider_secret_sync_service.build_sync_plan(
            target_project=target_project,
            environment_name=environment_name,
            provider_name="github_actions",
        )
        ready = secret_sync.get("mapped_binding_count", 0) > 0 and workflow_file_path.endswith((".yml", ".yaml"))
        steps = [
            {
                "step": "resolve_repository",
                "status": "ready",
                "repository_full_name": repository_full_name,
                "branch_name": branch_name,
            },
            {
                "step": "resolve_workflow_file",
                "status": "ready" if workflow_file_path else "blocked",
                "workflow_file_path": workflow_file_path,
            },
            {
                "step": "map_github_actions_secrets",
                "status": "ready" if secret_sync.get("mapped_binding_count", 0) > 0 else "blocked",
                "mapped_binding_count": secret_sync.get("mapped_binding_count", 0),
            },
            {
                "step": "dispatch_workflow_when_connector_available",
                "status": "planned" if ready else "blocked",
            },
        ]
        manifest_path = self.plan_root / target_project / environment_name / "github-actions-connector-plan.json"
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        manifest_payload = {
            "repository_full_name": repository_full_name,
            "target_project": target_project,
            "environment_name": environment_name,
            "workflow_file_path": workflow_file_path,
            "branch_name": branch_name,
            "ready": ready,
            "secret_sync_manifest": secret_sync.get("manifest_file"),
            "steps": steps,
        }
        manifest_path.write_text(json.dumps(manifest_payload, ensure_ascii=False, indent=2), encoding="utf-8")
        return {
            "ok": True,
            "mode": "github_actions_connector_result",
            "plan_status": "github_actions_connector_plan_ready" if ready else "github_actions_connector_plan_partial",
            "repository_full_name": repository_full_name,
            "target_project": target_project,
            "environment_name": environment_name,
            "workflow_file_path": workflow_file_path,
            "ready": ready,
            "step_count": len(steps),
            "manifest_file": str(manifest_path),
            "steps": steps,
        }

    def get_package(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "mode": "github_actions_connector_package",
            "package": {
                "status": self.get_status(),
                "package_status": "github_actions_connector_ready",
            },
        }


github_actions_connector_service = GitHubActionsConnectorService()
