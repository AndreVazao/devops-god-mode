from __future__ import annotations

import os
import socket
from datetime import datetime, timezone
from typing import Any, Dict, List

DEFAULT_PORT = int(os.environ.get("PORT", os.environ.get("GODMODE_PORT", "8000")))


class PcMobilePairingService:
    """PC-side pairing helper for the Android WebView shell.

    It does not store secrets. It exposes likely local URLs so the operator can pair the
    APK with the PC backend quickly, while APK auto-discovery remains the preferred path.
    """

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def _candidate_ips(self) -> List[str]:
        ips: List[str] = ["127.0.0.1"]
        try:
            hostname = socket.gethostname()
            for item in socket.getaddrinfo(hostname, None):
                candidate = item[4][0]
                if ":" in candidate:
                    continue
                if candidate not in ips:
                    ips.append(candidate)
        except Exception:
            pass
        try:
            probe = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            probe.connect(("8.8.8.8", 80))
            candidate = probe.getsockname()[0]
            probe.close()
            if candidate not in ips:
                ips.append(candidate)
        except Exception:
            pass
        return ips

    def _urls(self) -> List[Dict[str, Any]]:
        urls: List[Dict[str, Any]] = []
        for ip in self._candidate_ips():
            base_url = f"http://{ip}:{DEFAULT_PORT}"
            urls.append(
                {
                    "ip": ip,
                    "base_url": base_url,
                    "health_url": f"{base_url}/health",
                    "apk_start_url": f"{base_url}/app/apk-start",
                    "first_use_url": f"{base_url}/app/first-use",
                    "chat_url": f"{base_url}/app/operator-chat-sync-cards",
                    "recommended_for_phone": not ip.startswith("127."),
                }
            )
        return urls

    def get_status(self) -> Dict[str, Any]:
        urls = self._urls()
        recommended = next((item for item in urls if item["recommended_for_phone"]), urls[0] if urls else None)
        return {
            "ok": True,
            "mode": "pc_mobile_pairing_status",
            "status": "pairing_ready",
            "port": DEFAULT_PORT,
            "candidate_count": len(urls),
            "recommended_base_url": recommended.get("base_url") if recommended else None,
            "secret_storage": False,
            "requires_credentials": False,
        }

    def build_pairing_package(self) -> Dict[str, Any]:
        urls = self._urls()
        recommended = next((item for item in urls if item["recommended_for_phone"]), urls[0] if urls else None)
        return {
            "ok": True,
            "mode": "pc_mobile_pairing_package",
            "created_at": self._now(),
            "port": DEFAULT_PORT,
            "recommended": recommended,
            "urls": urls,
            "apk_instruction": "No APK, carregar em Auto. Se falhar, copiar o Recommended base URL para o campo do APK e carregar em Teste.",
            "manual_fallback": True,
            "security_note": "Não introduzir tokens, passwords, cookies ou API keys no chat/pairing.",
        }

    def build_dashboard(self) -> Dict[str, Any]:
        package = self.build_pairing_package()
        return {
            "ok": True,
            "mode": "pc_mobile_pairing_dashboard",
            "package": package,
            "buttons": [
                {"id": "apk_start", "label": "Abrir APK Start", "route": "/app/apk-start", "priority": "critical"},
                {"id": "first_use", "label": "First Use", "route": "/app/first-use", "priority": "high"},
                {"id": "chat", "label": "Chat", "route": "/app/operator-chat-sync-cards", "priority": "high"},
                {"id": "artifacts", "label": "Artifacts", "route": "/app/release-artifacts", "priority": "medium"},
            ],
        }

    def get_package(self) -> Dict[str, Any]:
        return {"ok": True, "mode": "pc_mobile_pairing_full_package", "package": {"status": self.get_status(), "dashboard": self.build_dashboard(), "pairing": self.build_pairing_package()}}


pc_mobile_pairing_service = PcMobilePairingService()
