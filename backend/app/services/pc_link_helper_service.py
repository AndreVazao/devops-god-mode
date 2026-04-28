from __future__ import annotations

import socket
from datetime import datetime, timezone
from typing import Any, Dict, List


class PcLinkHelperService:
    """Mobile-first helper to connect the APK/WebView to the PC backend."""

    DEFAULT_PORT = 8000

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def _local_ips(self) -> List[str]:
        ips = {"127.0.0.1"}
        try:
            hostname = socket.gethostname()
            for info in socket.getaddrinfo(hostname, None, family=socket.AF_INET):
                ip = info[4][0]
                if ip and not ip.startswith("127."):
                    ips.add(ip)
        except Exception:
            pass
        return sorted(ips)

    def build_panel(self, port: int = DEFAULT_PORT) -> Dict[str, Any]:
        ips = self._local_ips()
        urls = [self._url(ip, port, "/app/home") for ip in ips]
        health_urls = [self._url(ip, port, "/health") for ip in ips]
        return {
            "ok": True,
            "mode": "pc_link_helper_panel",
            "created_at": self._now(),
            "port": port,
            "status": "ready_for_manual_pairing",
            "headline": "Ligar APK ao PC",
            "primary_url": urls[0] if urls else self._url("127.0.0.1", port, "/app/home"),
            "candidate_urls": urls,
            "health_urls": health_urls,
            "manual_url_template": f"http://IP_DO_PC:{port}/app/home",
            "steps": [
                {"step": 1, "label": "Abrir o God Mode no PC", "detail": "Confirmar que o backend responde em /health."},
                {"step": 2, "label": "PC e telemóvel na mesma rede", "detail": "Usar a mesma rede Wi-Fi ou hotspot local."},
                {"step": 3, "label": "Abrir o APK", "detail": "Introduzir um dos URLs candidatos ou o IP do PC."},
                {"step": 4, "label": "Confirmar Home", "detail": "A Home deve mostrar semáforo, botões e próxima ação."},
                {"step": 5, "label": "Correr Instalação final", "detail": "Validar tudo antes da primeira ordem longa."},
            ],
            "buttons": [
                {"label": "Home local", "url": urls[0] if urls else self._url("127.0.0.1", port, "/app/home")},
                {"label": "Health", "url": health_urls[0] if health_urls else self._url("127.0.0.1", port, "/health")},
                {"label": "Instalação final", "endpoint": "/api/install-readiness-final/check"},
                {"label": "Instalar agora", "endpoint": "/api/first-real-install-launcher/plan"},
            ],
            "troubleshooting": [
                {"id": "same_network", "label": "Confirmar mesma rede", "detail": "PC e telemóvel precisam conseguir comunicar pela rede local."},
                {"id": "firewall", "label": "Permitir backend no firewall", "detail": f"Permitir ligações locais à porta {port}."},
                {"id": "try_other_ip", "label": "Testar outro IP", "detail": "Alguns PCs têm mais de uma interface de rede."},
                {"id": "pc_first", "label": "Abrir PC primeiro", "detail": "O APK é controlo remoto; o PC precisa estar ligado primeiro."},
            ],
            "safety": {
                "pc_is_brain": True,
                "apk_is_remote": True,
                "no_secret_storage": True,
                "preserve_local_state": ["data/", "memory/", ".env", "backend/.env"],
            },
        }

    def _url(self, host: str, port: int, path: str) -> str:
        clean_path = path if path.startswith("/") else f"/{path}"
        return f"http://{host}:{port}{clean_path}"

    def get_status(self) -> Dict[str, Any]:
        panel = self.build_panel()
        return {
            "ok": True,
            "mode": "pc_link_helper_status",
            "status": panel["status"],
            "primary_url": panel["primary_url"],
            "candidate_count": len(panel["candidate_urls"]),
            "port": panel["port"],
        }

    def get_package(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "mode": "pc_link_helper_package",
            "package": {
                "status": self.get_status(),
                "panel": self.build_panel(),
            },
        }


pc_link_helper_service = PcLinkHelperService()
