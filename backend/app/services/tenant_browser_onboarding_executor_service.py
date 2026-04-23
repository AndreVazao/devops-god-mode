from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

from app.services.provider_session_partition_service import provider_session_partition_service
from app.services.tenant_provider_onboarding_service import tenant_provider_onboarding_service


class TenantBrowserOnboardingExecutorService:
    def __init__(self, execution_root: str = "data/tenant_browser_onboarding_executor") -> None:
        self.execution_root = Path(execution_root)
        self.execution_root.mkdir(parents=True, exist_ok=True)

    def get_status(self) -> Dict[str, Any]:
        manifest_count = len([p for p in self.execution_root.rglob("*.json")]) if self.execution_root.exists() else 0
        return {
            "ok": True,
            "mode": "tenant_browser_onboarding_executor_status",
            "execution_root": str(self.execution_root),
            "manifest_count": manifest_count,
            "status": "tenant_browser_onboarding_executor_ready",
        }

    def execute_first_run_capture(
        self,
        tenant_id: str,
        project_name: str,
        provider_name: str,
        account_label: str,
        multirepo_mode: bool = False,
    ) -> Dict[str, Any]:
        onboarding = tenant_provider_onboarding_service.build_plan(
            tenant_id=tenant_id,
            project_name=project_name,
            providers=[provider_name],
            multirepo_mode=multirepo_mode,
        )
        if not onboarding.get("ok"):
            return {
                "ok": False,
                "mode": "tenant_browser_onboarding_executor_result",
                "execution_status": "tenant_onboarding_plan_failed",
                "tenant_id": tenant_id,
                "project_name": project_name,
                "provider_name": provider_name,
            }

        session_result = provider_session_partition_service.upsert_session(
            tenant_id=tenant_id,
            provider_name=provider_name,
            account_label=account_label,
            session_scope="interactive_browser_capture",
            access_mode="interactive_first_run_login",
            notes=f"first run capture planned for {project_name}",
        )
        steps = [
            {
                "step": "open_provider_login_surface",
                "status": "planned",
                "provider_name": provider_name,
                "requires_user_login": True,
            },
            {
                "step": "capture_authenticated_session",
                "status": "planned",
                "session_key": session_result["session"]["session_key"],
            },
            {
                "step": "store_session_under_tenant_partition",
                "status": "planned",
                "tenant_id": tenant_id,
            },
            {
                "step": "continue_provider_project_bootstrap",
                "status": "planned",
                "project_name": project_name,
                "multirepo_mode": multirepo_mode,
            },
        ]
        manifest_path = self.execution_root / tenant_id / project_name / f"{provider_name}-browser-onboarding-execution.json"
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        manifest_payload = {
            "tenant_id": tenant_id,
            "project_name": project_name,
            "provider_name": provider_name,
            "account_label": account_label,
            "multirepo_mode": multirepo_mode,
            "session_key": session_result["session"]["session_key"],
            "steps": steps,
        }
        manifest_path.write_text(json.dumps(manifest_payload, ensure_ascii=False, indent=2), encoding="utf-8")
        return {
            "ok": True,
            "mode": "tenant_browser_onboarding_executor_result",
            "execution_status": "tenant_browser_onboarding_capture_planned",
            "tenant_id": tenant_id,
            "project_name": project_name,
            "provider_name": provider_name,
            "account_label": account_label,
            "multirepo_mode": multirepo_mode,
            "step_count": len(steps),
            "manifest_file": str(manifest_path),
            "session_key": session_result["session"]["session_key"],
            "steps": steps,
        }

    def get_package(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "mode": "tenant_browser_onboarding_executor_package",
            "package": {
                "status": self.get_status(),
                "package_status": "tenant_browser_onboarding_executor_ready",
            },
        }


tenant_browser_onboarding_executor_service = TenantBrowserOnboardingExecutorService()
