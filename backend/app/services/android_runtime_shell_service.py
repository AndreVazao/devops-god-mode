from typing import Any, Dict

from app.services.first_run_bundle_service import first_run_bundle_service


class AndroidRuntimeShellService:
    def get_shell_bundle(self) -> Dict[str, Any]:
        bundle = first_run_bundle_service.get_bundle()["bundle"]
        pairing = first_run_bundle_service.get_pairing_asset()["pairing_asset"]
        return {
            "ok": True,
            "mode": "android_runtime_shell_bundle",
            "shell": {
                "shell_id": "android_shell_pc_phone_primary",
                "runtime_mode": "pc_and_phone_primary",
                "mobile_profile": "simple_intuitive",
                "bootstrap_asset": "godmode-mobile-bootstrap.json",
                "pairing_asset": pairing["asset_name"],
                "backend_hint": pairing["pairing_payload"]["local_backend_url"],
                "shell_status": "runtime_shell_ready",
                "recommended_sequence": bundle["recommended_sequence"],
                "desktop_payloads": bundle["desktop_payloads"],
                "mobile_payloads": bundle["mobile_payloads"],
                "pairing_payload": pairing["pairing_payload"],
            },
        }

    def get_pairing_hint(self) -> Dict[str, Any]:
        pairing = first_run_bundle_service.get_pairing_asset()["pairing_asset"]
        return {
            "ok": True,
            "mode": "android_runtime_shell_pairing_hint",
            "pairing_hint": {
                "pairing_mode": pairing["pairing_payload"]["pairing_mode"],
                "pairing_code": pairing["pairing_code"],
                "local_backend_url": pairing["pairing_payload"]["local_backend_url"],
                "local_shell_url": pairing["pairing_payload"]["local_shell_url"],
            },
        }


android_runtime_shell_service = AndroidRuntimeShellService()
