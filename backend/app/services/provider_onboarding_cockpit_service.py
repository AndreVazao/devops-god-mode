from __future__ import annotations

from typing import Any, Dict, List

from app.services.provider_connector_registry_service import provider_connector_registry_service
from app.services.provider_live_capability_service import provider_live_capability_service
from app.services.provider_onboarding_orchestrator_service import provider_onboarding_orchestrator_service
from app.services.tenant_partition_service import tenant_partition_service


class ProviderOnboardingCockpitService:
    def get_status(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "mode": "provider_onboarding_cockpit_status",
            "status": "provider_onboarding_cockpit_ready",
        }

    def build_dashboard(
        self,
        tenant_id: str = "owner-andre",
        project_name: str = "godmode-project",
        providers: List[str] | None = None,
        multirepo_mode: bool = True,
    ) -> Dict[str, Any]:
        requested_providers = [item.lower().strip() for item in (providers or ["github", "vercel", "supabase", "render"])]
        registry = provider_connector_registry_service.list_providers()
        capabilities = provider_live_capability_service.list_capabilities()
        capability_map = {item.get("provider_name"): item for item in capabilities.get("capabilities", [])}
        tenant_records = tenant_partition_service.list_tenants().get("tenants", [])
        first_run_plan = provider_onboarding_orchestrator_service.build_first_run_plan(
            project_name=project_name,
            providers=requested_providers,
            multirepo_mode=multirepo_mode,
        )

        provider_cards: List[Dict[str, Any]] = []
        blockers: List[str] = []
        for provider_name in requested_providers:
            capability = capability_map.get(provider_name, {})
            sync_ready = capability.get("real_secret_sync_available", False)
            deploy_ready = capability.get("real_deploy_dispatch_available", False)
            severity = "ok" if (sync_ready or deploy_ready) else "warning"
            if not capability:
                severity = "danger"
                blockers.append(f"Provider {provider_name} ainda não aparece mapeado nas capacidades live.")
            provider_cards.append(
                {
                    "provider_name": provider_name,
                    "severity": severity,
                    "real_secret_sync_available": sync_ready,
                    "real_deploy_dispatch_available": deploy_ready,
                    "requires_user_login": True,
                    "next_step": "abrir login e capturar sessão na primeira execução",
                }
            )

        if len(tenant_records) == 0:
            blockers.append("Ainda não existem tenants registados para separar owner, clientes e familiares.")

        repo_plan = first_run_plan.get("repo_plan", {})

        return {
            "ok": True,
            "mode": "provider_onboarding_cockpit_dashboard",
            "dashboard_status": "provider_onboarding_cockpit_dashboard_ready",
            "tenant_id": tenant_id,
            "project_name": project_name,
            "provider_count": len(requested_providers),
            "providers": provider_cards,
            "blocker_count": len(blockers),
            "blockers": blockers,
            "tenant_count": len(tenant_records),
            "registry_provider_count": registry.get("provider_count", 0),
            "capability_provider_count": capabilities.get("capability_count", len(capabilities.get("capabilities", []))),
            "multirepo_mode": multirepo_mode,
            "repo_plan": repo_plan,
            "first_run_steps": first_run_plan.get("steps", []),
            "manifest_file": first_run_plan.get("manifest_file"),
        }

    def get_package(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "mode": "provider_onboarding_cockpit_package",
            "package": {
                "status": self.get_status(),
                "package_status": "provider_onboarding_cockpit_ready",
            },
        }


provider_onboarding_cockpit_service = ProviderOnboardingCockpitService()
