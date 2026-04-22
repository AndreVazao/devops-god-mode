from pathlib import Path
from typing import Any, Dict

import httpx

from app.services.desktop_mobile_handoff_service import desktop_mobile_handoff_service
from app.services.desktop_installer_onboarding_service import (
    desktop_installer_onboarding_service,
)


class LocalPcRuntimeOrchestratorService:
    def _probe_url(self, url: str, path: str = "/") -> str:
        target = (url or "").rstrip("/") + path
        if not url:
            return "runtime_target_missing"
        try:
            response = httpx.get(target, timeout=1.5)
            if response.status_code < 500:
                return "runtime_reachable"
            return "runtime_unhealthy"
        except Exception:
            return "runtime_unreachable"

    def _desktop_bundle_presence(self, manifest: Dict[str, Any]) -> Dict[str, Any]:
        expected_files = [
            manifest["primary_executable"],
            *manifest["support_scripts"],
            *manifest["onboarding_assets"],
        ]
        return {
            "package_name": manifest["package_name"],
            "expected_files": expected_files,
            "bundle_status": "bundle_manifest_ready",
        }

    def get_runtime_state(self) -> Dict[str, Any]:
        handoff = desktop_mobile_handoff_service.get_handoff_package()["handoff"]
        manifest = desktop_installer_onboarding_service.get_installer_manifest()["manifest"]
        backend_host = "127.0.0.1"
        backend_port = 8787
        shell_url = "http://127.0.0.1:4173"
        backend_probe = self._probe_url(f"http://{backend_host}:{backend_port}", "/health")
        shell_probe = self._probe_url(shell_url, "/")
        desktop_bundle = self._desktop_bundle_presence(manifest)
        pairing_asset = handoff["pairing_asset"]
        pairing_status = "pairing_asset_ready" if pairing_asset else "pairing_asset_missing"
        orchestrator_status = (
            "runtime_orchestrator_ready"
            if backend_probe == "runtime_reachable" and shell_probe == "runtime_reachable"
            else "runtime_orchestrator_waiting_local_services"
        )

        return {
            "ok": True,
            "mode": "local_pc_runtime_state",
            "runtime": {
                "orchestrator_id": "orchestrator_pc_phone_primary",
                "runtime_mode": "pc_and_phone_primary",
                "backend_runtime": {
                    "host": backend_host,
                    "port": backend_port,
                    "healthcheck_path": "/health",
                    "status": backend_probe,
                },
                "shell_runtime": {
                    "url": shell_url,
                    "status": shell_probe,
                },
                "desktop_bundle": desktop_bundle,
                "mobile_handoff": {
                    "pairing_asset": pairing_asset,
                    "status": pairing_status,
                },
                "startup_sequence": [
                    "prepare_local_config",
                    "start_backend_runtime",
                    "start_shell_runtime",
                    "open_desktop_launcher",
                    "handoff_mobile_pairing",
                ],
                "local_only": True,
                "orchestrator_status": orchestrator_status,
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
                "handoff_mode": "pc_and_phone_local_first",
            },
        }


local_pc_runtime_orchestrator_service = LocalPcRuntimeOrchestratorService()
