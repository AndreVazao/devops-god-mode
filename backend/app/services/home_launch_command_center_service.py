from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, List
from uuid import uuid4

from app.utils.atomic_json_store import AtomicJsonStore

DATA_DIR = Path("data")
LAUNCH_FILE = DATA_DIR / "home_launch_command_center.json"
LAUNCH_STORE = AtomicJsonStore(
    LAUNCH_FILE,
    default_factory=lambda: {
        "version": 1,
        "policy": "single_home_entrypoint_for_install_download_pairing_and_first_real_use",
        "snapshots": [],
    },
)


class HomeLaunchCommandCenterService:
    """One Home entrypoint for installing and first real use.

    This service turns the final readiness and download/install flow into a
    mobile-first command center. It avoids hiding the final install path in
    technical endpoints.
    """

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def _safe(self, label: str, fn: Callable[[], Dict[str, Any]]) -> Dict[str, Any]:
        try:
            value = fn()
            return value if isinstance(value, dict) else {"ok": True, "value": value}
        except Exception as exc:
            return {"ok": False, "mode": label, "error": exc.__class__.__name__, "detail": str(exc)[:400]}

    def snapshot(self) -> Dict[str, Any]:
        readiness = self._safe("final_readiness", lambda: __import__("app.services.final_install_readiness_v2_service", fromlist=["final_install_readiness_v2_service"]).final_install_readiness_v2_service.get_status())
        downloads = self._safe("download_center", lambda: __import__("app.services.download_install_center_v2_service", fromlist=["download_install_center_v2_service"]).download_install_center_v2_service.get_status())
        pairing = self._safe("apk_pc_pairing", lambda: __import__("app.services.apk_pc_pairing_wizard_service", fromlist=["apk_pc_pairing_wizard_service"]).apk_pc_pairing_wizard_service.get_status())
        smoke = self._safe("real_install_smoke", lambda: __import__("app.services.real_install_smoke_test_service", fromlist=["real_install_smoke_test_service"]).real_install_smoke_test_service.get_status())
        self_update = self._safe("self_update", lambda: __import__("app.services.self_update_manager_service", fromlist=["self_update_manager_service"]).self_update_manager_service.get_status())
        mobile_update = self._safe("mobile_update", lambda: __import__("app.services.mobile_apk_update_orchestrator_service", fromlist=["mobile_apk_update_orchestrator_service"]).mobile_apk_update_orchestrator_service.get_status())
        registry = self._safe("project_registry", lambda: __import__("app.services.project_memory_registry_service", fromlist=["project_memory_registry_service"]).project_memory_registry_service.get_status())
        snapshot = {
            "snapshot_id": f"home-launch-{uuid4().hex[:12]}",
            "created_at": self._now(),
            "mode": "home_launch_command_center_snapshot",
            "headline": self._headline(readiness),
            "overall": self._overall(readiness, downloads, pairing, smoke, self_update, mobile_update, registry),
            "cards": [
                self._card("final_readiness", "Pronto para instalar?", "/api/final-install-readiness-v2/check", readiness, "critical"),
                self._card("download_install", "Baixar APK/EXE", "/api/download-install-center-v2/panel", downloads, "critical"),
                self._card("apk_pc_pairing", "Emparelhar APK ao PC", "/api/apk-pc-pairing/panel", pairing, "critical"),
                self._card("smoke_test", "Smoke test seguro", "/api/real-install-smoke-test/ci-safe", smoke, "critical"),
                self._card("self_update", "Atualização PC", "/api/self-update/panel", self_update, "high"),
                self._card("mobile_update", "Atualização APK", "/api/mobile-apk-update/panel", mobile_update, "high"),
                self._card("project_registry", "Projetos/memória", "/api/project-memory-registry/panel", registry, "high"),
                {
                    "id": "file_transfer",
                    "label": "Enviar ficheiro",
                    "endpoint": "/api/download-install-center-v2/intake-request",
                    "priority": "high",
                    "traffic_light": {"color": "green", "label": "pronto", "reason": "intake_available"},
                    "status": {"ok": True, "mode": "file_intake_ready"},
                },
            ],
            "primary_action": self._primary_action(readiness),
            "install_path": [
                {"step": 1, "label": "Verificar pronto para instalar", "endpoint": "/api/final-install-readiness-v2/check"},
                {"step": 2, "label": "Baixar EXE/APK", "endpoint": "/api/download-install-center-v2/panel"},
                {"step": 3, "label": "Abrir EXE no PC", "expected": "backend online"},
                {"step": 4, "label": "Emparelhar telemóvel", "endpoint": "/api/apk-pc-pairing/panel"},
                {"step": 5, "label": "Abrir Modo Fácil", "endpoint": "/api/home-operator-ux/panel"},
                {"step": 6, "label": "Fazer primeiro comando real", "endpoint": "/api/home-critical-actions/panel"},
            ],
            "operator_message": self._operator_message(readiness),
        }
        self._store(snapshot)
        return {"ok": True, "mode": "home_launch_command_center", "snapshot": snapshot}

    def _headline(self, readiness: Dict[str, Any]) -> str:
        if readiness.get("ready_to_install_real"):
            return "God Mode pronto para instalação controlada"
        score = readiness.get("score_percent")
        return f"God Mode quase pronto · gate {score}%" if score is not None else "Preparar instalação God Mode"

    def _overall(self, *statuses: Dict[str, Any]) -> Dict[str, Any]:
        red = len([s for s in statuses if not s.get("ok", False)])
        ready = statuses[0].get("ready_to_install_real") if statuses else False
        if red:
            return {"color": "red", "label": "há módulos com erro", "red": red}
        if ready:
            return {"color": "green", "label": "pronto para instalar/testar", "red": 0}
        return {"color": "yellow", "label": "sem erro crítico, confirmar gate final", "red": 0}

    def _card(self, card_id: str, label: str, endpoint: str, status: Dict[str, Any], priority: str) -> Dict[str, Any]:
        ok = bool(status.get("ok", False))
        color = "green" if ok else "red"
        if card_id == "final_readiness" and ok and status.get("ready_to_install_real") is not True:
            color = "yellow"
        return {
            "id": card_id,
            "label": label,
            "endpoint": endpoint,
            "priority": priority,
            "traffic_light": {"color": color, "label": self._light_label(card_id, status, ok), "reason": status.get("mode") or "status"},
            "status": status,
        }

    def _light_label(self, card_id: str, status: Dict[str, Any], ok: bool) -> str:
        if not ok:
            return "erro"
        if card_id == "final_readiness":
            if status.get("ready_to_install_real"):
                return "instalar"
            score = status.get("score_percent")
            return f"{score}%" if score is not None else "verificar"
        return "ok"

    def _primary_action(self, readiness: Dict[str, Any]) -> Dict[str, Any]:
        if readiness.get("ready_to_install_real"):
            return {"label": "Baixar e instalar", "endpoint": "/api/download-install-center-v2/panel", "priority": "critical"}
        return {"label": "Verificar gate final", "endpoint": "/api/final-install-readiness-v2/check", "priority": "critical"}

    def _operator_message(self, readiness: Dict[str, Any]) -> str:
        if readiness.get("ready_to_install_real"):
            return "Pode avançar para download/instalação controlada. Primeiro instala EXE no PC, depois APK no telemóvel e emparelha."
        return "Ainda não assumas uso diário. Corre o gate final e corrige blockers antes de instalar como versão de trabalho."

    def _store(self, snapshot: Dict[str, Any]) -> None:
        def mutate(state: Dict[str, Any]) -> Dict[str, Any]:
            state.setdefault("snapshots", [])
            state["snapshots"].append(snapshot)
            state["snapshots"] = state["snapshots"][-100:]
            return state
        LAUNCH_STORE.update(mutate)

    def latest(self) -> Dict[str, Any]:
        snapshots = LAUNCH_STORE.load().get("snapshots") or []
        return {"ok": True, "mode": "home_launch_latest", "latest_snapshot": snapshots[-1] if snapshots else None, "snapshot_count": len(snapshots)}

    def get_status(self) -> Dict[str, Any]:
        latest = self.latest().get("latest_snapshot")
        if not latest:
            latest = self.snapshot().get("snapshot")
        return {
            "ok": True,
            "mode": "home_launch_status",
            "headline": latest.get("headline"),
            "overall": latest.get("overall"),
            "primary_action": latest.get("primary_action"),
            "card_count": len(latest.get("cards") or []),
        }

    def get_package(self) -> Dict[str, Any]:
        return {"ok": True, "mode": "home_launch_package", "package": {"status": self.get_status(), "panel": self.snapshot(), "latest": self.latest()}}


home_launch_command_center_service = HomeLaunchCommandCenterService()
