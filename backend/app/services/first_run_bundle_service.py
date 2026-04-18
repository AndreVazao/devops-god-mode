from typing import Any, Dict

from app.services.desktop_bootstrap_service import Desktop_bootstrap_service
from app.services.pc_phone_bootstrap_service import pc_phone_bootstrap_service


class FirstRunBundleService:
    def get_bundle(self) -> Dict[str, Any]:
        desktop = Desktop_bootstrap_service.generate_first_run_payload()["payload"]
        pairing = pc_phone_bootstrap_service.generate_pairing_payload()
        return {
            "ok": True,
            "mode": "first_run_bundle",
            "bundle": {
                "bundle_id": "bundle_pc_phone_primary",
                "runtime_mode": "pc_and_phone_primary",
                "desktop_payloads": [
                    "desktop_first_run_payload.json",
                    "desktop_shortcut_payload.json",
                    "desktop_autostart_payload.json",
                ],
                "mobile_payloads": [
                    "godmode-mobile-bootstrap.json",
                    "godmode-mobile-pairing.json",
                ],
                "pairing_payload": pairing["qr_payload"],
                "recommended_sequence": [
                    "launch_desktop",
                    "read_first_run_payload",
                    "create_shortcut_if_enabled",
                    "enable_autostart_if_enabled",
                    "open_mobile_pairing",
                ],
                "desktop_payload": desktop,
                "final_status": "first_run_bundle_ready",
            },
        }

    def get_pairing_asset(self) -> Dict[str, Any]:
        pairing = pc_phone_bootstrap_service.generate_pairing_payload()
        return {
            "ok": True,
            "mode": "first_run_pairing_asset",
            "pairing_asset": {
                "pairing_code": pairing["pairing_code"],
                "pairing_payload": pairing["qr_payload"],
                "asset_name": "godmode-mobile-pairing.json",
            },
        }


first_run_bundle_service = FirstRunBundleService()
