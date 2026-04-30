from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, List
from uuid import uuid4

from app.utils.atomic_json_store import AtomicJsonStore

DATA_DIR = Path("data")
RC_FILE = DATA_DIR / "release_candidate_handoff.json"
RC_STORE = AtomicJsonStore(
    RC_FILE,
    default_factory=lambda: {
        "version": 1,
        "policy": "single_release_candidate_handoff_for_first_real_install",
        "handoffs": [],
    },
)


class ReleaseCandidateHandoffService:
    """Final release-candidate handoff before real installation.

    This service gives the operator a single install-ready package summary:
    version, commit, expected artifacts, required checks, first-run checklist and
    rollback policy.
    """

    ARTIFACTS = [
        {
            "id": "windows_exe",
            "label": "God Mode Desktop EXE",
            "artifact_name": "godmode-windows-exe",
            "expected_file": "GodModeDesktop.exe",
            "workflow": "windows-exe-real-build.yml",
            "target": "PC Windows",
        },
        {
            "id": "android_apk",
            "label": "God Mode Mobile APK",
            "artifact_name": "godmode-android-webview-apk",
            "expected_file": "GodModeMobile-debug.apk",
            "workflow": "android-real-build-progressive.yml",
            "target": "Android",
        },
    ]

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def _safe(self, label: str, fn: Callable[[], Dict[str, Any]]) -> Dict[str, Any]:
        try:
            value = fn()
            return value if isinstance(value, dict) else {"ok": True, "value": value}
        except Exception as exc:
            return {"ok": False, "mode": label, "error": exc.__class__.__name__, "detail": str(exc)[:400]}

    def build_handoff(
        self,
        version_label: str = "RC1",
        commit_sha: str = "b7f6174a7bd1c735534f9c4cdc9fce187402cb96",
        install_mode: str = "first_real_controlled_install",
    ) -> Dict[str, Any]:
        readiness = self._safe("final_readiness", lambda: __import__("app.services.final_install_readiness_v2_service", fromlist=["final_install_readiness_v2_service"]).final_install_readiness_v2_service.get_status())
        download = self._safe("download_center", lambda: __import__("app.services.download_install_center_v2_service", fromlist=["download_install_center_v2_service"]).download_install_center_v2_service.get_status())
        launch = self._safe("home_launch", lambda: __import__("app.services.home_launch_command_center_service", fromlist=["home_launch_command_center_service"]).home_launch_command_center_service.get_status())
        first_run = self._safe("first_real_run", lambda: __import__("app.services.first_real_run_checklist_service", fromlist=["first_real_run_checklist_service"]).first_real_run_checklist_service.get_status())
        smoke = self._safe("smoke_test", lambda: __import__("app.services.real_install_smoke_test_service", fromlist=["real_install_smoke_test_service"]).real_install_smoke_test_service.get_status())
        blockers = self._blockers([readiness, download, launch, smoke])
        handoff = {
            "handoff_id": f"rc-handoff-{uuid4().hex[:12]}",
            "created_at": self._now(),
            "version_label": version_label,
            "commit_sha": commit_sha,
            "install_mode": install_mode,
            "ready_for_first_real_install": not blockers and bool(readiness.get("ready_to_install_real", False)),
            "status_label": self._status_label(readiness, blockers),
            "artifacts": self.ARTIFACTS,
            "checks": {
                "final_readiness": readiness,
                "download_center": download,
                "home_launch": launch,
                "first_real_run": first_run,
                "smoke_test": smoke,
            },
            "blockers": blockers,
            "operator_steps": self._operator_steps(),
            "rollback_policy": self._rollback_policy(),
            "do_not_forget": [
                "Instala primeiro o EXE no PC.",
                "Depois instala o APK no telemóvel.",
                "Emparelha APK ao PC antes de dar ordens reais.",
                "Corre a checklist first-real-run antes de uso diário.",
                "Não coloques credenciais no chat normal.",
            ],
            "next_endpoint": "/api/first-real-run/panel" if not blockers else "/api/final-install-readiness-v2/check",
        }
        self._store(handoff)
        return {"ok": True, "mode": "release_candidate_handoff", "handoff": handoff}

    def _blockers(self, statuses: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        blockers: List[Dict[str, Any]] = []
        for status in statuses:
            if not status.get("ok", False):
                blockers.append({"mode": status.get("mode"), "reason": status.get("error") or "not_ok"})
        return blockers

    def _status_label(self, readiness: Dict[str, Any], blockers: List[Dict[str, Any]]) -> str:
        if blockers:
            return "blocked_before_install"
        if readiness.get("ready_to_install_real"):
            return "install_candidate_ready"
        return "candidate_needs_gate_confirmation"

    def _operator_steps(self) -> List[Dict[str, Any]]:
        return [
            {"step": 1, "label": "Abrir GitHub Actions e baixar artifacts", "artifacts": [a["artifact_name"] for a in self.ARTIFACTS]},
            {"step": 2, "label": "Extrair/abrir bundle do EXE no PC", "expected_file": "GodModeDesktop.exe"},
            {"step": 3, "label": "Executar GodModeDesktop.exe", "expected": "backend online"},
            {"step": 4, "label": "Instalar GodModeMobile-debug.apk", "expected": "APK abre"},
            {"step": 5, "label": "Emparelhar APK ao PC", "endpoint": "/api/apk-pc-pairing/panel"},
            {"step": 6, "label": "Abrir Modo Fácil", "endpoint": "/api/home-operator-ux/panel"},
            {"step": 7, "label": "Executar checklist first-real-run", "endpoint": "/api/first-real-run/panel"},
            {"step": 8, "label": "Dar primeiro comando real curto", "example": "continua o projeto GOD_MODE e para se precisares do meu OK"},
        ]

    def _rollback_policy(self) -> Dict[str, Any]:
        return {
            "if_pc_update_fails": "usar /api/self-update/rollback se existir backup; caso contrário manter bundle anterior",
            "if_apk_update_fails": "reinstalar APK anterior mantendo mesmo package id quando possível",
            "preserve_paths": ["data/", "memory/", ".env", "backend/.env"],
            "never_delete": ["data", "memory", "local project state", "operator files"],
        }

    def _store(self, handoff: Dict[str, Any]) -> None:
        def mutate(state: Dict[str, Any]) -> Dict[str, Any]:
            state.setdefault("handoffs", [])
            state["handoffs"].append(handoff)
            state["handoffs"] = state["handoffs"][-100:]
            return state
        RC_STORE.update(mutate)

    def latest(self) -> Dict[str, Any]:
        handoffs = RC_STORE.load().get("handoffs") or []
        return {"ok": True, "mode": "release_candidate_latest", "latest_handoff": handoffs[-1] if handoffs else None, "handoff_count": len(handoffs)}

    def panel(self) -> Dict[str, Any]:
        handoff = self.build_handoff().get("handoff")
        return {
            "ok": True,
            "mode": "release_candidate_panel",
            "headline": "Versão candidata para instalação real",
            "handoff": handoff,
            "safe_buttons": [
                {"id": "build", "label": "Gerar handoff RC", "endpoint": "/api/release-candidate-handoff/build", "priority": "critical"},
                {"id": "download", "label": "Baixar APK/EXE", "endpoint": "/api/download-install-center-v2/panel", "priority": "critical"},
                {"id": "first_run", "label": "Primeira execução", "endpoint": "/api/first-real-run/panel", "priority": "critical"},
            ],
        }

    def get_status(self) -> Dict[str, Any]:
        latest = self.latest().get("latest_handoff")
        if not latest:
            latest = self.build_handoff().get("handoff")
        return {
            "ok": True,
            "mode": "release_candidate_status",
            "version_label": latest.get("version_label"),
            "commit_sha": latest.get("commit_sha"),
            "ready_for_first_real_install": latest.get("ready_for_first_real_install"),
            "status_label": latest.get("status_label"),
            "blocker_count": len(latest.get("blockers") or []),
        }

    def get_package(self) -> Dict[str, Any]:
        return {"ok": True, "mode": "release_candidate_package", "package": {"status": self.get_status(), "panel": self.panel(), "latest": self.latest()}}


release_candidate_handoff_service = ReleaseCandidateHandoffService()
