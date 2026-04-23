from __future__ import annotations

from typing import Any, Dict, List


class ProviderLiveCapabilityService:
    def __init__(self) -> None:
        self.capabilities: List[Dict[str, Any]] = [
            {
                "provider_name": "github_actions",
                "real_repo_write_available": True,
                "real_secret_sync_available": False,
                "real_deploy_dispatch_available": False,
                "notes": [
                    "Repository file mutation is available through the current GitHub connector.",
                    "Direct GitHub Actions secret creation is not exposed by the current connector.",
                    "Direct workflow dispatch is not exposed by the current connector.",
                ],
            },
            {
                "provider_name": "vercel",
                "real_repo_write_available": False,
                "real_secret_sync_available": False,
                "real_deploy_dispatch_available": False,
                "notes": [
                    "No Vercel API connector is currently available in this runtime.",
                ],
            },
            {
                "provider_name": "render",
                "real_repo_write_available": False,
                "real_secret_sync_available": False,
                "real_deploy_dispatch_available": False,
                "notes": [
                    "No Render API connector is currently available in this runtime.",
                ],
            },
            {
                "provider_name": "supabase",
                "real_repo_write_available": False,
                "real_secret_sync_available": False,
                "real_deploy_dispatch_available": False,
                "notes": [
                    "No Supabase API connector is currently available in this runtime.",
                ],
            },
            {
                "provider_name": "paypal",
                "real_repo_write_available": False,
                "real_secret_sync_available": False,
                "real_deploy_dispatch_available": False,
                "notes": [
                    "No PayPal API connector is currently available in this runtime.",
                ],
            },
            {
                "provider_name": "stripe",
                "real_repo_write_available": False,
                "real_secret_sync_available": False,
                "real_deploy_dispatch_available": False,
                "notes": [
                    "No Stripe API connector is currently available in this runtime.",
                ],
            },
        ]

    def get_status(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "mode": "provider_live_capability_status",
            "provider_count": len(self.capabilities),
            "status": "provider_live_capability_ready",
        }

    def list_capabilities(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "mode": "provider_live_capability_list",
            "provider_count": len(self.capabilities),
            "capabilities": self.capabilities,
        }

    def get_provider_capability(self, provider_name: str) -> Dict[str, Any]:
        provider = provider_name.lower().strip()
        capability = next((item for item in self.capabilities if item.get("provider_name") == provider), None)
        if capability is None:
            return {
                "ok": False,
                "mode": "provider_live_capability_item",
                "provider_name": provider,
                "status": "provider_not_found",
            }
        return {
            "ok": True,
            "mode": "provider_live_capability_item",
            "provider_name": provider,
            "status": "provider_capability_found",
            "capability": capability,
        }

    def get_package(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "mode": "provider_live_capability_package",
            "package": {
                "status": self.get_status(),
                "package_status": "provider_live_capability_ready",
            },
        }


provider_live_capability_service = ProviderLiveCapabilityService()
