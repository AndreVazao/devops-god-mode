from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from app.services.provider_onboarding_orchestrator_service import provider_onboarding_orchestrator_service
from app.services.provider_session_partition_service import provider_session_partition_service
from app.services.tenant_partition_service import tenant_partition_service


class TenantProviderOnboardingService:
    def __init__(self, onboarding_root: str = "data/tenant_provider_onboarding") -> None:
        self.onboarding_root = Path(onboarding_root)
        self.onboarding_root.mkdir(parents=True, exist_ok=True)

    def get_status(self) -> Dict[str, Any]:
        manifest_count = len([p for p in self.onboarding_root.rglob("*.json")]) if self.onboarding_root.exists() else 0
        return {
            "ok": True,
            "mode": "tenant_provider_onboarding_status",
            "onboarding_root": str(self.onboarding_root),
            "manifest_count": manifest_count,
            "status": "tenant_provider_onboarding_ready",
        }

    def build_plan(
        self,
        tenant_id: str,
        project_name: str,
        providers: List[str],
        multirepo_mode: bool = False,
    ) -> Dict[str, Any]:
        tenant_plan = tenant_partition_service.build_partition_plan(
            tenant_id=tenant_id,
            project_name=project_name,
            multirepo_mode=multirepo_mode,
        )
        if not tenant_plan.get("ok"):
            return {
                "ok": False,
                "mode": "tenant_provider_onboarding_result",
                "plan_status": "tenant_not_found",
                "tenant_id": tenant_id,
                "project_name": project_name,
            }
        base_plan = provider_onboarding_orchestrator_service.build_first_run_plan(
            project_name=project_name,
            providers=providers,
            multirepo_mode=multirepo_mode,
        )
        session_previews: List[Dict[str, Any]] = []
        for provider in providers:
            session_previews.append(
                {
                    "tenant_id": tenant_id,
                    "provider_name": provider,
                    "account_label": f"{tenant_id}-{provider}",
                    "session_scope": "tenant_provider_onboarding",
                    "access_mode": "interactive_first_run_login",
                }
            )
        manifest_path = self.onboarding_root / tenant_id / project_name / "tenant-provider-onboarding.json"
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        manifest_payload = {
            "tenant_id": tenant_id,
            "project_name": project_name,
            "providers": providers,
            "multirepo_mode": multirepo_mode,
            "tenant_plan": tenant_plan["plan"],
            "base_plan": base_plan,
            "session_previews": session_previews,
        }
        manifest_path.write_text(json.dumps(manifest_payload, ensure_ascii=False, indent=2), encoding="utf-8")
        return {
            "ok": True,
            "mode": "tenant_provider_onboarding_result",
            "plan_status": "tenant_provider_onboarding_ready",
            "tenant_id": tenant_id,
            "project_name": project_name,
            "provider_count": len(providers),
            "multirepo_mode": multirepo_mode,
            "manifest_file": str(manifest_path),
            "tenant_plan": tenant_plan["plan"],
            "session_previews": session_previews,
        }

    def materialize_session_preview(
        self,
        tenant_id: str,
        provider_name: str,
        account_label: str,
        notes: str = "",
    ) -> Dict[str, Any]:
        return provider_session_partition_service.upsert_session(
            tenant_id=tenant_id,
            provider_name=provider_name,
            account_label=account_label,
            session_scope="tenant_provider_onboarding",
            access_mode="interactive_first_run_login",
            notes=notes,
        )

    def get_package(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "mode": "tenant_provider_onboarding_package",
            "package": {
                "status": self.get_status(),
                "package_status": "tenant_provider_onboarding_ready",
            },
        }


tenant_provider_onboarding_service = TenantProviderOnboardingService()
