from __future__ import annotations

import hashlib
import socket
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import uuid4

from app.services.final_install_readiness_v2_service import final_install_readiness_v2_service
from app.services.mobile_apk_update_orchestrator_service import mobile_apk_update_orchestrator_service
from app.utils.atomic_json_store import AtomicJsonStore

DATA_DIR = Path("data")
DOWNLOAD_CENTER_FILE = DATA_DIR / "download_install_center_v2.json"
DOWNLOAD_CENTER_STORE = AtomicJsonStore(
    DOWNLOAD_CENTER_FILE,
    default_factory=lambda: {
        "version": 2,
        "policy": "pc_artifact_cache_with_secure_mobile_download_and_drive_fallback",
        "packages": [],
        "shares": [],
        "transfers": [],
        "intake_requests": [],
    },
)


class DownloadInstallCenterV2Service:
    """Download/install center for EXE/APK and heavy file handoff.

    Preferred architecture:
    - PC downloads/caches artifacts after GitHub Actions builds.
    - Phone downloads APK from PC over paired LAN/tunnel when available.
    - If outside LAN/tunnel, use remote secure link or Drive/manual fallback.
    - Large visual checks/files can use the same transfer policy.
    """

    SHARE_TTL_MINUTES = 60
    DEFAULT_PORT = 8000
    ARTIFACTS = [
        {
            "id": "windows_exe",
            "label": "God Mode Desktop EXE",
            "filename": "GodModeDesktop.exe",
            "artifact_name": "godmode-windows-exe",
            "workflow": ".github/workflows/windows-exe-real-build.yml",
            "target": "pc",
            "install_mode": "run_exe",
        },
        {
            "id": "android_apk",
            "label": "God Mode Mobile APK",
            "filename": "GodModeMobile-debug.apk",
            "artifact_name": "godmode-android-webview-apk",
            "workflow": ".github/workflows/android-real-build-progressive.yml",
            "target": "android",
            "install_mode": "apk_prompt_or_adb",
        },
    ]

    def _now(self) -> datetime:
        return datetime.now(timezone.utc)

    def _now_iso(self) -> str:
        return self._now().isoformat()

    def _sha(self, value: str) -> str:
        return hashlib.sha256(value.encode("utf-8")).hexdigest()

    def _local_ips(self) -> List[str]:
        ips: List[str] = []
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

    def policy(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "mode": "download_install_center_policy",
            "preferred_channels": [
                {
                    "id": "pc_local_lan_or_tunnel",
                    "label": "PC serve artifacts ao telemóvel",
                    "best_for": "APK, prints, logs, ficheiros médios quando PC e telefone estão conectados",
                    "priority": 1,
                },
                {
                    "id": "remote_secure_link",
                    "label": "Link seguro remoto/túnel",
                    "best_for": "quando estás fora de casa e o PC está online",
                    "priority": 2,
                },
                {
                    "id": "drive_fallback",
                    "label": "Drive/manual fallback",
                    "best_for": "ficheiros grandes, fora da rede, ou quando túnel não estiver disponível",
                    "priority": 3,
                },
            ],
            "rules": [
                "PC é a cache principal dos artifacts depois do build",
                "telemóvel baixa do PC quando houver pairing/túnel/LAN",
                "fora da rede usar link seguro ou Drive/manual",
                "ficheiros pesados de visualização podem usar a mesma política",
                "não guardar tokens de Drive/túnel em memória",
                "links temporários devem expirar",
            ],
        }

    def build_package(
        self,
        version: str = "latest",
        commit_sha: str = "unknown",
        github_run_url: Optional[str] = None,
        artifact_base_url: Optional[str] = None,
    ) -> Dict[str, Any]:
        readiness = final_install_readiness_v2_service.get_status()
        artifacts = []
        for artifact in self.ARTIFACTS:
            local_path = f"artifacts/{version}/{artifact['filename']}"
            artifacts.append({
                **artifact,
                "version": version,
                "commit_sha": commit_sha,
                "local_cache_path": local_path,
                "github_artifact_hint": f"{github_run_url or '<github_run_url>'}::{artifact['artifact_name']}",
                "direct_url": f"{artifact_base_url.rstrip('/')}/{artifact['filename']}" if artifact_base_url else None,
                "status": "expected_from_workflow",
            })
        package = {
            "package_id": f"download-install-package-{uuid4().hex[:12]}",
            "created_at": self._now_iso(),
            "version": version,
            "commit_sha": commit_sha,
            "github_run_url": github_run_url,
            "ready_to_install_real": readiness.get("ready_to_install_real"),
            "readiness": readiness,
            "artifacts": artifacts,
            "install_steps": self.install_steps(),
            "transfer_policy": self.policy(),
        }
        self._store("packages", package)
        return {"ok": True, "mode": "download_install_package", "package": package}

    def install_steps(self) -> List[Dict[str, Any]]:
        return [
            {"step": 1, "label": "Confirmar gate final", "endpoint": "/api/final-install-readiness-v2/check"},
            {"step": 2, "label": "Baixar EXE no PC", "artifact_id": "windows_exe"},
            {"step": 3, "label": "Executar GodModeDesktop.exe", "expected": "backend online"},
            {"step": 4, "label": "Baixar APK no telemóvel pelo PC/LAN/túnel ou fallback", "artifact_id": "android_apk"},
            {"step": 5, "label": "Instalar APK", "expected": "mesmo package id/assinatura para manter dados"},
            {"step": 6, "label": "Emparelhar APK ↔ PC", "endpoint": "/api/apk-pc-pairing/start"},
            {"step": 7, "label": "Abrir Modo Fácil e Ações críticas", "endpoint": "/api/home-critical-actions/panel"},
            {"step": 8, "label": "Rodar smoke local", "endpoint": "/api/real-install-smoke-test/local-contract"},
        ]

    def create_share(
        self,
        artifact_id: str = "android_apk",
        channel: str = "auto",
        filename: Optional[str] = None,
        local_path: Optional[str] = None,
        port: int = DEFAULT_PORT,
    ) -> Dict[str, Any]:
        artifact = next((a for a in self.ARTIFACTS if a["id"] == artifact_id), None)
        if not artifact:
            return {"ok": False, "mode": "download_share", "error": "artifact_not_found"}
        safe_filename = filename or artifact["filename"]
        share_token = uuid4().hex + uuid4().hex[:8]
        expires_at = self._now() + timedelta(minutes=self.SHARE_TTL_MINUTES)
        ips = self._local_ips()
        local_urls = [f"http://{ip}:{port}/api/download-install-center-v2/download/{share_token}" for ip in ips]
        normalized_channel = self._channel(channel)
        share = {
            "share_id": f"download-share-{uuid4().hex[:12]}",
            "created_at": self._now_iso(),
            "expires_at": expires_at.isoformat(),
            "artifact_id": artifact_id,
            "filename": safe_filename,
            "local_path": local_path or f"artifacts/latest/{safe_filename}",
            "channel": normalized_channel,
            "share_token_hash": self._sha(share_token),
            "token_returned_once": True,
            "local_urls": local_urls,
            "remote_secure_link": None,
            "drive_fallback": {
                "enabled": normalized_channel in {"auto", "drive_fallback"},
                "status": "requires_drive_connector_or_manual_upload",
                "note": "não guardar tokens Drive; usar conector/login do operador quando disponível",
            },
            "payload_for_mobile": {
                "kind": "god_mode_download_share",
                "artifact_id": artifact_id,
                "filename": safe_filename,
                "local_urls": local_urls,
                "token": share_token,
                "expires_at": expires_at.isoformat(),
                "fallback": "drive_or_remote_secure_link",
            },
        }
        self._store("shares", self._redact_share(share))
        return {"ok": True, "mode": "download_share_created", "share": share}

    def _channel(self, channel: str) -> str:
        value = (channel or "auto").strip().lower().replace(" ", "_")
        allowed = {"auto", "pc_local_lan_or_tunnel", "remote_secure_link", "drive_fallback"}
        return value if value in allowed else "auto"

    def _redact_share(self, share: Dict[str, Any]) -> Dict[str, Any]:
        safe = dict(share)
        mobile = dict(safe.get("payload_for_mobile") or {})
        if "token" in mobile:
            mobile["token"] = "<returned_once_not_stored>"
        safe["payload_for_mobile"] = mobile
        return safe

    def transfer_plan(
        self,
        direction: str = "phone_to_pc",
        file_label: str = "operator file",
        size_hint_mb: Optional[float] = None,
        purpose: str = "use file in project",
        project_id: str = "GOD_MODE",
    ) -> Dict[str, Any]:
        size = size_hint_mb or 0
        channel = self._best_transfer_channel(direction=direction, size_hint_mb=size)
        plan = {
            "transfer_id": f"file-transfer-plan-{uuid4().hex[:12]}",
            "created_at": self._now_iso(),
            "direction": direction,
            "file_label": file_label[:300],
            "size_hint_mb": size_hint_mb,
            "purpose": purpose[:1000],
            "project_id": project_id.strip().upper().replace("-", "_").replace(" ", "_"),
            "recommended_channel": channel,
            "flow": self._transfer_flow(direction, channel),
            "security": [
                "não guardar tokens Drive/túnel",
                "ficheiro fica associado ao projeto",
                "se for pesado, preferir Drive/manual fallback",
                "se for imagem/preview, gerar miniatura quando possível",
            ],
        }
        self._store("transfers", plan)
        return {"ok": True, "mode": "file_transfer_plan", "plan": plan}

    def _best_transfer_channel(self, direction: str, size_hint_mb: float) -> str:
        if size_hint_mb >= 100:
            return "drive_fallback"
        if direction in {"pc_to_phone", "phone_to_pc"} and size_hint_mb <= 50:
            return "pc_local_lan_or_tunnel"
        return "auto"

    def _transfer_flow(self, direction: str, channel: str) -> List[Dict[str, Any]]:
        if channel == "drive_fallback":
            return [
                {"step": 1, "label": "upload para Drive/manual pelo dispositivo que tem o ficheiro"},
                {"step": 2, "label": "God Mode recebe link/seleção do ficheiro"},
                {"step": 3, "label": "associar ficheiro ao projeto"},
                {"step": 4, "label": "processar/visualizar conforme objetivo"},
            ]
        return [
            {"step": 1, "label": "criar share temporário no lado que tem o ficheiro"},
            {"step": 2, "label": "outro lado baixa pelo túnel/LAN"},
            {"step": 3, "label": "confirmar checksum/receção"},
            {"step": 4, "label": "associar ao job/projeto e continuar"},
        ]

    def intake_request(
        self,
        project_id: str = "GOD_MODE",
        request_text: str = "usar ficheiro recebido no projeto",
        expected_file_type: str = "any",
        preferred_channel: str = "auto",
    ) -> Dict[str, Any]:
        request = {
            "intake_request_id": f"file-intake-request-{uuid4().hex[:12]}",
            "created_at": self._now_iso(),
            "project_id": project_id.strip().upper().replace("-", "_").replace(" ", "_"),
            "request_text": request_text[:2000],
            "expected_file_type": expected_file_type,
            "preferred_channel": self._channel(preferred_channel),
            "operator_message": "Envia o ficheiro pelo APK/túnel se estiver ligado; senão usa Drive/link e o God Mode associa ao projeto.",
            "status": "waiting_for_file",
        }
        self._store("intake_requests", request)
        return {"ok": True, "mode": "file_intake_request", "request": request}

    def latest(self) -> Dict[str, Any]:
        state = DOWNLOAD_CENTER_STORE.load()
        return {
            "ok": True,
            "mode": "download_install_center_latest",
            "latest_package": (state.get("packages") or [None])[-1],
            "latest_share": (state.get("shares") or [None])[-1],
            "latest_transfer": (state.get("transfers") or [None])[-1],
            "latest_intake_request": (state.get("intake_requests") or [None])[-1],
            "package_count": len(state.get("packages") or []),
            "share_count": len(state.get("shares") or []),
            "transfer_count": len(state.get("transfers") or []),
        }

    def panel(self) -> Dict[str, Any]:
        package = self.build_package().get("package")
        apk_update = mobile_apk_update_orchestrator_service.get_status()
        return {
            "ok": True,
            "mode": "download_install_center_v2_panel",
            "headline": "Download e instalação God Mode",
            "package": package,
            "mobile_update_status": apk_update,
            "latest": self.latest(),
            "safe_buttons": [
                {"id": "package", "label": "Ver APK/EXE", "endpoint": "/api/download-install-center-v2/package", "priority": "critical"},
                {"id": "share_apk", "label": "Partilhar APK pelo PC", "endpoint": "/api/download-install-center-v2/share", "priority": "critical"},
                {"id": "transfer", "label": "Plano transferência", "endpoint": "/api/download-install-center-v2/transfer-plan", "priority": "high"},
                {"id": "intake", "label": "Enviar ficheiro para projeto", "endpoint": "/api/download-install-center-v2/intake-request", "priority": "high"},
            ],
        }

    def get_status(self) -> Dict[str, Any]:
        latest = self.latest()
        readiness = final_install_readiness_v2_service.get_status()
        return {
            "ok": True,
            "mode": "download_install_center_v2_status",
            "ready_to_install_real": readiness.get("ready_to_install_real"),
            "readiness_score": readiness.get("score_percent"),
            "artifact_count": len(self.ARTIFACTS),
            "package_count": latest.get("package_count", 0),
            "share_count": latest.get("share_count", 0),
            "preferred_channel": "pc_local_lan_or_tunnel_then_drive_fallback",
        }

    def get_package(self) -> Dict[str, Any]:
        return {"ok": True, "mode": "download_install_center_v2_package", "package": {"status": self.get_status(), "panel": self.panel(), "latest": self.latest()}}

    def _store(self, key: str, value: Dict[str, Any]) -> None:
        def mutate(state: Dict[str, Any]) -> Dict[str, Any]:
            state.setdefault(key, [])
            state[key].append(value)
            state[key] = state[key][-100:]
            return state
        DOWNLOAD_CENTER_STORE.update(mutate)


download_install_center_v2_service = DownloadInstallCenterV2Service()
