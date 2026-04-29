from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import uuid4

from app.utils.atomic_json_store import AtomicJsonStore

DATA_DIR = Path("data")
FIRST_RUN_FILE = DATA_DIR / "first_real_run_checklist.json"
FIRST_RUN_STORE = AtomicJsonStore(
    FIRST_RUN_FILE,
    default_factory=lambda: {
        "version": 1,
        "policy": "operator_first_real_run_checklist_before_daily_use",
        "sessions": [],
        "step_results": [],
        "completions": [],
    },
)


class FirstRealRunChecklistService:
    """Operator checklist for the first real God Mode installation/run."""

    STEPS = [
        {"step_id": "gate_final", "order": 1, "label": "Confirmar gate final verde", "endpoint": "/api/final-install-readiness-v2/check", "required": True},
        {"step_id": "download_exe_apk", "order": 2, "label": "Baixar EXE e APK", "endpoint": "/api/download-install-center-v2/panel", "required": True},
        {"step_id": "run_pc_exe", "order": 3, "label": "Executar GodModeDesktop.exe no PC", "endpoint": "/api/home-launch/panel", "required": True},
        {"step_id": "install_apk", "order": 4, "label": "Instalar/abrir APK no telemóvel", "endpoint": "/api/mobile-apk-update/policy", "required": True},
        {"step_id": "pair_apk_pc", "order": 5, "label": "Emparelhar APK ao PC", "endpoint": "/api/apk-pc-pairing/panel", "required": True},
        {"step_id": "open_easy_mode", "order": 6, "label": "Abrir Home / Modo Fácil", "endpoint": "/api/home-operator-ux/panel", "required": True},
        {"step_id": "run_local_smoke", "order": 7, "label": "Rodar smoke local de primeira execução", "endpoint": "/api/real-install-smoke-test/local-contract", "required": True},
        {"step_id": "test_file_transfer", "order": 8, "label": "Testar envio/receção de ficheiro pequeno", "endpoint": "/api/download-install-center-v2/intake-request", "required": False},
        {"step_id": "create_first_real_job", "order": 9, "label": "Criar primeiro job real controlado", "endpoint": "/api/resumable-jobs/create", "required": True},
        {"step_id": "first_operator_command", "order": 10, "label": "Dar primeiro comando real curto", "endpoint": "/api/daily-command-router/route", "required": True},
        {"step_id": "confirm_daily_ready", "order": 11, "label": "Confirmar pronto para uso diário", "endpoint": "/api/first-real-run/complete", "required": True},
    ]

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def start(self, operator: str = "Andre", target_pc: str = "primary_pc", target_phone: str = "android_phone") -> Dict[str, Any]:
        session = {
            "session_id": f"first-real-run-{uuid4().hex[:12]}",
            "created_at": self._now(),
            "operator": operator,
            "target_pc": target_pc,
            "target_phone": target_phone,
            "status": "in_progress",
            "required_step_count": len([s for s in self.STEPS if s.get("required")]),
            "total_step_count": len(self.STEPS),
            "steps": self.STEPS,
            "current_step": self.STEPS[0]["step_id"],
        }
        self._store("sessions", session)
        return {"ok": True, "mode": "first_real_run_started", "session": session}

    def record_step(self, session_id: str, step_id: str, ok: bool, detail: str = "", evidence: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        session = self._find_session(session_id)
        if not session:
            return {"ok": False, "mode": "first_real_run_step", "error": "session_not_found"}
        step = next((item for item in self.STEPS if item["step_id"] == step_id), None)
        if not step:
            return {"ok": False, "mode": "first_real_run_step", "error": "step_not_found"}
        result = {
            "result_id": f"first-run-step-{uuid4().hex[:12]}",
            "created_at": self._now(),
            "session_id": session_id,
            "step_id": step_id,
            "step_label": step.get("label"),
            "required": step.get("required"),
            "ok": bool(ok),
            "detail": detail[:2000],
            "evidence": self._safe_evidence(evidence or {}),
        }
        self._store("step_results", result)
        self._advance_session(session_id)
        return {"ok": True, "mode": "first_real_run_step_recorded", "result": result, "progress": self.progress(session_id).get("progress")}

    def progress(self, session_id: str) -> Dict[str, Any]:
        session = self._find_session(session_id)
        if not session:
            return {"ok": False, "mode": "first_real_run_progress", "error": "session_not_found"}
        results = self._results_for_session(session_id)
        latest_by_step = {r["step_id"]: r for r in results}
        step_status = []
        blockers = []
        for step in self.STEPS:
            result = latest_by_step.get(step["step_id"])
            status = "pending" if result is None else ("passed" if result.get("ok") else "failed")
            item = {**step, "status": status, "result": result}
            step_status.append(item)
            if step.get("required") and result is not None and not result.get("ok"):
                blockers.append(item)
        required_steps = [s for s in self.STEPS if s.get("required")]
        passed_required = len([s for s in required_steps if latest_by_step.get(s["step_id"], {}).get("ok") is True])
        progress = {
            "session_id": session_id,
            "status": session.get("status"),
            "required_passed": passed_required,
            "required_total": len(required_steps),
            "total_steps": len(self.STEPS),
            "percent": round((passed_required / max(1, len(required_steps))) * 100),
            "ready_for_daily_use": passed_required == len(required_steps) and not blockers,
            "blockers": blockers,
            "steps": step_status,
            "next_step": self._next_step(step_status),
        }
        return {"ok": True, "mode": "first_real_run_progress", "progress": progress}

    def complete(self, session_id: str, operator_ok: bool = False) -> Dict[str, Any]:
        progress_result = self.progress(session_id)
        if not progress_result.get("ok"):
            return progress_result
        progress = progress_result.get("progress") or {}
        if not progress.get("ready_for_daily_use") and not operator_ok:
            return {"ok": False, "mode": "first_real_run_complete", "error": "required_steps_not_complete", "progress": progress}
        completion = {
            "completion_id": f"first-real-run-completion-{uuid4().hex[:12]}",
            "created_at": self._now(),
            "session_id": session_id,
            "ready_for_daily_use": bool(progress.get("ready_for_daily_use")),
            "operator_override": bool(operator_ok and not progress.get("ready_for_daily_use")),
            "progress_percent": progress.get("percent"),
            "next_recommended_actions": [
                "usar Modo Fácil para comandos curtos",
                "manter backend no PC ligado quando quiseres automação",
                "usar Ações críticas para instalação/update/ficheiros",
                "não inserir credenciais no chat normal",
            ],
        }
        self._store("completions", completion)
        self._update_session_fields(session_id, {"updated_at": self._now(), "status": "completed" if completion["ready_for_daily_use"] else "completed_with_override"})
        return {"ok": True, "mode": "first_real_run_completed", "completion": completion}

    def _safe_evidence(self, evidence: Dict[str, Any]) -> Dict[str, Any]:
        sensitive_markers = ["pass", "secret", "credential", "auth", "key"]
        safe: Dict[str, Any] = {}
        for key, value in evidence.items():
            lowered = str(key).lower()
            safe[key] = "<redacted>" if any(part in lowered for part in sensitive_markers) else value
        return safe

    def _next_step(self, step_status: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        return next((step for step in step_status if step.get("status") != "passed"), None)

    def _find_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        sessions = FIRST_RUN_STORE.load().get("sessions", [])
        return next((s for s in sessions if s.get("session_id") == session_id), None)

    def _results_for_session(self, session_id: str) -> List[Dict[str, Any]]:
        return [r for r in FIRST_RUN_STORE.load().get("step_results", []) if r.get("session_id") == session_id]

    def _advance_session(self, session_id: str) -> None:
        progress_result = self.progress(session_id)
        next_step = (progress_result.get("progress") or {}).get("next_step") if progress_result.get("ok") else None
        updates = {"updated_at": self._now(), "current_step": (next_step or {}).get("step_id"), "status": "ready_to_complete" if next_step is None else "in_progress"}
        self._update_session_fields(session_id, updates)

    def _update_session_fields(self, session_id: str, updates: Dict[str, Any]) -> None:
        def mutate(state: Dict[str, Any]) -> Dict[str, Any]:
            for session in state.get("sessions", []):
                if session.get("session_id") == session_id:
                    session.update(updates)
            return state
        FIRST_RUN_STORE.update(mutate)

    def _store(self, key: str, value: Dict[str, Any]) -> None:
        def mutate(state: Dict[str, Any]) -> Dict[str, Any]:
            state.setdefault(key, [])
            state[key].append(value)
            state[key] = state[key][-100:]
            return state
        FIRST_RUN_STORE.update(mutate)

    def latest(self) -> Dict[str, Any]:
        state = FIRST_RUN_STORE.load()
        return {
            "ok": True,
            "mode": "first_real_run_latest",
            "latest_session": (state.get("sessions") or [None])[-1],
            "latest_step_result": (state.get("step_results") or [None])[-1],
            "latest_completion": (state.get("completions") or [None])[-1],
            "session_count": len(state.get("sessions") or []),
            "completion_count": len(state.get("completions") or []),
        }

    def panel(self) -> Dict[str, Any]:
        latest_session = self.latest().get("latest_session")
        progress = self.progress(latest_session["session_id"]).get("progress") if latest_session else None
        return {
            "ok": True,
            "mode": "first_real_run_panel",
            "headline": "Primeira execução real do God Mode",
            "latest": self.latest(),
            "progress": progress,
            "steps": self.STEPS,
            "safe_buttons": [
                {"id": "start", "label": "Começar primeira execução", "endpoint": "/api/first-real-run/start", "priority": "critical"},
                {"id": "progress", "label": "Ver progresso", "endpoint": "/api/first-real-run/progress", "priority": "critical"},
                {"id": "complete", "label": "Confirmar pronto", "endpoint": "/api/first-real-run/complete", "priority": "critical"},
            ],
        }

    def get_status(self) -> Dict[str, Any]:
        latest = self.latest()
        completion = latest.get("latest_completion") or {}
        session = latest.get("latest_session") or {}
        return {
            "ok": True,
            "mode": "first_real_run_status",
            "has_session": bool(session),
            "latest_session_status": session.get("status"),
            "ready_for_daily_use": completion.get("ready_for_daily_use"),
            "session_count": latest.get("session_count", 0),
            "completion_count": latest.get("completion_count", 0),
        }

    def get_package(self) -> Dict[str, Any]:
        return {"ok": True, "mode": "first_real_run_package", "package": {"status": self.get_status(), "panel": self.panel(), "latest": self.latest()}}


first_real_run_checklist_service = FirstRealRunChecklistService()
