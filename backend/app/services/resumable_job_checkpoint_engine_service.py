from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import uuid4

from app.services.memory_context_router_service import memory_context_router_service
from app.utils.atomic_json_store import AtomicJsonStore

DATA_DIR = Path("data")
JOBS_FILE = DATA_DIR / "resumable_job_checkpoint_engine.json"
JOBS_STORE = AtomicJsonStore(
    JOBS_FILE,
    default_factory=lambda: {
        "version": 1,
        "policy": "checkpoint_every_safe_step_and_resume_after_interruptions",
        "jobs": [],
        "checkpoints": [],
        "stop_events": [],
        "resume_plans": [],
        "resume_runs": [],
    },
)


class ResumableJobCheckpointEngineService:
    """Generic resumable job/checkpoint engine for God Mode.

    Long jobs must survive APK disconnect, network loss, provider limits,
    browser session loss and PC restarts. This service stores durable job state,
    safe checkpoints, stop reasons and resume plans without storing secrets.
    """

    SAFE_STOP_REASONS = [
        "apk_disconnected",
        "network_offline",
        "provider_rate_limited",
        "browser_session_lost",
        "pc_restarted",
        "job_paused_by_operator",
        "needs_operator_login",
        "needs_operator_ok",
        "validation_failed",
        "work_completed",
    ]
    HARD_STOP_REASONS = [
        "unsafe_or_sensitive_request",
        "destructive_action_without_approval",
        "secret_detected",
        "unknown_critical_error",
    ]

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def policy(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "mode": "resumable_job_checkpoint_policy",
            "rules": [
                "criar job antes de trabalho longo",
                "guardar checkpoint depois de cada passo seguro",
                "guardar stop reason quando parar",
                "não guardar tokens/passwords/cookies/secrets",
                "retomar do último checkpoint safe_to_resume",
                "se houver hard stop, exigir operador",
                "se trabalho terminar, congelar estado final",
            ],
            "safe_stop_reasons": self.SAFE_STOP_REASONS,
            "hard_stop_reasons": self.HARD_STOP_REASONS,
        }

    def create_job(
        self,
        project_id: str = "GOD_MODE",
        title: str = "God Mode job",
        objective: str = "continue until completed or blocked",
        source_module: str = "operator",
        priority: str = "normal",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        job = {
            "job_id": f"resumable-job-{uuid4().hex[:12]}",
            "created_at": self._now(),
            "updated_at": self._now(),
            "project_id": self._normalize_project(project_id),
            "title": title[:300],
            "objective": objective[:2000],
            "source_module": source_module,
            "priority": priority,
            "status": "active",
            "current_step": None,
            "last_checkpoint_id": None,
            "last_stop_reason": None,
            "metadata": self._safe_metadata(metadata or {}),
        }
        self._store("jobs", job)
        self.add_checkpoint(
            job_id=job["job_id"],
            step_id="job_created",
            step_label="Job criado",
            state_summary=objective,
            safe_to_resume=True,
            resume_hint="start_next_planned_step",
        )
        memory_context_router_service.prepare_project_context(
            project_id=job["project_id"],
            source="resumable_job_created",
            idea=f"Job {job['job_id']}: {title} — {objective}",
            max_chars=4000,
        )
        return {"ok": True, "mode": "resumable_job_created", "job": self._find_job(job["job_id"])}

    def add_checkpoint(
        self,
        job_id: str,
        step_id: str,
        step_label: str = "",
        state_summary: str = "",
        safe_to_resume: bool = True,
        resume_hint: str = "continue_from_here",
        artifacts: Optional[List[Dict[str, Any]]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        job = self._find_job(job_id)
        if not job:
            return {"ok": False, "mode": "resumable_job_checkpoint", "error": "job_not_found"}
        checkpoint = {
            "checkpoint_id": f"checkpoint-{uuid4().hex[:12]}",
            "created_at": self._now(),
            "job_id": job_id,
            "project_id": job.get("project_id"),
            "step_id": step_id[:200],
            "step_label": step_label[:300],
            "state_summary": state_summary[:5000],
            "safe_to_resume": bool(safe_to_resume),
            "resume_hint": resume_hint[:1000],
            "artifacts": self._safe_artifacts(artifacts or []),
            "metadata": self._safe_metadata(metadata or {}),
        }
        self._store("checkpoints", checkpoint)
        self._update_job(job_id, {
            "updated_at": self._now(),
            "current_step": step_id,
            "last_checkpoint_id": checkpoint["checkpoint_id"],
            "status": "active" if job.get("status") != "completed" else "completed",
        })
        return {"ok": True, "mode": "resumable_job_checkpoint", "checkpoint": checkpoint}

    def stop_job(
        self,
        job_id: str,
        stop_reason: str,
        detail: str = "",
        requires_operator: bool = False,
        next_action: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        job = self._find_job(job_id)
        if not job:
            return {"ok": False, "mode": "resumable_job_stop", "error": "job_not_found"}
        normalized_reason = self._normalize_stop_reason(stop_reason)
        hard_stop = normalized_reason in self.HARD_STOP_REASONS
        status = "completed" if normalized_reason == "work_completed" else ("blocked" if hard_stop or requires_operator else "paused")
        stop_event = {
            "stop_event_id": f"stop-event-{uuid4().hex[:12]}",
            "created_at": self._now(),
            "job_id": job_id,
            "project_id": job.get("project_id"),
            "stop_reason": normalized_reason,
            "detail": detail[:2000],
            "requires_operator": bool(requires_operator or hard_stop or normalized_reason in {"needs_operator_login", "needs_operator_ok"}),
            "hard_stop": hard_stop,
            "next_action": next_action or self._default_next_action(normalized_reason),
        }
        self._store("stop_events", stop_event)
        self._update_job(job_id, {
            "updated_at": self._now(),
            "status": status,
            "last_stop_reason": normalized_reason,
        })
        return {"ok": True, "mode": "resumable_job_stop", "stop_event": stop_event, "job": self._find_job(job_id)}

    def resume_plan(self, job_id: str) -> Dict[str, Any]:
        job = self._find_job(job_id)
        if not job:
            return {"ok": False, "mode": "resumable_job_resume_plan", "error": "job_not_found"}
        checkpoints = self._job_checkpoints(job_id)
        last_safe = next((cp for cp in reversed(checkpoints) if cp.get("safe_to_resume")), None)
        hard_block = job.get("last_stop_reason") in self.HARD_STOP_REASONS
        plan = {
            "resume_plan_id": f"resume-plan-{uuid4().hex[:12]}",
            "created_at": self._now(),
            "job_id": job_id,
            "project_id": job.get("project_id"),
            "job_status": job.get("status"),
            "last_stop_reason": job.get("last_stop_reason"),
            "last_safe_checkpoint": last_safe,
            "can_resume": bool(last_safe and not hard_block and job.get("status") != "completed"),
            "requires_operator": bool(hard_block or job.get("status") == "blocked"),
            "resume_from_step": (last_safe or {}).get("step_id"),
            "resume_hint": (last_safe or {}).get("resume_hint"),
            "recommended_action": self._recommended_resume_action(job, last_safe, hard_block),
        }
        self._store("resume_plans", plan)
        return {"ok": True, "mode": "resumable_job_resume_plan", "plan": plan}

    def resume_job(self, job_id: str, operator_ok: bool = False) -> Dict[str, Any]:
        plan_result = self.resume_plan(job_id)
        if not plan_result.get("ok"):
            return plan_result
        plan = plan_result.get("plan") or {}
        if plan.get("requires_operator") and not operator_ok:
            return {
                "ok": False,
                "mode": "resumable_job_resume",
                "error": "operator_ok_required",
                "resume_plan": plan,
            }
        if not plan.get("can_resume") and not operator_ok:
            return {
                "ok": False,
                "mode": "resumable_job_resume",
                "error": "job_not_resumable_without_operator",
                "resume_plan": plan,
            }
        run = {
            "resume_run_id": f"resume-run-{uuid4().hex[:12]}",
            "created_at": self._now(),
            "job_id": job_id,
            "resume_plan_id": plan.get("resume_plan_id"),
            "resumed_from_checkpoint_id": (plan.get("last_safe_checkpoint") or {}).get("checkpoint_id"),
            "resumed_from_step": plan.get("resume_from_step"),
            "status": "resume_ready_for_executor",
            "executor_contract": {
                "continue_from_step": plan.get("resume_from_step"),
                "resume_hint": plan.get("resume_hint"),
                "do_not_repeat_completed_unsafe_actions": True,
                "write_checkpoint_after_next_safe_step": True,
            },
        }
        self._store("resume_runs", run)
        self._update_job(job_id, {"updated_at": self._now(), "status": "active", "last_stop_reason": None})
        return {"ok": True, "mode": "resumable_job_resume", "run": run}

    def complete_job(self, job_id: str, summary: str = "completed") -> Dict[str, Any]:
        self.add_checkpoint(
            job_id=job_id,
            step_id="job_completed",
            step_label="Job concluído",
            state_summary=summary,
            safe_to_resume=False,
            resume_hint="job_done_no_resume_needed",
        )
        return self.stop_job(job_id=job_id, stop_reason="work_completed", detail=summary, requires_operator=False)

    def _safe_metadata(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        blocked = ["token", "password", "cookie", "secret", "authorization", "bearer", "api_key", "apikey", "private_key"]
        safe = {}
        for key, value in metadata.items():
            lowered = str(key).lower()
            safe[key] = "<redacted_sensitive_key>" if any(part in lowered for part in blocked) else value
        return safe

    def _safe_artifacts(self, artifacts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        safe = []
        for item in artifacts[:50]:
            safe.append(self._safe_metadata(item))
        return safe

    def _normalize_stop_reason(self, reason: str) -> str:
        normalized = (reason or "unknown_critical_error").strip().lower().replace(" ", "_")
        if normalized in self.SAFE_STOP_REASONS or normalized in self.HARD_STOP_REASONS:
            return normalized
        return "unknown_critical_error"

    def _default_next_action(self, reason: str) -> Dict[str, Any]:
        mapping = {
            "apk_disconnected": {"label": "continuar backend; aguardar heartbeat APK", "operator_required": False},
            "network_offline": {"label": "aguardar rede e retomar do checkpoint", "operator_required": False},
            "provider_rate_limited": {"label": "trocar provider ou pausar até limite passar", "operator_required": False},
            "browser_session_lost": {"label": "pedir login manual se necessário", "operator_required": True},
            "needs_operator_login": {"label": "mostrar popup de login", "operator_required": True},
            "needs_operator_ok": {"label": "pedir aprovação no APK/Home", "operator_required": True},
            "validation_failed": {"label": "abrir plano de correção", "operator_required": False},
            "work_completed": {"label": "mostrar resultado final", "operator_required": False},
        }
        return mapping.get(reason, {"label": "parar e pedir revisão", "operator_required": True})

    def _recommended_resume_action(self, job: Dict[str, Any], checkpoint: Optional[Dict[str, Any]], hard_block: bool) -> Dict[str, Any]:
        if job.get("status") == "completed":
            return {"label": "Job concluído; não retomar", "endpoint": "/api/resumable-jobs/latest"}
        if hard_block:
            return {"label": "Pedir revisão do operador", "endpoint": "/api/resumable-jobs/status"}
        if checkpoint:
            return {"label": "Retomar do último checkpoint seguro", "endpoint": "/api/resumable-jobs/resume"}
        return {"label": "Sem checkpoint seguro; criar novo plano", "endpoint": "/api/resumable-jobs/create"}

    def _find_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        jobs = JOBS_STORE.load().get("jobs", [])
        return next((job for job in jobs if job.get("job_id") == job_id), None)

    def _job_checkpoints(self, job_id: str) -> List[Dict[str, Any]]:
        return [cp for cp in JOBS_STORE.load().get("checkpoints", []) if cp.get("job_id") == job_id]

    def _update_job(self, job_id: str, updates: Dict[str, Any]) -> None:
        def mutate(state: Dict[str, Any]) -> Dict[str, Any]:
            for job in state.get("jobs", []):
                if job.get("job_id") == job_id:
                    job.update(updates)
            return state
        JOBS_STORE.update(mutate)

    def _normalize_project(self, project_id: str) -> str:
        return (project_id or "GOD_MODE").strip().upper().replace("-", "_").replace(" ", "_")

    def _store(self, key: str, value: Dict[str, Any]) -> None:
        def mutate(state: Dict[str, Any]) -> Dict[str, Any]:
            state.setdefault(key, [])
            state[key].append(value)
            state[key] = state[key][-200:]
            return state
        JOBS_STORE.update(mutate)

    def latest(self) -> Dict[str, Any]:
        state = JOBS_STORE.load()
        return {
            "ok": True,
            "mode": "resumable_job_latest",
            "latest_job": (state.get("jobs") or [None])[-1],
            "latest_checkpoint": (state.get("checkpoints") or [None])[-1],
            "latest_stop_event": (state.get("stop_events") or [None])[-1],
            "latest_resume_plan": (state.get("resume_plans") or [None])[-1],
            "latest_resume_run": (state.get("resume_runs") or [None])[-1],
            "job_count": len(state.get("jobs") or []),
            "active_job_count": len([j for j in state.get("jobs", []) if j.get("status") == "active"]),
            "paused_job_count": len([j for j in state.get("jobs", []) if j.get("status") == "paused"]),
            "blocked_job_count": len([j for j in state.get("jobs", []) if j.get("status") == "blocked"]),
        }

    def panel(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "mode": "resumable_job_panel",
            "headline": "Jobs retomáveis com checkpoints",
            "policy": self.policy(),
            "latest": self.latest(),
            "safe_buttons": [
                {"id": "create", "label": "Criar job", "endpoint": "/api/resumable-jobs/create", "priority": "critical"},
                {"id": "checkpoint", "label": "Guardar checkpoint", "endpoint": "/api/resumable-jobs/checkpoint", "priority": "critical"},
                {"id": "resume_plan", "label": "Plano retoma", "endpoint": "/api/resumable-jobs/resume-plan", "priority": "critical"},
                {"id": "resume", "label": "Retomar", "endpoint": "/api/resumable-jobs/resume", "priority": "critical"},
            ],
        }

    def get_status(self) -> Dict[str, Any]:
        latest = self.latest()
        return {
            "ok": True,
            "mode": "resumable_job_status",
            "job_count": latest.get("job_count", 0),
            "active_job_count": latest.get("active_job_count", 0),
            "paused_job_count": latest.get("paused_job_count", 0),
            "blocked_job_count": latest.get("blocked_job_count", 0),
            "safe_stop_reasons": self.SAFE_STOP_REASONS,
            "hard_stop_reasons": self.HARD_STOP_REASONS,
        }

    def get_package(self) -> Dict[str, Any]:
        return {"ok": True, "mode": "resumable_job_package", "package": {"status": self.get_status(), "panel": self.panel(), "latest": self.latest()}}


resumable_job_checkpoint_engine_service = ResumableJobCheckpointEngineService()
