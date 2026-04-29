from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import uuid4

from app.utils.atomic_json_store import AtomicJsonStore

DATA_DIR = Path("data")
MOBILE_UPDATE_FILE = DATA_DIR / "mobile_apk_update_orchestrator.json"
MOBILE_UPDATE_STORE = AtomicJsonStore(
    MOBILE_UPDATE_FILE,
    default_factory=lambda: {
        "version": 1,
        "policy": "mobile_apk_updates_use_backend_only_prompt_or_adb_authorized_install",
        "plans": [],
        "handoffs": [],
        "adb_scripts": [],
        "results": [],
    },
)


class MobileApkUpdateOrchestratorService:
    """Mobile APK update orchestration.

    Android normally does not allow a regular APK to silently uninstall/install
    another APK or itself. The supported safe modes are:
    - backend_only: no APK reinstall required;
    - apk_prompt_install: APK downloads/open Package Installer and operator taps install;
    - pc_adb_assisted: PC installs with adb install -r after debugging authorization;
    - device_owner_future: enterprise/kiosk path for managed devices.
    """

    APPROVAL_PHRASE = "UPDATE MOBILE APK"
    ADB_APPROVAL_PHRASE = "ADB UPDATE APK"
    DEFAULT_PACKAGE_ID = "com.godmode.mobile"

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def _sha(self, value: str) -> str:
        return hashlib.sha256(value.encode("utf-8")).hexdigest()

    def policy(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "mode": "mobile_apk_update_policy",
            "hard_truth": "um APK normal não pode instalar/desinstalar APKs em silêncio sem ADB, Device Owner/MDM, root ou permissão privilegiada",
            "supported_modes": [
                {
                    "id": "backend_only",
                    "label": "Atualização sem reinstalar APK",
                    "description": "backend/frontend servido pelo PC muda; APK WebView continua igual",
                    "operator_tap_required": False,
                    "preserves_app_data": True,
                },
                {
                    "id": "apk_prompt_install",
                    "label": "APK pede instalação",
                    "description": "APK baixa/recebe artifact e abre instalador Android; operador toca Instalar",
                    "operator_tap_required": True,
                    "preserves_app_data": "sim, se package id e assinatura forem iguais e instalar por cima",
                },
                {
                    "id": "pc_adb_assisted",
                    "label": "PC instala via ADB autorizado",
                    "description": "PC envia e executa adb install -r para atualizar mantendo dados",
                    "operator_tap_required": "só autorização inicial USB/Wi-Fi debugging",
                    "preserves_app_data": True,
                },
                {
                    "id": "device_owner_future",
                    "label": "Device Owner/MDM futuro",
                    "description": "instalação mais silenciosa em dispositivos geridos/kiosk",
                    "operator_tap_required": "configuração inicial avançada",
                    "preserves_app_data": True,
                },
            ],
            "preserve_rules": [
                "usar o mesmo applicationId/package id",
                "usar a mesma assinatura/certificado",
                "preferir install-over-existing; não desinstalar antes",
                "ADB deve usar adb install -r",
                "não limpar dados do APK sem aprovação explícita",
            ],
            "approval_phrase": self.APPROVAL_PHRASE,
            "adb_approval_phrase": self.ADB_APPROVAL_PHRASE,
        }

    def create_plan(
        self,
        current_apk_version: str = "unknown",
        target_apk_version: str = "latest",
        package_id: str = DEFAULT_PACKAGE_ID,
        update_kind: str = "backend_only",
        apk_artifact_name: str = "GodModeMobile-debug.apk",
        apk_download_url: Optional[str] = None,
        target_commit: str = "unknown",
    ) -> Dict[str, Any]:
        normalized_kind = self._normalize_kind(update_kind)
        plan = {
            "plan_id": f"mobile-apk-update-plan-{uuid4().hex[:12]}",
            "created_at": self._now(),
            "current_apk_version": current_apk_version,
            "target_apk_version": target_apk_version,
            "target_commit": target_commit,
            "package_id": package_id,
            "update_kind": normalized_kind,
            "apk_artifact_name": apk_artifact_name,
            "apk_download_url": apk_download_url,
            "operator_required": self._operator_required(normalized_kind),
            "recommended_flow": self._flow(normalized_kind),
            "preserve_app_data_strategy": self._preserve_strategy(normalized_kind),
            "approval_phrase": self.APPROVAL_PHRASE if normalized_kind != "backend_only" else None,
            "safe_to_auto_apply": normalized_kind == "backend_only",
            "status": "planned",
        }
        self._store("plans", plan)
        return {"ok": True, "mode": "mobile_apk_update_plan", "plan": plan}

    def _normalize_kind(self, update_kind: str) -> str:
        value = (update_kind or "backend_only").strip().lower().replace(" ", "_")
        allowed = {"backend_only", "apk_prompt_install", "pc_adb_assisted", "device_owner_future"}
        return value if value in allowed else "apk_prompt_install"

    def _operator_required(self, kind: str) -> Any:
        if kind == "backend_only":
            return False
        if kind == "pc_adb_assisted":
            return "ADB authorization required first time"
        return True

    def _flow(self, kind: str) -> List[Dict[str, Any]]:
        if kind == "backend_only":
            return [
                {"step": 1, "label": "Atualizar backend/frontend servido pelo PC"},
                {"step": 2, "label": "APK mantém WebView e reconecta"},
                {"step": 3, "label": "Rodar heartbeat e Home smoke test"},
            ]
        if kind == "pc_adb_assisted":
            return [
                {"step": 1, "label": "PC descarrega artifact APK"},
                {"step": 2, "label": "Confirmar telefone ligado/autorizado por ADB"},
                {"step": 3, "label": "Executar adb install -r GodModeMobile-debug.apk"},
                {"step": 4, "label": "Abrir app/heartbeat/pairing"},
                {"step": 5, "label": "Rodar smoke test local"},
            ]
        if kind == "device_owner_future":
            return [
                {"step": 1, "label": "Validar dispositivo gerido/Device Owner"},
                {"step": 2, "label": "Instalar APK por policy/device owner"},
                {"step": 3, "label": "Rodar smoke test"},
            ]
        return [
            {"step": 1, "label": "APK/PC descarrega artifact APK"},
            {"step": 2, "label": "APK abre Package Installer"},
            {"step": 3, "label": "Operador toca Instalar"},
            {"step": 4, "label": "App abre novamente e faz heartbeat"},
            {"step": 5, "label": "Rodar smoke test local"},
        ]

    def _preserve_strategy(self, kind: str) -> Dict[str, Any]:
        return {
            "same_package_id_required": True,
            "same_signing_key_required": True,
            "do_not_uninstall_first": True,
            "install_over_existing": True,
            "adb_command": "adb install -r <apk>" if kind == "pc_adb_assisted" else None,
            "app_data_preserved": kind in {"backend_only", "pc_adb_assisted", "apk_prompt_install", "device_owner_future"},
            "warning": "uninstall/install normally clears app data; prefer update-over-existing",
        }

    def prepare_handoff(self, plan_id: str, approval_phrase: str = "") -> Dict[str, Any]:
        plan = self._find("plans", plan_id, "plan_id")
        if not plan:
            return {"ok": False, "mode": "mobile_apk_update_handoff", "error": "plan_not_found"}
        if plan.get("update_kind") != "backend_only" and approval_phrase != self.APPROVAL_PHRASE:
            return {"ok": False, "mode": "mobile_apk_update_handoff", "error": "approval_phrase_required", "required_phrase": self.APPROVAL_PHRASE}
        handoff = {
            "handoff_id": f"mobile-update-handoff-{uuid4().hex[:12]}",
            "created_at": self._now(),
            "plan_id": plan_id,
            "update_kind": plan.get("update_kind"),
            "package_id": plan.get("package_id"),
            "apk_artifact_name": plan.get("apk_artifact_name"),
            "apk_download_url": plan.get("apk_download_url"),
            "target_apk_version": plan.get("target_apk_version"),
            "payload_for_apk": self._payload_for_apk(plan),
            "payload_for_pc": self._payload_for_pc(plan),
            "status": "ready_for_execution",
        }
        self._store("handoffs", handoff)
        return {"ok": True, "mode": "mobile_apk_update_handoff", "handoff": handoff}

    def _payload_for_apk(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "kind": "god_mode_mobile_update",
            "update_kind": plan.get("update_kind"),
            "target_version": plan.get("target_apk_version"),
            "apk_download_url": plan.get("apk_download_url"),
            "package_id": plan.get("package_id"),
            "open_package_installer": plan.get("update_kind") == "apk_prompt_install",
            "message": self._apk_message(plan.get("update_kind")),
        }

    def _payload_for_pc(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "kind": "god_mode_pc_mobile_update",
            "update_kind": plan.get("update_kind"),
            "apk_artifact_name": plan.get("apk_artifact_name"),
            "adb_allowed": plan.get("update_kind") == "pc_adb_assisted",
            "adb_script_endpoint": "/api/mobile-apk-update/adb-script",
        }

    def _apk_message(self, kind: str) -> str:
        if kind == "backend_only":
            return "Atualização do PC/backend pronta; APK só precisa reconectar."
        if kind == "pc_adb_assisted":
            return "PC vai tentar atualizar por ADB autorizado. Mantém o telemóvel ligado/autorizado."
        if kind == "device_owner_future":
            return "Atualização por modo gerido futuro."
        return "Há novo APK. Toca em instalar quando o instalador Android abrir."

    def adb_script(self, plan_id: str, local_apk_path: Optional[str] = None, adb_approval_phrase: str = "") -> Dict[str, Any]:
        if adb_approval_phrase != self.ADB_APPROVAL_PHRASE:
            return {"ok": False, "mode": "mobile_apk_adb_script", "error": "adb_approval_phrase_required", "required_phrase": self.ADB_APPROVAL_PHRASE}
        plan = self._find("plans", plan_id, "plan_id")
        if not plan:
            return {"ok": False, "mode": "mobile_apk_adb_script", "error": "plan_not_found"}
        if plan.get("update_kind") != "pc_adb_assisted":
            return {"ok": False, "mode": "mobile_apk_adb_script", "error": "plan_not_adb_assisted"}
        apk_path = local_apk_path or plan.get("apk_artifact_name") or "GodModeMobile-debug.apk"
        script = self._build_adb_script(apk_path, plan.get("package_id") or self.DEFAULT_PACKAGE_ID)
        record = {
            "script_id": f"mobile-adb-script-{uuid4().hex[:12]}",
            "created_at": self._now(),
            "plan_id": plan_id,
            "apk_path": apk_path,
            "package_id": plan.get("package_id"),
            "script": script,
            "script_sha256": self._sha(script),
        }
        self._store("adb_scripts", record)
        return {"ok": True, "mode": "mobile_apk_adb_script", "script": record}

    def _build_adb_script(self, apk_path: str, package_id: str) -> str:
        return "\n".join([
            "$ErrorActionPreference = 'Stop'",
            "Write-Host 'God Mode Mobile APK ADB Update'",
            "if (-not (Get-Command adb -ErrorAction SilentlyContinue)) { throw 'ADB not found. Install Android platform-tools first.' }",
            "adb devices",
            f"Write-Host 'Installing over existing package: {package_id}'",
            f"adb install -r \"{apk_path}\"",
            f"adb shell monkey -p {package_id} 1",
            "Write-Host 'APK update attempted. Check app heartbeat/pairing.'",
        ]) + "\n"

    def record_result(
        self,
        plan_id: str,
        status: str = "unknown",
        detail: str = "",
        apk_version_after: Optional[str] = None,
        heartbeat_ok: bool = False,
    ) -> Dict[str, Any]:
        result = {
            "result_id": f"mobile-update-result-{uuid4().hex[:12]}",
            "created_at": self._now(),
            "plan_id": plan_id,
            "status": status,
            "detail": detail[:2000],
            "apk_version_after": apk_version_after,
            "heartbeat_ok": heartbeat_ok,
            "ok": status in {"completed", "backend_only_completed", "adb_completed", "prompt_install_completed"} and bool(heartbeat_ok),
        }
        self._store("results", result)
        return {"ok": True, "mode": "mobile_apk_update_result", "result": result}

    def _find(self, key: str, value: str, id_key: str) -> Optional[Dict[str, Any]]:
        items = MOBILE_UPDATE_STORE.load().get(key, [])
        return next((item for item in items if item.get(id_key) == value), None)

    def _store(self, key: str, value: Dict[str, Any]) -> None:
        def mutate(state: Dict[str, Any]) -> Dict[str, Any]:
            state.setdefault(key, [])
            state[key].append(value)
            state[key] = state[key][-100:]
            return state
        MOBILE_UPDATE_STORE.update(mutate)

    def latest(self) -> Dict[str, Any]:
        state = MOBILE_UPDATE_STORE.load()
        return {
            "ok": True,
            "mode": "mobile_apk_update_latest",
            "latest_plan": (state.get("plans") or [None])[-1],
            "latest_handoff": (state.get("handoffs") or [None])[-1],
            "latest_adb_script": (state.get("adb_scripts") or [None])[-1],
            "latest_result": (state.get("results") or [None])[-1],
            "plan_count": len(state.get("plans") or []),
            "result_count": len(state.get("results") or []),
        }

    def panel(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "mode": "mobile_apk_update_panel",
            "headline": "Atualização do APK pelo PC/backend",
            "policy": self.policy(),
            "latest": self.latest(),
            "safe_buttons": [
                {"id": "plan", "label": "Plano update APK", "endpoint": "/api/mobile-apk-update/plan", "priority": "critical"},
                {"id": "handoff", "label": "Preparar envio APK", "endpoint": "/api/mobile-apk-update/handoff", "priority": "critical"},
                {"id": "adb", "label": "Script ADB", "endpoint": "/api/mobile-apk-update/adb-script", "priority": "high"},
                {"id": "result", "label": "Registar resultado", "endpoint": "/api/mobile-apk-update/record-result", "priority": "high"},
            ],
        }

    def get_status(self) -> Dict[str, Any]:
        latest = self.latest()
        return {
            "ok": True,
            "mode": "mobile_apk_update_status",
            "plan_count": latest.get("plan_count", 0),
            "result_count": latest.get("result_count", 0),
            "silent_install_possible_for_normal_apk": False,
            "best_automation_mode": "pc_adb_assisted_when_phone_authorized",
            "backend_only_updates_need_apk_reinstall": False,
        }

    def get_package(self) -> Dict[str, Any]:
        return {"ok": True, "mode": "mobile_apk_update_package", "package": {"status": self.get_status(), "panel": self.panel(), "latest": self.latest()}}


mobile_apk_update_orchestrator_service = MobileApkUpdateOrchestratorService()
