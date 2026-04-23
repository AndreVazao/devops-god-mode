from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from app.services.provider_live_capability_service import provider_live_capability_service


class ProviderOnboardingOrchestratorService:
    def __init__(self, onboarding_root: str = "data/provider_onboarding_orchestrator") -> None:
        self.onboarding_root = Path(onboarding_root)
        self.onboarding_root.mkdir(parents=True, exist_ok=True)

    def get_status(self) -> Dict[str, Any]:
        manifest_count = len([p for p in self.onboarding_root.rglob("*.json")]) if self.onboarding_root.exists() else 0
        return {
            "ok": True,
            "mode": "provider_onboarding_orchestrator_status",
            "onboarding_root": str(self.onboarding_root),
            "manifest_count": manifest_count,
            "status": "provider_onboarding_orchestrator_ready",
        }

    def build_first_run_plan(self, project_name: str, providers: List[str], multirepo_mode: bool = False) -> Dict[str, Any]:
        capabilities = provider_live_capability_service.list_capabilities().get("capabilities", [])
        capability_map = {item.get("provider_name"): item for item in capabilities}
        steps: List[Dict[str, Any]] = []
        for provider in providers:
            provider_key = provider.lower().strip()
            capability = capability_map.get(provider_key, {})
            steps.append(
                {
                    "provider_name": provider_key,
                    "step": "open_provider_login_session_on_first_run",
                    "status": "planned",
                    "requires_user_login": True,
                    "capture_session_after_login": True,
                    "capture_env_and_secret_metadata": True,
                    "real_secret_sync_available": capability.get("real_secret_sync_available", False),
                    "real_deploy_dispatch_available": capability.get("real_deploy_dispatch_available", False),
                }
            )
        repo_plan = {
            "multirepo_mode": multirepo_mode,
            "frontend_repo": f"{project_name}-frontend" if multirepo_mode else project_name,
            "backend_repo": f"{project_name}-backend" if multirepo_mode else project_name,
            "shared_secret_topology_enabled": True,
        }
        manifest_path = self.onboarding_root / project_name / "first-run-provider-onboarding.json"
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        manifest_payload = {
            "project_name": project_name,
            "providers": providers,
            "steps": steps,
            "repo_plan": repo_plan,
        }
        manifest_path.write_text(json.dumps(manifest_payload, ensure_ascii=False, indent=2), encoding="utf-8")
        return {
            "ok": True,
            "mode": "provider_onboarding_orchestrator_result",
            "plan_status": "first_run_provider_onboarding_ready",
            "project_name": project_name,
            "provider_count": len(providers),
            "multirepo_mode": multirepo_mode,
            "manifest_file": str(manifest_path),
            "steps": steps,
            "repo_plan": repo_plan,
        }

    def get_package(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "mode": "provider_onboarding_orchestrator_package",
            "package": {
                "status": self.get_status(),
                "package_status": "provider_onboarding_orchestrator_ready",
            },
        }


provider_onboarding_orchestrator_service = ProviderOnboardingOrchestratorService()
