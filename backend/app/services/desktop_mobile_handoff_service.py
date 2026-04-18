from typing import Any, Dict

from app.services.desktop_installer_onboarding_service import (
    desktop_installer_onboarding_service,
)
from app.services.first_run_bundle_service import first_run_bundle_service
from app.services.android_runtime_shell_service import android_runtime_shell_service


class DesktopMobileHandoffService:
    def get_handoff_package(self) -> Dict[str, Any]:
        manifest = desktop_installer_onboarding_service.get_installer_manifest()["manifest"]
        onboarding = desktop_installer_onboarding_service.get_onboarding_bundle()["onboarding"]
        first_run = first_run_bundle_service.get_bundle()["bundle"]
        mobile_shell = android_runtime_shell_service.get_shell_bundle()["shell"]
        return {
            "ok": True,
            "mode": "desktop_mobile_handoff_package",
            "handoff": {
                "handoff_id": "handoff_pc_phone_primary",
                "runtime_mode": "pc_and_phone_primary",
                "desktop_bundle_assets": [
                    manifest["primary_executable"],
                    "desktop-installer-manifest.json",
                    "desktop-onboarding.json",
                    "desktop-bundle-index.json",
                ],
                "mobile_bundle_assets": [
                    "GodModeMobile.apk",
                    *first_run["mobile_payloads"],
                    mobile_shell["pairing_asset"],
                ],
                "pairing_asset": mobile_shell["pairing_asset"],
                "install_sequence": onboarding["steps"],
                "handoff_status": "handoff_package_ready",
            },
        }

    def get_install_sequence(self) -> Dict[str, Any]:
        onboarding = desktop_installer_onboarding_service.get_onboarding_bundle()["onboarding"]
        return {
            "ok": True,
            "mode": "desktop_mobile_install_sequence",
            "install_sequence": onboarding["steps"],
        }

    def get_pairing_summary(self) -> Dict[str, Any]:
        pairing = first_run_bundle_service.get_pairing_asset()["pairing_asset"]
        return {
            "ok": True,
            "mode": "desktop_mobile_pairing_summary",
            "pairing_summary": {
                "pairing_asset": pairing["asset_name"],
                "pairing_code": pairing["pairing_code"],
                "pairing_mode": pairing["pairing_payload"]["pairing_mode"],
                "local_backend_url": pairing["pairing_payload"]["local_backend_url"],
                "local_shell_url": pairing["pairing_payload"]["local_shell_url"],
            },
        }


desktop_mobile_handoff_service = DesktopMobileHandoffService()
