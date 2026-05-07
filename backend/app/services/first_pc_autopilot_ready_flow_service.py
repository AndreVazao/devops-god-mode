from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List

from app.services.artifacts_center_service import artifacts_center_service
from app.services.first_pc_install_ready_pack_service import first_pc_install_ready_pack_service
from app.services.first_pc_runtime_verification_service import first_pc_runtime_verification_service
from app.services.god_mode_global_state_service import god_mode_global_state_service
from app.services.god_mode_local_vault_service import god_mode_local_vault_service
from app.services.ia_operator_permission_vault_bridge_service import ia_operator_permission_vault_bridge_service
from app.services.mobile_permission_relay_driver_voice_service import mobile_permission_relay_driver_voice_service


class FirstPcAutopilotReadyFlowService:
    SERVICE_ID = "first_pc_autopilot_ready_flow"
    VERSION = "phase_207_v1"

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def status(self) -> Dict[str, Any]:
        checks = self.readiness_checks()
        return {
            "ok": True,
            "service": self.SERVICE_ID,
            "version": self.VERSION,
            "generated_at": self._now(),
            "ready_score": checks.get("ready_score"),
            "is_today_ready": checks.get("is_today_ready"),
            "canonical_pc_url": "http://127.0.0.1:8000/app/home",
            "today_ready_route": "/app/first-pc-autopilot-ready",
            "first_loop_route": "/app/ia-operator-bridge",
        }

    def readiness_checks(self) -> Dict[str, Any]:
        checks: List[Dict[str, Any]] = []
        checks.append(self._check("global_state", god_mode_global_state_service.status(), "/api/god-mode-global-state/package"))
        checks.append(self._check("install_ready_pack", first_pc_install_ready_pack_service.status(), "/api/first-pc-install-ready-pack/package"))
        checks.append(self._check("runtime_verification", first_pc_runtime_verification_service.status(), "/api/first-pc-runtime-verification/package"))
        checks.append(self._check("artifacts_center", artifacts_center_service.status(), "/api/artifacts-center/status"))
        checks.append(self._check("local_vault", god_mode_local_vault_service.status(), "/api/god-mode-vault/status"))
        checks.append(self._check("permission_relay", mobile_permission_relay_driver_voice_service.status(), "/api/mobile-permission-relay/status"))
        checks.append(self._check("ia_operator_bridge", ia_operator_permission_vault_bridge_service.status(), "/api/ia-operator-bridge/status"))
        passed = sum(1 for item in checks if item.get("ok"))
        score = round((passed / max(1, len(checks))) * 100)
        return {"ok": True, "mode": "first_pc_autopilot_ready_checks", "generated_at": self._now(), "ready_score": score, "is_today_ready": score >= 85, "checks": checks}

    def operator_steps(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "mode": "today_operator_steps",
            "pc_steps": [
                {"step": 1, "title": "Download latest Windows EXE artifact", "route": "/app/artifacts-center", "note": "Usar o artifact Windows EXE mais recente das Actions verdes."},
                {"step": 2, "title": "Run GodModeDesktop.exe", "route": "local", "note": "Abrir no PC de casa. O backend deve arrancar localmente e abrir cockpit."},
                {"step": 3, "title": "Open Home", "route": "http://127.0.0.1:8000/app/home", "note": "Cockpit canónico."},
                {"step": 4, "title": "Open Today Ready", "route": "/app/first-pc-autopilot-ready", "note": "Ver readiness e próximos botões."},
                {"step": 5, "title": "Open Vault Intake", "route": "/app/god-mode-vault", "note": "Colar .env/chaves/URLs que queiras que o God Mode classifique e guarde."},
                {"step": 6, "title": "Start First Autonomous Loop", "route": "/app/ia-operator-bridge", "note": "Iniciar o primeiro ciclo de trabalho autónomo seguro."},
            ],
            "mobile_steps": [
                {"step": 1, "title": "Open Mobile Permission Relay", "route": "/app/mobile-permission-relay", "note": "Receber popups/permissões."},
                {"step": 2, "title": "Use voice when driving", "route": "/app/driver-voice-permissions", "note": "Aprovar/rejeitar/pausar por voz curta quando seguro."},
                {"step": 3, "title": "Fill sensitive values only when stopped", "route": "/app/mobile-permission-relay", "note": "Se pedir credencial, parar em segurança antes de preencher."},
            ],
        }

    def launch_contract(self) -> Dict[str, Any]:
        checks = self.readiness_checks()
        steps = self.operator_steps()
        return {
            "ok": True,
            "mode": "first_pc_autopilot_launch_contract",
            "generated_at": self._now(),
            "ready": checks.get("is_today_ready"),
            "ready_score": checks.get("ready_score"),
            "expected_executable": "GodModeDesktop.exe",
            "canonical_local_url": "http://127.0.0.1:8000/app/home",
            "must_open_routes": [
                "/app/home",
                "/app/first-pc-autopilot-ready",
                "/app/ia-operator-bridge",
                "/app/mobile-permission-relay",
                "/app/god-mode-vault",
            ],
            "one_sentence": "Instala/abre GodModeDesktop.exe no PC, confirma readiness, coloca Vault se necessário e inicia First Autonomous Work Loop.",
            "readiness": checks,
            "steps": steps,
        }

    def start_today_autopilot(self, tenant_id: str = "owner-andre") -> Dict[str, Any]:
        checks = self.readiness_checks()
        if not checks.get("is_today_ready"):
            return {"ok": False, "mode": "start_today_autopilot", "error": "readiness_below_threshold", "readiness": checks}
        loop = ia_operator_permission_vault_bridge_service.start_first_autonomous_work_loop(tenant_id=tenant_id)
        return {"ok": True, "mode": "start_today_autopilot", "readiness": checks, "first_loop": loop}

    def package(self) -> Dict[str, Any]:
        return {"status": self.status(), "readiness": self.readiness_checks(), "steps": self.operator_steps(), "launch_contract": self.launch_contract()}

    def _check(self, name: str, payload: Dict[str, Any], route: str) -> Dict[str, Any]:
        return {"name": name, "ok": bool(payload.get("ok", True)), "route": route, "version": payload.get("version"), "summary": {key: payload.get(key) for key in ["service", "ready_score", "is_today_ready", "current_phase", "latest_merged_phase"] if key in payload}}


first_pc_autopilot_ready_flow_service = FirstPcAutopilotReadyFlowService()
