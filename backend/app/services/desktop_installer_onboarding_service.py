from typing import Any, Dict

from app.services.first_run_bundle_service import first_run_bundle_service


class DesktopInstallerOnboardingService:
    def get_installer_manifest(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "mode": "desktop_installer_manifest",
            "manifest": {
                "installer_id": "installer_pc_phone_primary",
                "package_name": "GodModeDesktopBundle",
                "primary_executable": "GodModeDesktop.exe",
                "support_scripts": [
                    "windows_shortcut_bootstrap.ps1",
                    "windows_autostart_bootstrap.ps1",
                    "windows_autostart_remove.ps1",
                ],
                "onboarding_assets": [
                    "desktop_first_run_payload.json",
                    "desktop_shortcut_payload.json",
                    "desktop_autostart_payload.json",
                    "godmode-mobile-pairing.json",
                ],
                "install_mode": "desktop_bundle_local_actions",
                "installer_status": "installer_manifest_ready",
            },
        }

    def get_onboarding_bundle(self) -> Dict[str, Any]:
        first_run = first_run_bundle_service.get_bundle()["bundle"]
        return {
            "ok": True,
            "mode": "desktop_onboarding_bundle",
            "onboarding": {
                "onboarding_id": "onboarding_pc_phone_primary",
                "runtime_mode": "pc_and_phone_primary",
                "steps": [
                    "launch_desktop_bundle",
                    "read_manifest",
                    "run_first_bootstrap",
                    "create_desktop_shortcut_if_enabled",
                    "enable_autostart_if_enabled",
                    "open_mobile_pairing",
                ],
                "desktop_assets": [
                    "GodModeDesktop.exe",
                    "desktop_first_run_payload.json",
                    "desktop_shortcut_payload.json",
                    "desktop_autostart_payload.json",
                ],
                "mobile_assets": first_run["mobile_payloads"],
                "pairing_required": True,
                "onboarding_status": "onboarding_bundle_ready",
            },
        }

    def get_bundle_inventory(self) -> Dict[str, Any]:
        first_run = first_run_bundle_service.get_bundle()["bundle"]
        return {
            "ok": True,
            "mode": "desktop_bundle_inventory",
            "inventory": {
                "bundle_id": "desktop_bundle_pc_phone_primary",
                "package_name": "GodModeDesktopBundle",
                "primary_executable": "GodModeDesktop.exe",
                "support_files": [
                    "windows_shortcut_bootstrap.ps1",
                    "windows_autostart_bootstrap.ps1",
                    "windows_autostart_remove.ps1",
                ],
                "onboarding_files": [
                    "desktop-installer-manifest.json",
                    "desktop-onboarding.json",
                ],
                "mobile_linked_assets": first_run["mobile_payloads"],
                "delivery_mode": "local_bundle_artifact",
                "inventory_status": "bundle_inventory_ready",
            },
        }


desktop_installer_onboarding_service = DesktopInstallerOnboardingService()
