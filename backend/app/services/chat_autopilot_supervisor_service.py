from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List
from uuid import uuid4

from app.services.request_worker_loop_service import request_worker_loop_service
from app.utils.atomic_json_store import AtomicJsonStore

DATA_DIR = Path("data")
AUTOPILOT_FILE = DATA_DIR / "chat_autopilot_supervisor.json"
AUTOPILOT_STORE = AtomicJsonStore(
    AUTOPILOT_FILE,
    default_factory=lambda: {"version": 1, "runs": [], "reports": []},
)


class ChatAutopilotSupervisorService:
    """Runs controlled worker rounds after a chat command.

    The goal is not to bypass approvals. It repeatedly gives the backend chances
    to continue safe work until it becomes idle, blocked, or reaches budget.
    """

    DEFAULT_MAX_ROUNDS = 6
    DEFAULT_MAX_JOBS_PER_ROUND = 4

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def _normalize(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        payload.setdefault("version", 1)
        payload.setdefault("runs", [])
        payload.setdefault("reports", [])
        return payload

    def _record(self, key: str, item: Dict[str, Any]) -> None:
        def mutate(payload: Dict[str, Any]) -> Dict[str, Any]:
            payload = self._normalize(payload)
            payload[key].append(item)
            payload[key] = payload[key][-300:]
            return payload

        AUTOPILOT_STORE.update(mutate)

    def get_status(self) -> Dict[str, Any]:
        state = self._normalize(AUTOPILOT_STORE.load())
        return {
            "ok": True,
            "mode": "chat_autopilot_supervisor_status",
            "status": "ready",
            "policy": "continue_until_idle_blocked_or_budget",
            "approval_bypass": False,
            "max_rounds_default": self.DEFAULT_MAX_ROUNDS,
            "max_jobs_per_round_default": self.DEFAULT_MAX_JOBS_PER_ROUND,
            "run_count": len(state["runs"]),
            "report_count": len(state["reports"]),
        }

    def run_until_blocked_or_idle(
        self,
        tenant_id: str = "owner-andre",
        job_id: str | None = None,
        reason: str = "chat_command",
        max_rounds: int | None = None,
        max_jobs_per_round: int | None = None,
    ) -> Dict[str, Any]:
        run_id = f"autopilot-{uuid4().hex[:12]}"
        rounds_budget = max(1, min(int(max_rounds or self.DEFAULT_MAX_ROUNDS), 20))
        jobs_budget = max(1, min(int(max_jobs_per_round or self.DEFAULT_MAX_JOBS_PER_ROUND), 20))
        rounds: List[Dict[str, Any]] = []
        stop_reason = "budget_exhausted"
        for index in range(1, rounds_budget + 1):
            tick = request_worker_loop_service.tick(tenant_id=tenant_id, max_jobs=jobs_budget)
            summary = self._summarize_tick(index, tick)
            rounds.append(summary)
            if summary["processed_count"] <= 0:
                stop_reason = "idle_no_jobs_processed"
                break
            if summary["blocked_count"] > 0:
                stop_reason = "blocked_waiting_operator"
                break
            if summary["failed_count"] > 0:
                stop_reason = "failed_needs_review"
                break
        report = {
            "report_id": f"autopilot-report-{uuid4().hex[:12]}",
            "run_id": run_id,
            "created_at": self._now(),
            "tenant_id": tenant_id,
            "job_id": job_id,
            "reason": reason,
            "rounds_budget": rounds_budget,
            "jobs_budget": jobs_budget,
            "rounds": rounds,
            "round_count": len(rounds),
            "processed_total": sum(item["processed_count"] for item in rounds),
            "blocked_total": sum(item["blocked_count"] for item in rounds),
            "failed_total": sum(item["failed_count"] for item in rounds),
            "stop_reason": stop_reason,
            "needs_operator": stop_reason in {"blocked_waiting_operator", "failed_needs_review"},
            "approval_bypass": False,
            "next_routes": self._next_routes(stop_reason),
        }
        run = {
            "run_id": run_id,
            "created_at": report["created_at"],
            "tenant_id": tenant_id,
            "job_id": job_id,
            "reason": reason,
            "stop_reason": stop_reason,
            "processed_total": report["processed_total"],
        }
        self._record("runs", run)
        self._record("reports", report)
        return {"ok": True, "mode": "chat_autopilot_supervisor_run", "run": run, "report": report}

    def _summarize_tick(self, round_index: int, tick: Any) -> Dict[str, Any]:
        if not isinstance(tick, dict):
            return {"round": round_index, "raw": str(tick), "processed_count": 0, "blocked_count": 0, "failed_count": 0, "completed_count": 0}
        text = str(tick).lower()
        processed_items = tick.get("processed") or tick.get("jobs") or tick.get("results") or []
        if isinstance(processed_items, dict):
            processed_items = list(processed_items.values())
        if not isinstance(processed_items, list):
            processed_items = []
        processed_count = int(tick.get("processed_count", len(processed_items) if processed_items else 0) or 0)
        blocked_count = int(tick.get("blocked_count", 0) or 0)
        failed_count = int(tick.get("failed_count", 0) or 0)
        completed_count = int(tick.get("completed_count", 0) or 0)
        if blocked_count == 0 and "blocked" in text:
            blocked_count = 1
        if failed_count == 0 and ("failed" in text or "error" in text):
            failed_count = 1
        if processed_count == 0 and any(word in text for word in ["processed", "job_id", "running", "blocked", "completed"]):
            processed_count = 1
        return {
            "round": round_index,
            "processed_count": processed_count,
            "blocked_count": blocked_count,
            "failed_count": failed_count,
            "completed_count": completed_count,
            "tick_mode": tick.get("mode"),
            "tick_status": tick.get("status"),
            "tick": tick,
        }

    def _next_routes(self, stop_reason: str) -> List[Dict[str, str]]:
        routes = [
            {"label": "Chat", "route": "/app/operator-chat-sync-cards"},
            {"label": "Worker", "route": "/app/request-worker"},
        ]
        if stop_reason in {"blocked_waiting_operator", "failed_needs_review"}:
            routes.insert(0, {"label": "Aprovações", "route": "/app/mobile-approval-cockpit-v2"})
        return routes

    def latest(self) -> Dict[str, Any]:
        state = self._normalize(AUTOPILOT_STORE.load())
        return {
            "ok": True,
            "mode": "chat_autopilot_supervisor_latest",
            "run": state["runs"][-1] if state["runs"] else None,
            "report": state["reports"][-1] if state["reports"] else None,
        }

    def get_package(self) -> Dict[str, Any]:
        return {"ok": True, "mode": "chat_autopilot_supervisor_package", "package": {"status": self.get_status(), "latest": self.latest()}}


chat_autopilot_supervisor_service = ChatAutopilotSupervisorService()
