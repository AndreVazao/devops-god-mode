from __future__ import annotations

import base64
import json
import os
import shutil
import socket
import subprocess
from datetime import datetime, timezone
from typing import Any, Dict, List
from urllib.parse import quote

DEFAULT_PORT = int(os.environ.get("PORT", os.environ.get("GODMODE_PORT", "8000")))


class PrivateTunnelCenterService:
    """Guided private tunnel center for APK -> PC access outside the LAN.

    This service does not store or request secrets. It detects local tools when possible
    and presents safe instructions for manual login/setup.
    """

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def _cmd_exists(self, command: str) -> bool:
        return shutil.which(command) is not None

    def _safe_run(self, command: List[str], timeout: int = 3) -> Dict[str, Any]:
        try:
            result = subprocess.run(command, capture_output=True, text=True, timeout=timeout, check=False)
            text = (result.stdout or result.stderr or "").strip()
            return {"ok": result.returncode == 0, "returncode": result.returncode, "output": text[:1000]}
        except Exception as exc:
            return {"ok": False, "returncode": None, "output": str(exc)[:1000]}

    def _provider_statuses(self) -> List[Dict[str, Any]]:
        tailscale_present = self._cmd_exists("tailscale")
        cloudflared_present = self._cmd_exists("cloudflared")
        ngrok_present = self._cmd_exists("ngrok")
        tailscale_status = self._safe_run(["tailscale", "status", "--self"]) if tailscale_present else {"ok": False, "output": "tailscale not installed"}
        tailscale_ip = self._safe_run(["tailscale", "ip", "-4"]) if tailscale_present else {"ok": False, "output": ""}
        return [
            {
                "provider_id": "tailscale",
                "label": "Tailscale private network",
                "recommended": True,
                "free_path": True,
                "privacy_model": "private_mesh_vpn",
                "installed": tailscale_present,
                "status_ok": tailscale_status.get("ok", False),
                "detected_ip": tailscale_ip.get("output") if tailscale_ip.get("ok") else None,
                "apk_base_url": f"http://{tailscale_ip.get('output')}:{DEFAULT_PORT}" if tailscale_ip.get("ok") and tailscale_ip.get("output") else None,
                "requires_manual_login": True,
                "stores_secrets": False,
                "operator_note": "Recommended for street/remote use. Install Tailscale on PC and phone, login manually, then use the Tailscale IP in the APK.",
            },
            {
                "provider_id": "cloudflare_tunnel",
                "label": "Cloudflare Tunnel",
                "recommended": False,
                "free_path": True,
                "privacy_model": "public_or_zero_trust_tunnel_if_configured",
                "installed": cloudflared_present,
                "status_ok": False,
                "detected_ip": None,
                "apk_base_url": None,
                "requires_manual_login": True,
                "stores_secrets": False,
                "operator_note": "Alternative only. Can expose a public URL if misconfigured. Use with explicit approval and manual login/configuration.",
            },
            {
                "provider_id": "ngrok",
                "label": "ngrok / temporary tunnel",
                "recommended": False,
                "free_path": True,
                "privacy_model": "temporary_public_tunnel",
                "installed": ngrok_present,
                "status_ok": False,
                "detected_ip": None,
                "apk_base_url": None,
                "requires_manual_login": True,
                "stores_secrets": False,
                "operator_note": "Temporary fallback. Do not use for normal operation without authentication controls.",
            },
        ]

    def _local_base_url(self) -> str:
        try:
            probe = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            probe.connect(("8.8.8.8", 80))
            ip = probe.getsockname()[0]
            probe.close()
        except Exception:
            ip = "127.0.0.1"
        return f"http://{ip}:{DEFAULT_PORT}"

    def _recommended_provider(self, providers: List[Dict[str, Any]]) -> Dict[str, Any]:
        return next((item for item in providers if item["provider_id"] == "tailscale"), providers[0])

    def build_pairing_payload(self) -> Dict[str, Any]:
        report = self.build_tunnel_report(include_pairing=False)
        provider = self._recommended_provider(report["providers"])
        base_url = provider.get("apk_base_url") or report.get("local_base_url")
        payload = {
            "type": "god_mode_mobile_pairing",
            "version": 1,
            "provider": provider.get("provider_id"),
            "base_url": base_url,
            "health_url": f"{base_url}/health" if base_url else None,
            "entry_url": f"{base_url}/app/apk-start" if base_url else None,
            "created_at": self._now(),
            "contains_secret": False,
            "operator_note": "Non-secret pairing payload. Use in APK as base URL if Auto fails.",
        }
        compact = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
        encoded = base64.urlsafe_b64encode(compact.encode("utf-8")).decode("ascii").rstrip("=")
        deep_link = f"godmode://pair?payload={quote(encoded)}"
        browser_link = f"{base_url}/app/apk-start" if base_url else None
        return {
            "ok": True,
            "mode": "private_tunnel_pairing_payload",
            "payload": payload,
            "payload_json": json.dumps(payload, ensure_ascii=False, indent=2),
            "payload_compact": compact,
            "payload_base64url": encoded,
            "deep_link": deep_link,
            "browser_link": browser_link,
            "qr_ready_text": deep_link,
            "qr_status": "qr_ready_payload_not_secret",
            "is_scannable_qr_generated": False,
            "security": {
                "contains_secret": False,
                "safe_to_show_on_screen": True,
                "safe_to_copy": True,
            },
        }

    def build_tunnel_report(self, include_pairing: bool = True) -> Dict[str, Any]:
        providers = self._provider_statuses()
        recommended = self._recommended_provider(providers)
        blockers = []
        if not recommended.get("installed"):
            blockers.append({"id": "tailscale:not_installed", "label": "Tailscale não encontrado no PC", "detail": "Instalar Tailscale manualmente no PC e telemóvel."})
        if recommended.get("installed") and not recommended.get("status_ok"):
            blockers.append({"id": "tailscale:not_logged_in", "label": "Tailscale não está pronto", "detail": "Abrir Tailscale e fazer login manual."})
        status = "green" if recommended.get("apk_base_url") and not blockers else "yellow"
        report = {
            "ok": True,
            "mode": "private_tunnel_center_report",
            "created_at": self._now(),
            "status": status,
            "recommended_provider": "tailscale",
            "local_base_url": self._local_base_url(),
            "providers": providers,
            "blockers": blockers,
            "security": {
                "stores_tokens": False,
                "stores_passwords": False,
                "stores_cookies": False,
                "manual_login_required": True,
                "default_exposes_public_url": False,
            },
            "street_mode_steps": self._street_mode_steps(recommended),
            "apk_instruction": self._apk_instruction(recommended),
            "next_actions": self._next_actions(blockers, recommended),
        }
        if include_pairing:
            report["pairing_payload"] = self.build_pairing_payload()
        return report

    def _street_mode_steps(self, tailscale: Dict[str, Any]) -> List[Dict[str, Any]]:
        return [
            {"step": 1, "label": "Instalar Tailscale no PC", "detail": "Instalar manualmente e iniciar sessão. O God Mode não guarda login."},
            {"step": 2, "label": "Instalar Tailscale no telemóvel", "detail": "Entrar na mesma conta/rede privada."},
            {"step": 3, "label": "Confirmar IP Tailscale do PC", "detail": tailscale.get("detected_ip") or "Depois de login, o God Mode tenta mostrar o IP Tailscale aqui."},
            {"step": 4, "label": "Abrir APK na rua", "detail": "Usar Auto. Se falhar, colar o URL Tailscale recomendado."},
            {"step": 5, "label": "Validar /health", "detail": "O APK deve abrir /app/apk-start quando /health responder."},
            {"step": 6, "label": "Usar pairing não secreto", "detail": "Copiar o deep link/payload não secreto se o Auto falhar."},
        ]

    def _apk_instruction(self, tailscale: Dict[str, Any]) -> str:
        if tailscale.get("apk_base_url"):
            return f"No APK, usar Auto ou colar {tailscale['apk_base_url']} e carregar em Teste."
        return "No APK, usar Auto na mesma rede. Para rua, instalar/logar Tailscale no PC e telemóvel, depois colar o IP Tailscale do PC."

    def _next_actions(self, blockers: List[Dict[str, Any]], tailscale: Dict[str, Any]) -> List[Dict[str, Any]]:
        actions = []
        if blockers:
            actions.extend({"priority": "critical", "label": blocker["label"], "detail": blocker["detail"]} for blocker in blockers)
        if tailscale.get("apk_base_url"):
            actions.append({"priority": "critical", "label": "Testar APK pela rede Tailscale", "detail": tailscale["apk_base_url"]})
        actions.extend([
            {"priority": "high", "label": "Manter LAN Auto Discovery como fallback", "detail": "/app/pairing"},
            {"priority": "medium", "label": "Usar pairing payload não secreto", "detail": "Copiar deep link ou base URL para o APK."},
            {"priority": "medium", "label": "Futuro: QR scannable real", "detail": "Adicionar gerador QR local aprovado para o deep link não secreto."},
        ])
        return actions

    def get_status(self) -> Dict[str, Any]:
        report = self.build_tunnel_report(include_pairing=False)
        return {
            "ok": True,
            "mode": "private_tunnel_center_status",
            "status": report["status"],
            "recommended_provider": report["recommended_provider"],
            "blocker_count": len(report["blockers"]),
            "stores_secrets": False,
            "pairing_payload_available": True,
        }

    def build_dashboard(self) -> Dict[str, Any]:
        report = self.build_tunnel_report()
        return {
            "ok": True,
            "mode": "private_tunnel_center_dashboard",
            "report": report,
            "buttons": [
                {"id": "pairing", "label": "Pairing LAN", "route": "/app/pairing", "priority": "high"},
                {"id": "apk_start", "label": "APK Start", "route": "/app/apk-start", "priority": "high"},
                {"id": "first_use", "label": "First Use", "route": "/app/first-use", "priority": "medium"},
                {"id": "artifacts", "label": "Artifacts", "route": "/app/release-artifacts", "priority": "medium"},
            ],
        }

    def get_package(self) -> Dict[str, Any]:
        return {"ok": True, "mode": "private_tunnel_center_package", "package": {"status": self.get_status(), "dashboard": self.build_dashboard(), "report": self.build_tunnel_report(), "pairing": self.build_pairing_payload()}}


private_tunnel_center_service = PrivateTunnelCenterService()
