from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

from app.services.provider_secret_sync_service import provider_secret_sync_service


class ExternalProviderBridgeService:
    def __init__(self, bridge_root: str = "data/external_provider_bridge") -> None:
        self.bridge_root = Path(bridge_root)
        self.bridge_root.mkdir(parents=True, exist_ok=True)

    def get_status(self) -> Dict[str, Any]:
        manifest_count = len([p for p in self.bridge_root.rglob("*.json")]) if self.bridge_root.exists() else 0
        return {
            "ok": True,
            "mode": "external_provider_bridge_status",
            "bridge_root": str(self.bridge_root),
            "manifest_count": manifest_count,
            "status": "external_provider_bridge_ready",
        }

    def build_bridge_plan(self, provider_name: str, target_project: str, environment_name: str) -> Dict[str, Any]:
        provider = provider_name.lower().strip()
        secret_sync = provider_secret_sync_service.build_sync_plan(
            target_project=target_project,
            environment_name=environment_name,
            provider_name=provider,
        )
        if provider == "vercel":
            execution_mode = "provider_api_required"
            steps = [
                {"step": "resolve_vercel_project", "status": "planned"},
                {"step": "sync_vercel_environment_variables", "status": "planned", "mapped_binding_count": secret_sync.get("mapped_binding_count", 0)},
                {"step": "trigger_vercel_deploy", "status": "planned"},
            ]
        elif provider == "render":
            execution_mode = "provider_api_required"
            steps = [
                {"step": "resolve_render_service", "status": "planned"},
                {"step": "sync_render_environment_variables", "status": "planned", "mapped_binding_count": secret_sync.get("mapped_binding_count", 0)},
                {"step": "trigger_render_deploy", "status": "planned"},
            ]
        elif provider == "supabase":
            execution_mode = "provider_api_required"
            steps = [
                {"step": "resolve_supabase_project", "status": "planned"},
                {"step": "sync_supabase_secrets", "status": "planned", "mapped_binding_count": secret_sync.get("mapped_binding_count", 0)},
                {"step": "apply_supabase_runtime_update", "status": "planned"},
            ]
        else:
            execution_mode = "generic_provider_bridge"
            steps = [
                {"step": "resolve_provider_target", "status": "planned"},
                {"step": "sync_provider_secrets", "status": "planned", "mapped_binding_count": secret_sync.get("mapped_binding_count", 0)},
                {"step": "trigger_provider_deploy", "status": "planned"},
            ]
        manifest_path = self.bridge_root / target_project / environment_name / f"{provider}-bridge-plan.json"
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        manifest_payload = {
            "provider_name": provider,
            "target_project": target_project,
            "environment_name": environment_name,
            "execution_mode": execution_mode,
            "secret_sync_manifest": secret_sync.get("manifest_file"),
            "steps": steps,
        }
        manifest_path.write_text(json.dumps(manifest_payload, ensure_ascii=False, indent=2), encoding="utf-8")
        return {
            "ok": True,
            "mode": "external_provider_bridge_result",
            "bridge_status": "external_provider_bridge_plan_ready",
            "provider_name": provider,
            "target_project": target_project,
            "environment_name": environment_name,
            "execution_mode": execution_mode,
            "step_count": len(steps),
            "manifest_file": str(manifest_path),
            "steps": steps,
        }

    def get_package(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "mode": "external_provider_bridge_package",
            "package": {
                "status": self.get_status(),
                "package_status": "external_provider_bridge_ready",
            },
        }


external_provider_bridge_service = ExternalProviderBridgeService()
