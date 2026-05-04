from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List


class AppEntrypointManifestService:
    """Canonical launcher/APK entrypoint contract.

    Phase 174 formalizes `/app/home` as the default visual cockpit route for
    desktop launcher, browser and Android WebView. Older entry routes remain as
    compatibility aliases and redirect to the canonical route.
    """

    SERVICE_ID = "app_entrypoint_manifest"
    VERSION = "phase_174_v1"
    CANONICAL_ROUTE = "/app/home"
    LOCAL_BASE_URL = "http://127.0.0.1:8000"
    BACKEND_PORT = 8000

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def status(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "service": self.SERVICE_ID,
            "version": self.VERSION,
            "created_at": self._now(),
            "canonical_route": self.CANONICAL_ROUTE,
            "canonical_url": f"{self.LOCAL_BASE_URL}{self.CANONICAL_ROUTE}",
            "desktop_default_route": self.CANONICAL_ROUTE,
            "android_default_route": self.CANONICAL_ROUTE,
            "browser_default_route": self.CANONICAL_ROUTE,
            "compatibility_redirects_enabled": True,
        }

    def aliases(self) -> List[Dict[str, Any]]:
        return [
            {"route": "/app", "target": self.CANONICAL_ROUTE, "reason": "short app entrypoint"},
            {"route": "/desktop", "target": self.CANONICAL_ROUTE, "reason": "desktop launcher fallback"},
            {"route": "/mobile", "target": self.CANONICAL_ROUTE, "reason": "mobile shell fallback"},
            {"route": "/app/apk-start", "target": self.CANONICAL_ROUTE, "reason": "legacy APK build metadata compatibility"},
            {"route": "/app/mobile", "target": self.CANONICAL_ROUTE, "reason": "mobile webview compatibility"},
            {"route": "/home", "target": self.CANONICAL_ROUTE, "reason": "human-friendly fallback"},
        ]

    def manifest(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "service": self.SERVICE_ID,
            "version": self.VERSION,
            "generated_at": self._now(),
            "canonical": {
                "route": self.CANONICAL_ROUTE,
                "local_url": f"{self.LOCAL_BASE_URL}{self.CANONICAL_ROUTE}",
                "control_surface_package": "/api/home-control-surface/package",
                "visual_shell_package": "/api/home-visual-shell/package",
            },
            "desktop_launcher": {
                "expected_config_key": "shell_url",
                "default_route": self.CANONICAL_ROUTE,
                "default_url": f"{self.LOCAL_BASE_URL}{self.CANONICAL_ROUTE}",
                "backend_port": self.BACKEND_PORT,
                "boot_sequence": ["start_backend", "wait_for_health", "open_app_home"],
            },
            "android_webview": {
                "expected_constant": "ENTRY_ROUTE",
                "default_route": self.CANONICAL_ROUTE,
                "default_base_url": self.LOCAL_BASE_URL,
                "physical_phone_note": "Use the PC LAN backend URL, for example http://192.168.x.x:8000, then open /app/home.",
            },
            "browser": {
                "default_route": self.CANONICAL_ROUTE,
                "supported_aliases": [item["route"] for item in self.aliases()],
            },
            "compatibility_aliases": self.aliases(),
            "safety": {
                "direct_destructive_actions": False,
                "rendered_actions_source": "/api/home-control-surface/package",
                "server_side_gates_remain_authoritative": True,
            },
        }

    def package(self) -> Dict[str, Any]:
        return {"status": self.status(), "manifest": self.manifest()}


app_entrypoint_manifest_service = AppEntrypointManifestService()
