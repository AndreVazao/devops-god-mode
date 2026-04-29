from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import uuid4

from app.services.approved_deep_execution_plan_service import approved_deep_execution_plan_service
from app.services.operation_queue_service import operation_queue_service
from app.services.real_work_command_pipeline_service import real_work_command_pipeline_service
from app.services.request_worker_loop_service import request_worker_loop_service
from app.utils.atomic_json_store import AtomicJsonStore

DATA_DIR = Path("data")
QUEUE_FILE = DATA_DIR / "approved_work_queue_runner.json"
QUEUE_STORE = AtomicJsonStore(
    QUEUE_FILE,
    default_factory=lambda: {
        "version": 1,
        "policy": "run_safe_steps_only_stop_on_gates",
        "queues": [],
        "runs": [],
    },
)


class ApprovedWorkQueueRunnerService:
    """Queue runner for approval-gated deep execution.

    This layer transforms Phase 112 lanes into a durable operational queue.
    It may submit safe commands to the real work pipeline, but it stops before
    any gated/destructive action.
    """

    SAFE_ACTION_TYPES = {
        "read_inventory",
        "read_project_tree",
        "read_repo_metadata",
        "read_visible_chat_snapshot",
        "summarize_findings",
        "prepare_patch_preview",
    }

    GATED_ACTION_TYPES = {
        "external_ai_prompt_send",
        "conversation_rename",
        "repo_create",
        "project_file_write",
        "code_materialization",
        "build_trigger",
        "module_merge_or_delete",
    }

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def build_queue(self, tenant_id: str = "owner-andre", requested_project: Optional[str] = None) -> Dict[str, Any]:
        plan_result = approved_deep_execution_plan_service.build_plan(
            tenant_id=tenant_id,
            requested_project=requested_project,
        )
        plan = plan_result.get("plan") or {}
        queue_id = f"approved-work-queue-{uuid4().hex[:12]}"
        if not plan_result.get("ok"):
            queue = {
                "queue_id": queue_id,
                "created_at": self._now(),
                "tenant_id": tenant_id,
                "status": "blocked_waiting_operator_confirmation",
                "plan_id": plan.get("plan_id"),
                "blocked_reason": plan.get("readiness", {}).get("blocked_reasons", []),
                "items": [],
                "operator_next": plan.get("operator_next"),
            }
            self._store_queue(queue)
            return {"ok": False, "mode": "approved_work_queue_build", "queue": queue}

        items: List[Dict[str, Any]] = []
        for lane in plan.get("lanes", []):
            for step in lane.get("safe_first_steps", []):
                items.append(self._queue_item(plan, lane, step, approval_required=False))
            for step in lane.get("gated_steps", []):
                items.append(self._queue_item(plan, lane, step, approval_required=True))
        queue = {
            "queue_id": queue_id,
            "created_at": self._now(),
            "tenant_id": tenant_id,
            "status": "ready",
            "plan_id": plan.get("plan_id"),
            "active_project": plan.get("active_project"),
            "items": items,
            "item_count": len(items),
            "safe_item_count": len([item for item in items if not item["approval_required"]]),
            "gated_item_count": len([item for item in items if item["approval_required"]]),
            "external_queue_preview": operation_queue_service.get_preview(),
            "operator_next": {"label": "Executar próximos passos seguros", "endpoint": "/api/approved-work-queue/run-safe", "route": "/app/home"},
        }
        self._store_queue(queue)
        return {"ok": True, "mode": "approved_work_queue_build", "queue": queue}

    def _queue_item(self, plan: Dict[str, Any], lane: Dict[str, Any], step: Dict[str, Any], approval_required: bool) -> Dict[str, Any]:
        action_type = step.get("action_type") or "unknown"
        return {
            "item_id": f"approved-work-item-{uuid4().hex[:12]}",
            "plan_id": plan.get("plan_id"),
            "lane_id": lane.get("lane_id"),
            "project_id": lane.get("project_id"),
            "priority": lane.get("priority"),
            "step_id": step.get("id"),
            "label": step.get("label"),
            "action_type": action_type,
            "approval_required": approval_required or action_type in self.GATED_ACTION_TYPES,
            "status": "waiting_approval" if approval_required or action_type in self.GATED_ACTION_TYPES else "queued",
            "safe_to_auto_run": (not approval_required) and action_type in self.SAFE_ACTION_TYPES,
            "created_at": self._now(),
        }

    def run_safe(self, tenant_id: str = "owner-andre", queue_id: Optional[str] = None, max_items: int = 3) -> Dict[str, Any]:
        state = QUEUE_STORE.load()
        queue = self._select_queue(state, queue_id)
        if not queue:
            built = self.build_queue(tenant_id=tenant_id)
            queue = built.get("queue")
        if not queue or queue.get("status") != "ready":
            return {"ok": False, "mode": "approved_work_queue_run_safe", "status": "blocked", "queue": queue}

        limit = max(1, min(max_items, 10))
        runnable = [item for item in queue.get("items", []) if item.get("status") == "queued" and item.get("safe_to_auto_run")]
        selected = runnable[:limit]
        submitted: List[Dict[str, Any]] = []
        for item in selected:
            command = self._safe_command_for_item(item)
            try:
                result = real_work_command_pipeline_service.submit_command(
                    command_text=command,
                    tenant_id=tenant_id,
                    requested_project=item.get("project_id"),
                    auto_run=False,
                )
                item["status"] = "submitted_safe"
                item["submitted_at"] = self._now()
                item["command"] = command
                item["pipeline_report"] = (result.get("report") or {}) if isinstance(result, dict) else {}
                submitted.append({"item_id": item["item_id"], "ok": True, "command": command, "report": item["pipeline_report"]})
            except Exception as exc:
                item["status"] = "safe_submit_failed"
                item["error"] = exc.__class__.__name__
                item["detail"] = str(exc)[:300]
                submitted.append({"item_id": item["item_id"], "ok": False, "error": item["error"], "detail": item["detail"]})

        gated = [item for item in queue.get("items", []) if item.get("approval_required") and item.get("status") == "waiting_approval"]
        worker_tick = None
        if submitted:
            try:
                worker_tick = request_worker_loop_service.tick(tenant_id=tenant_id, max_jobs=limit)
            except Exception as exc:
                worker_tick = {"ok": False, "error": exc.__class__.__name__, "detail": str(exc)[:300]}

        run = {
            "run_id": f"approved-work-run-{uuid4().hex[:12]}",
            "queue_id": queue.get("queue_id"),
            "created_at": self._now(),
            "tenant_id": tenant_id,
            "submitted_count": len(submitted),
            "submitted": submitted,
            "gated_waiting_count": len(gated),
            "worker_tick": worker_tick,
            "stop_reason": "waiting_approval" if gated else ("no_more_safe_items" if not runnable[limit:] else "safe_batch_submitted"),
        }
        self._update_queue_and_record_run(queue, run)
        return {
            "ok": True,
            "mode": "approved_work_queue_run_safe",
            "run": run,
            "operator_next": self._operator_next_after_run(run),
        }

    def _safe_command_for_item(self, item: Dict[str, Any]) -> str:
        return (
            f"Projeto {item.get('project_id')}: executar apenas o passo seguro '{item.get('label')}' "
            f"({item.get('action_type')}). Não escrever ficheiros, não criar repos, não enviar prompts externos, "
            "não renomear conversas e parar se precisares de aprovação."
        )

    def _operator_next_after_run(self, run: Dict[str, Any]) -> Dict[str, Any]:
        if run.get("gated_waiting_count", 0) > 0:
            return {"label": "Rever aprovações pendentes", "endpoint": "/api/approved-work-queue/gates", "route": "/app/home"}
        return {"label": "Ver estado da fila", "endpoint": "/api/approved-work-queue/current", "route": "/app/home"}

    def gates(self, queue_id: Optional[str] = None) -> Dict[str, Any]:
        state = QUEUE_STORE.load()
        queue = self._select_queue(state, queue_id)
        gated = [item for item in (queue or {}).get("items", []) if item.get("approval_required")]
        return {
            "ok": True,
            "mode": "approved_work_queue_gates",
            "queue_id": (queue or {}).get("queue_id"),
            "gated_count": len(gated),
            "gates": gated,
            "policy": "operator_approval_required_before_execution",
        }

    def current(self) -> Dict[str, Any]:
        state = QUEUE_STORE.load()
        queue = self._select_queue(state, None)
        return {
            "ok": True,
            "mode": "approved_work_queue_current",
            "queue": queue,
            "latest_run": (state.get("runs") or [])[-1] if state.get("runs") else None,
        }

    def _select_queue(self, state: Dict[str, Any], queue_id: Optional[str]) -> Optional[Dict[str, Any]]:
        queues = state.get("queues") or []
        if queue_id:
            return next((q for q in queues if q.get("queue_id") == queue_id), None)
        return queues[-1] if queues else None

    def _store_queue(self, queue: Dict[str, Any]) -> None:
        def mutate(state: Dict[str, Any]) -> Dict[str, Any]:
            state.setdefault("version", 1)
            state.setdefault("policy", "run_safe_steps_only_stop_on_gates")
            state.setdefault("queues", [])
            state.setdefault("runs", [])
            state["queues"].append(queue)
            state["queues"] = state["queues"][-100:]
            return state

        QUEUE_STORE.update(mutate)

    def _update_queue_and_record_run(self, queue: Dict[str, Any], run: Dict[str, Any]) -> None:
        def mutate(state: Dict[str, Any]) -> Dict[str, Any]:
            state.setdefault("queues", [])
            state.setdefault("runs", [])
            for idx, existing in enumerate(state["queues"]):
                if existing.get("queue_id") == queue.get("queue_id"):
                    state["queues"][idx] = queue
                    break
            state["runs"].append(run)
            state["runs"] = state["runs"][-200:]
            return state

        QUEUE_STORE.update(mutate)

    def get_status(self) -> Dict[str, Any]:
        state = QUEUE_STORE.load()
        current_queue = self._select_queue(state, None)
        return {
            "ok": True,
            "mode": "approved_work_queue_status",
            "status": (current_queue or {}).get("status") or "no_queue_yet",
            "queue_count": len(state.get("queues") or []),
            "run_count": len(state.get("runs") or []),
            "current_queue_id": (current_queue or {}).get("queue_id"),
            "policy": state.get("policy"),
        }

    def get_package(self) -> Dict[str, Any]:
        return {"ok": True, "mode": "approved_work_queue_package", "package": {"status": self.get_status(), "current": self.current()}}


approved_work_queue_runner_service = ApprovedWorkQueueRunnerService()
