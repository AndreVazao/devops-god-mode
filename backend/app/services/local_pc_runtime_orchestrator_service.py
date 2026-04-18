from typing import Any, Dict

from app.services.desktop_mobile_handoff_service import desktop_mobile_handoff_service
from app.services.desktop_installer_onboarding_service import (
    desktop_installer_onboarding_service,
)


class LocalPcRuntimeOrchestratorService:
    def get_runtime_state(self) -> Dict[str, Any]:
        handoff = desktop_mobile_handoff_service.get_handoff_package()["handoff"]
        manifest = desktop_installer_onboarding_service.get_installer_manifest()["manifest"]
        return {
            "ok": True,
            "mode": "local_pc_runtime_state",
            "runtime": {
                "orchestrator_id": "orchestrator_pc_phone_primary",
                "runtime_mode": "pc_and_phone_primary",
                "backend_runtime": {
                    "host": "127.0.0.1",
                    "port": 8787,
                    "status": "backend_runtime_ready",
                },
                "shell_runtime": {
                    "url": "http://127.0.0.1:4173",
                    "status": "shell_runtime_ready",
                },
                "desktop_bundle": manifest["package_name"],
                "mobile_handoff": handoff["pairing_asset"],
                "startup_sequence": [
                    "prepare_local_config",
                    "start_backend_runtime",
                    "start_shell_runtime",
                    "open_desktop_launcher",
                    "handoff_mobile_pairing",
                ],
                "orchestrator_status": "runtime_orchestrator_ready",
            },
        }

    def get_startup_sequence(self) -> Dict[str, Any]:
        runtime = self.get_runtime_state()["runtime"]
        return {
            "ok": True,
            "mode": "local_pc_startup_sequence",
            "startup_sequence": runtime["startup_sequence"],
        }

    def get_mobile_handoff_state(self) -> Dict[str, Any]:
        handoff = desktop_mobile_handoff_service.get_handoff_package()["handoff"]
        pairing = desktop_mobile_handoff_service.get_pairing_summary()["pairing_summary"]
        return {
            "ok": True,
            "mode": "local_pc_mobile_handoff_state",
            "mobile_handoff_state": {
                "pairing_asset": handoff["pairing_asset"],
                "mobile_bundle_assets": handoff["mobile_bundle_assets"],
                "pairing_code": pairing["pairing_code"],
                "pairing_mode": pairing["pairing_mode"],
                "local_backend_url": pairing["local_backend_url"],
                "local_shell_url": pairing["local_shell_url"],
            },
        }


local_pc_runtime_orchestrator_service = LocalPcRuntimeOrchestratorService()
