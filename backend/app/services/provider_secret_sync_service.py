from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from app.services.deployment_secret_binding_service import deployment_secret_binding_service


class ProviderSecretSyncService:
    def __init__(self, sync_root: str = "data/provider_secret_sync") -> None:
        self.sync_root = Path(sync_root)
        self.sync_root.mkdir(parents=True, exist_ok=True)

    def get_status(self) -> Dict[str, Any]:
        manifest_count = len([p for p in self.sync_root.rglob("*.json")]) if self.sync_root.exists() else 0
        return {
            "ok": True,
            "mode": "provider_secret_sync_status",
            "sync_root": str(self.sync_root),
            "manifest_count": manifest_count,
            "status": "provider_secret_sync_ready",
        }

    def _map_binding(self, provider_name: str, binding: Dict[str, Any]) -> Dict[str, Any]:
        provider = provider_name.lower().strip()
        inject_as = binding.get("inject_as") or binding.get("secret_name")
        if provider == "github_actions":
            return {
                "provider": provider,
                "sync_action": "map_github_actions_secret",
                "secret_name": binding.get("secret_name"),
                "destination_name": inject_as,
                "environment_name": binding.get("environment_name"),
            }
        if provider == "vercel":
            return {
                "provider": provider,
                "sync_action": "map_vercel_environment_variable",
                "secret_name": binding.get("secret_name"),
                "destination_name": inject_as,
                "environment_name": binding.get("environment_name"),
            }
        return {
            "provider": provider or "generic",
            "sync_action": "map_generic_provider_secret",
            "secret_name": binding.get("secret_name"),
            "destination_name": inject_as,
            "environment_name": binding.get("environment_name"),
        }

    def build_sync_plan(self, target_project: str, environment_name: str, provider_name: str) -> Dict[str, Any]:
        binding_plan = deployment_secret_binding_service.build_deploy_secret_plan(
            target_name=target_project,
            environment_name=environment_name,
        )
        bindings = binding_plan.get("bindings", [])
        mapped_bindings: List[Dict[str, Any]] = [self._map_binding(provider_name=provider_name, binding=b) for b in bindings]
        manifest_path = self.sync_root / target_project / environment_name / f"{provider_name}-secret-sync.json"
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        manifest_payload = {
            "target_project": target_project,
            "environment_name": environment_name,
            "provider_name": provider_name,
            "binding_count": len(bindings),
            "mapped_bindings": mapped_bindings,
        }
        manifest_path.write_text(json.dumps(manifest_payload, ensure_ascii=False, indent=2), encoding="utf-8")
        return {
            "ok": True,
            "mode": "provider_secret_sync_result",
            "sync_status": "provider_secret_sync_plan_ready",
            "target_project": target_project,
            "environment_name": environment_name,
            "provider_name": provider_name,
            "binding_count": len(bindings),
            "mapped_binding_count": len(mapped_bindings),
            "manifest_file": str(manifest_path),
            "mapped_bindings": mapped_bindings,
        }

    def get_package(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "mode": "provider_secret_sync_package",
            "package": {
                "status": self.get_status(),
                "package_status": "provider_secret_sync_ready",
            },
        }


provider_secret_sync_service = ProviderSecretSyncService()
