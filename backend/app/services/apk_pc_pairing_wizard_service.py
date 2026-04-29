from __future__ import annotations

import hashlib
import secrets
import socket
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import uuid4

from app.utils.atomic_json_store import AtomicJsonStore

DATA_DIR = Path("data")
PAIRING_FILE = DATA_DIR / "apk_pc_pairing_wizard.json"
PAIRING_STORE = AtomicJsonStore(
    PAIRING_FILE,
    default_factory=lambda: {
        "version": 1,
        "policy": "short_lived_pairing_tokens_no_secret_storage",
        "sessions": [],
        "heartbeats": [],
        "confirmations": [],
    },
)


class ApkPcPairingWizardService:
    """First-run APK <-> PC pairing wizard.

    The wizard is designed for mobile-first installation: the PC backend exposes a
    short-lived pairing session and the APK can connect using LAN URL/QR/manual
    code. It stores only hashes of pairing tokens, never passwords/API keys.
    """

    DEFAULT_PORT = 8000
    TOKEN_TTL_MINUTES = 15

    def _now(self) -> datetime:
        return datetime.now(timezone.utc)

    def _now_iso(self) -> str:
        return self._now().isoformat()

    def _hash(self, token: str) -> str:
        return hashlib.sha256(token.encode("utf-8")).hexdigest()

    def _local_ips(self) -> List[str]:
        ips = []
        try:
            hostname = socket.gethostname()
            for info in socket.getaddrinfo(hostname, None):
                ip = info[4][0]
                if ":" not in ip and not ip.startswith("127.") and ip not in ips:
                    ips.append(ip)
        except Exception:
            pass
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
                sock.connect(("8.8.8.8", 80))
                ip = sock.getsockname()[0]
                if ip and not ip.startswith("127.") and ip not in ips:
                    ips.append(ip)
        except Exception:
            pass
        return ips or ["127.0.0.1"]

    def start(self, port: int = DEFAULT_PORT, label: str = "God Mode PC") -> Dict[str, Any]:
        pairing_code = f"GM-{secrets.randbelow(900000) + 100000}"
        raw_token = secrets.token_urlsafe(24)
        session_id = f"apk-pc-pairing-{uuid4().hex[:12]}"
        expires_at = self._now() + timedelta(minutes=self.TOKEN_TTL_MINUTES)
        ips = self._local_ips()
        base_urls = [f"http://{ip}:{port}" for ip in ips]
        session = {
            "session_id": session_id,
            "created_at": self._now_iso(),
            "expires_at": expires_at.isoformat(),
            "label": label,
            "port": port,
            "local_ips": ips,
            "base_urls": base_urls,
            "pairing_code": pairing_code,
            "token_hash": self._hash(raw_token),
            "status": "waiting_for_apk",
            "manual_url": f"{base_urls[0]}/api/apk-pc-pairing/confirm" if base_urls else None,
            "qr_payload": {
                "kind": "god_mode_pairing",
                "session_id": session_id,
                "base_urls": base_urls,
                "pairing_code": pairing_code,
                "token": raw_token,
                "expires_at": expires_at.isoformat(),
            },
            "security_note": "token is returned once for QR/manual pairing; only token hash is stored",
        }
        self._store("sessions", self._redact_session_for_store(session))
        response = dict(session)
        return {"ok": True, "mode": "apk_pc_pairing_started", "session": response}

    def _redact_session_for_store(self, session: Dict[str, Any]) -> Dict[str, Any]:
        safe = dict(session)
        qr = dict(safe.get("qr_payload") or {})
        if "token" in qr:
            qr["token"] = "<returned_once_not_stored>"
        safe["qr_payload"] = qr
        return safe

    def confirm(
        self,
        session_id: str,
        pairing_code: str,
        token: str,
        apk_device_label: str = "Android APK",
    ) -> Dict[str, Any]:
        session = self._find_session(session_id)
        if not session:
            return {"ok": False, "mode": "apk_pc_pairing_confirm", "error": "session_not_found"}
        if self._is_expired(session):
            return {"ok": False, "mode": "apk_pc_pairing_confirm", "error": "session_expired", "session_id": session_id}
        if session.get("pairing_code") != pairing_code:
            return {"ok": False, "mode": "apk_pc_pairing_confirm", "error": "invalid_pairing_code"}
        if session.get("token_hash") != self._hash(token):
            return {"ok": False, "mode": "apk_pc_pairing_confirm", "error": "invalid_token"}
        confirmation = {
            "confirmation_id": f"apk-pc-confirmation-{uuid4().hex[:12]}",
            "created_at": self._now_iso(),
            "session_id": session_id,
            "apk_device_label": apk_device_label,
            "status": "paired",
            "backend_base_urls": session.get("base_urls", []),
            "recommended_base_url": (session.get("base_urls") or [None])[0],
            "next_endpoint": "/api/home-operator-ux/panel",
        }
        self._store("confirmations", confirmation)
        self._update_session_status(session_id, "paired")
        return {"ok": True, "mode": "apk_pc_pairing_confirmed", "confirmation": confirmation}

    def heartbeat(self, session_id: str, apk_device_label: str = "Android APK") -> Dict[str, Any]:
        session = self._find_session(session_id)
        if not session:
            return {"ok": False, "mode": "apk_pc_pairing_heartbeat", "error": "session_not_found"}
        heartbeat = {
            "heartbeat_id": f"apk-pc-heartbeat-{uuid4().hex[:12]}",
            "created_at": self._now_iso(),
            "session_id": session_id,
            "apk_device_label": apk_device_label,
            "backend_status": "online",
            "session_status": session.get("status"),
            "home_endpoint": "/api/home-operator-ux/panel",
            "critical_actions_endpoint": "/api/home-critical-actions/panel",
        }
        self._store("heartbeats", heartbeat)
        return {"ok": True, "mode": "apk_pc_pairing_heartbeat", "heartbeat": heartbeat}

    def guide(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "mode": "apk_pc_pairing_guide",
            "headline": "Ligar APK ao PC",
            "steps": [
                {"step": 1, "label": "Abrir God Mode no PC"},
                {"step": 2, "label": "Clicar em Emparelhar APK"},
                {"step": 3, "label": "Abrir APK no telemóvel"},
                {"step": 4, "label": "Ler QR ou inserir URL/código manual"},
                {"step": 5, "label": "Confirmar ligação"},
                {"step": 6, "label": "Abrir Modo Fácil"},
            ],
            "fallbacks": [
                "Se QR falhar, usar URL manual.",
                "Se IP local não abrir, confirmar que PC e telemóvel estão na mesma rede.",
                "Se firewall bloquear, pedir autorização no Windows para o backend.",
                "Se APK fechar, backend continua e heartbeat retoma quando voltar.",
            ],
            "security": [
                "token temporário expira",
                "token não é guardado em claro",
                "não guarda passwords, cookies ou API keys",
            ],
        }

    def _find_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        sessions = PAIRING_STORE.load().get("sessions", [])
        return next((s for s in sessions if s.get("session_id") == session_id), None)

    def _is_expired(self, session: Dict[str, Any]) -> bool:
        try:
            expires_at = datetime.fromisoformat(session.get("expires_at"))
            return self._now() > expires_at
        except Exception:
            return True

    def _update_session_status(self, session_id: str, status: str) -> None:
        def mutate(state: Dict[str, Any]) -> Dict[str, Any]:
            for session in state.get("sessions", []):
                if session.get("session_id") == session_id:
                    session["status"] = status
                    session["updated_at"] = self._now_iso()
            return state
        PAIRING_STORE.update(mutate)

    def _store(self, key: str, value: Dict[str, Any]) -> None:
        def mutate(state: Dict[str, Any]) -> Dict[str, Any]:
            state.setdefault(key, [])
            state[key].append(value)
            state[key] = state[key][-100:]
            return state
        PAIRING_STORE.update(mutate)

    def latest(self) -> Dict[str, Any]:
        state = PAIRING_STORE.load()
        return {
            "ok": True,
            "mode": "apk_pc_pairing_latest",
            "latest_session": (state.get("sessions") or [None])[-1],
            "latest_heartbeat": (state.get("heartbeats") or [None])[-1],
            "latest_confirmation": (state.get("confirmations") or [None])[-1],
            "session_count": len(state.get("sessions") or []),
            "heartbeat_count": len(state.get("heartbeats") or []),
            "confirmation_count": len(state.get("confirmations") or []),
        }

    def panel(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "mode": "apk_pc_pairing_panel",
            "headline": "Emparelhar APK ao PC",
            "guide": self.guide(),
            "latest": self.latest(),
            "safe_buttons": [
                {"id": "start", "label": "Emparelhar APK", "endpoint": "/api/apk-pc-pairing/start", "priority": "critical"},
                {"id": "guide", "label": "Guia ligação", "endpoint": "/api/apk-pc-pairing/guide", "priority": "high"},
                {"id": "latest", "label": "Última ligação", "endpoint": "/api/apk-pc-pairing/latest", "priority": "high"},
            ],
        }

    def get_status(self) -> Dict[str, Any]:
        latest = self.latest()
        confirmation = latest.get("latest_confirmation") or {}
        return {
            "ok": True,
            "mode": "apk_pc_pairing_status",
            "paired": bool(confirmation),
            "latest_confirmation": confirmation,
            "session_count": latest.get("session_count", 0),
            "token_ttl_minutes": self.TOKEN_TTL_MINUTES,
            "stores_plain_token": False,
        }

    def get_package(self) -> Dict[str, Any]:
        return {"ok": True, "mode": "apk_pc_pairing_package", "package": {"status": self.get_status(), "panel": self.panel(), "latest": self.latest()}}


apk_pc_pairing_wizard_service = ApkPcPairingWizardService()
