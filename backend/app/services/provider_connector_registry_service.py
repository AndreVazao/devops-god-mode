from __future__ import annotations

from typing import Any, Dict, List


class ProviderConnectorRegistryService:
    def __init__(self) -> None:
        self.providers: List[Dict[str, Any]] = [
            {
                "provider_name": "github_actions",
                "execution_mode": "dry_run_orchestrated",
                "supports_secret_sync": True,
                "supports_workflow_dispatch": True,
            },
            {
                "provider_name": "vercel",
                "execution_mode": "dry_run_orchestrated",
                "supports_secret_sync": True,
                "supports_project_deploy": True,
            },
            {
                "provider_name": "generic",
                "execution_mode": "dry_run_orchestrated",
                "supports_secret_sync": True,
                "supports_project_deploy": False,
            },
        ]

    def get_status(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "mode": "provider_connector_registry_status",
            "provider_count": len(self.providers),
            "status": "provider_connector_registry_ready",
        }

    def list_providers(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "mode": "provider_connector_registry_list",
            "providers": self.providers,
            "provider_count": len(self.providers),
        }

    def get_package(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "mode": "provider_connector_registry_package",
            "package": {
                "status": self.get_status(),
                "package_status": "provider_connector_registry_ready",
            },
        }


provider_connector_registry_service = ProviderConnectorRegistryService()
