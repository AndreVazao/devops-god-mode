from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

from app.services.provider_live_capability_service import provider_live_capability_service
from app.services.provider_secret_sync_service import provider_secret_sync_service


class ProviderRealExecutionGuardService:
    def __init__(self, guard_root: str = "data/provider_real_execution_guard") -> None:
        self.guard_root = Path(guard_root)
        self.guard_root.mkdir(parents=True, exist_ok=True)

    def get_status(self) -> Dict[str, Any]:
        manifest_count = len([p for p in self.guard_root.rglob("*.json")]) if self.guard_root.exists() else 0
        return {
            "ok": True,
            "mode": "provider_real_execution_guard_status",
            "guard_root": str(self.guard_root),
            "manifest_count": manifest_count,
            "status": "provider_real_execution_guard_ready",
        }

    def build_guard(self, provider_name: str, target_project: str, environment_name: str) -> Dict[str, Any]:
        capability = provider_live_capability_service.get_provider_capability(provider_name)
        if not capability.get("ok"):
            return {
                "ok": False,
                "mode": "provider_real_execution_guard_result",
                "guard_status": "provider_not_found",
                "provider_name": provider_name,
                "target_project": target_project,
                "environment_name": environment_name,
            }
        sync_plan = provider_secret_sync_service.build_sync_plan(
            target_project=target_project,
            environment_name=environment_name,
            provider_name=provider_name,
        )
        item = capability["capability"]
        blockers = []
        if not item.get("real_secret_sync_available"):
            blockers.append("real_secret_sync_unavailable")
        if not item.get("real_deploy_dispatch_available"):
            blockers.append("real_deploy_dispatch_unavailable")
        if sync_plan.get("mapped_binding_count", 0) == 0:
            blockers.append("no_mapped_bindings")
        real_execution_ready = not blockers
        manifest_path = self.guard_root / target_project / environment_name / f"{provider_name}-real-execution-guard.json"
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        manifest_payload = {
            "provider_name": provider_name,
            "target_project": target_project,
            "environment_name": environment_name,
            "real_execution_ready": real_execution_ready,
            "blockers": blockers,
            "capability": item,
            "sync_manifest": sync_plan.get("manifest_file"),
        }
        manifest_path.write_text(json.dumps(manifest_payload, ensure_ascii=False, indent=2), encoding="utf-8")
        return {
            "ok": True,
            "mode": "provider_real_execution_guard_result",
            "guard_status": "real_execution_ready" if real_execution_ready else "real_execution_blocked",
            "provider_name": provider_name,
            "target_project": target_project,
            "environment_name": environment_name,
            "real_execution_ready": real_execution_ready,
            "blocker_count": len(blockers),
            "blockers": blockers,
            "manifest_file": str(manifest_path),
        }

    def get_package(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "mode": "provider_real_execution_guard_package",
            "package": {
                "status": self.get_status(),
                "package_status": "provider_real_execution_guard_ready",
            },
        }


provider_real_execution_guard_service = ProviderRealExecutionGuardService()
