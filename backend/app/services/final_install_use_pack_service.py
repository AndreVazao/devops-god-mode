from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List

from app.services.artifacts_center_service import artifacts_center_service
from app.services.first_pc_autopilot_ready_flow_service import first_pc_autopilot_ready_flow_service
from app.services.god_mode_global_state_service import god_mode_global_state_service
from app.services.ia_operator_permission_vault_bridge_service import ia_operator_permission_vault_bridge_service
from app.services.mobile_pc_pairing_remote_access_service import mobile_pc_pairing_remote_access_service


class FinalInstallUsePackService:
    SERVICE_ID = "final_install_use_pack"
    VERSION = "phase_210_v1"

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def status(self) -> Dict[str, Any]:
        checks = self.final_readiness()
        return {
            "ok": True,
            "service": self.SERVICE_ID,
            "version": self.VERSION,
            "generated_at": self._now(),
            "final_ready_score": checks.get("final_ready_score"),
            "ready_to_install_and_use": checks.get("ready_to_install_and_use"),
            "route": "/app/install-use-now",
            "alias": "/app/final-ready",
        }

    def final_readiness(self) -> Dict[str, Any]:
        checks = [
            self._check("global_state", god_mode_global_state_service.status(), "/api/god-mode-global-state/package"),
            self._check("artifacts", artifacts_center_service.status(), "/api/artifacts-center/status"),
            self._check("today_ready", first_pc_autopilot_ready_flow_service.status(), "/api/first-pc-autopilot-ready/package"),
            self._check("pc_mobile_pairing", mobile_pc_pairing_remote_access_service.status(), "/api/mobile-pc-pairing/package"),
            self._check("ia_bridge", ia_operator_permission_vault_bridge_service.status(), "/api/ia-operator-bridge/package"),
        ]
        passed = sum(1 for item in checks if item.get("ok"))
        score = round((passed / max(1, len(checks))) * 100)
        return {
            "ok": True,
            "mode": "final_install_use_readiness",
            "generated_at": self._now(),
            "final_ready_score": score,
            "ready_to_install_and_use": score >= 90,
            "checks": checks,
        }

    def apk_endpoint_contract(self) -> Dict[str, Any]:
        manifest = mobile_pc_pairing_remote_access_service.connection_manifest()
        candidates = manifest.get("mobile_should_try_in_order", [])
        return {
            "ok": True,
            "mode": "apk_endpoint_contract",
            "generated_at": self._now(),
            "manifest_endpoint": "/api/mobile-pc-pairing/connection-manifest",
            "recommended_start_url_home": "http://192.168.1.81:8000/app/mobile-permission-relay",
            "lan_sweep_endpoint": "/api/mobile-pc-pairing/lan-scan-candidates",
            "fallback_routes": [
                "/app/mobile-permission-relay",
                "/app/today-ready",
                "/app/ia-operator-bridge",
                "/app/god-mode-vault",
                "/app/connect-phone",
            ],
            "apk_behavior": [
                "Load last_working_endpoint if available.",
                "If it fails, fetch or use cached connection_manifest.",
                "Try home_lan candidates first, including sweep 192.168.1.61-101.",
                "If LAN fails, try configured remote endpoint.",
                "Save the first working endpoint as last_working_endpoint.",
                "Open /app/mobile-permission-relay by default after connection.",
            ],
            "mobile_should_try_in_order": candidates,
            "connection_manifest": manifest,
        }

    def install_steps(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "mode": "final_install_steps",
            "pc": [
                {"step": 1, "title": "Download Windows artifact", "action": "Open GitHub Actions → Windows EXE Build → latest green run → download godmode-windows-exe."},
                {"step": 2, "title": "Extract and run", "action": "Extract ZIP and open GodModeDesktop.exe."},
                {"step": 3, "title": "Open final ready page", "action": "Go to http://127.0.0.1:8000/app/install-use-now."},
                {"step": 4, "title": "Pair phone", "action": "Open /app/connect-phone and create pairing. PC LAN sweep includes 192.168.1.61-101."},
                {"step": 5, "title": "Add Vault material if needed", "action": "Open /app/god-mode-vault and paste .env/URLs/access material only if needed."},
                {"step": 6, "title": "Start Autopilot", "action": "Open /app/today-ready and press Start Autopilot."},
            ],
            "phone": [
                {"step": 1, "title": "Install APK artifact", "action": "Install latest godmode-android-webview-apk from Android APK Build."},
                {"step": 2, "title": "Home connection", "action": "Try http://192.168.1.81:8000/app/mobile-permission-relay. If it fails, use LAN sweep manifest."},
                {"step": 3, "title": "Remote connection", "action": "For outside home, configure Tailscale/Cloudflare/Ngrok/manual HTTPS URL in /app/connect-phone."},
                {"step": 4, "title": "Use cockpit", "action": "Use /app/mobile-permission-relay for approvals and /app/driver-voice-permissions for voice mode."},
            ],
        }

    def start_now(self, tenant_id: str = "owner-andre") -> Dict[str, Any]:
        readiness = self.final_readiness()
        if not readiness.get("ready_to_install_and_use"):
            return {"ok": False, "mode": "final_start_now", "error": "final_readiness_below_threshold", "readiness": readiness}
        loop = first_pc_autopilot_ready_flow_service.start_today_autopilot(tenant_id=tenant_id)
        return {"ok": True, "mode": "final_start_now", "readiness": readiness, "autopilot": loop}

    def package(self) -> Dict[str, Any]:
        return {
            "status": self.status(),
            "readiness": self.final_readiness(),
            "install_steps": self.install_steps(),
            "apk_endpoint_contract": self.apk_endpoint_contract(),
            "today_ready": first_pc_autopilot_ready_flow_service.launch_contract(),
        }

    def _check(self, name: str, payload: Dict[str, Any], route: str) -> Dict[str, Any]:
        return {
            "name": name,
            "ok": bool(payload.get("ok", True)),
            "route": route,
            "summary": {key: payload.get(key) for key in ["service", "version", "current_phase", "latest_merged_phase", "ready_score", "is_today_ready"] if key in payload},
        }


final_install_use_pack_service = FinalInstallUsePackService()
