from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List
from uuid import uuid4

from app.services.mobile_approval_cockpit_v2_service import mobile_approval_cockpit_v2_service

DATA_DIR = Path("data")
EXECUTION_QUEUE_FILE = DATA_DIR / "approved_card_execution_queue.json"

TASK_RULES = {
    "operator_command": ["prepare-read-only-execution", "notify-mobile-progress"],
    "deploy_env_sync_approval": ["prepare-provider-env-sync", "verify-no-secret-values-in-output", "notify-mobile-progress"],
    "pr_write_approval": ["prepare-git-branch", "apply-approved-patch", "open-pr", "notify-mobile-progress"],
    "secret_binding_approval": ["prepare-secret-binding", "verify-secret-presence", "notify-mobile-progress"],
    "provider_login_request": ["open-provider-login-session", "wait-for-operator-login", "notify-mobile-progress"],
    "destructive_action_guard": ["hard-stop-and-require-secondary-confirmation"],
    "progress_update": ["acknowledge-progress"],
}


class ApprovedCardExecutionQueueService:
    """Queue approved mobile cards into safe PC execution tasks.

    This phase consumes Phase 30 decisions and turns approved/acknowledged cards
    into deterministic task bundles. It still does not execute external writes by
    itself; it prepares auditable tasks with risk tags for future executors.
    """

    def get_status(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "mode": "approved_card_execution_queue_status",
            "status": "approved_card_execution_queue_ready",
            "queue_file": str(EXECUTION_QUEUE_FILE),
        }

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def _load_queue(self) -> Dict[str, Any]:
        if not EXECUTION_QUEUE_FILE.exists():
            return {"tasks": [], "processed_card_ids": []}
        try:
            loaded = json.loads(EXECUTION_QUEUE_FILE.read_text(encoding="utf-8"))
            if not isinstance(loaded, dict):
                return {"tasks": [], "processed_card_ids": []}
            loaded.setdefault("tasks", [])
            loaded.setdefault("processed_card_ids", [])
            return loaded
        except json.JSONDecodeError:
            return {"tasks": [], "processed_card_ids": []}

    def _save_queue(self, queue: Dict[str, Any]) -> None:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        EXECUTION_QUEUE_FILE.write_text(json.dumps(queue, ensure_ascii=False, indent=2), encoding="utf-8")

    def _risk_for_step(self, step_id: str, card_type: str) -> str:
        if card_type == "destructive_action_guard":
            return "blocked_destructive"
        if any(token in step_id for token in ["apply", "open-pr", "provider-env-sync", "secret-binding", "login"]):
            return "write_or_external_requires_executor_guard"
        return "safe_local_preparation"

    def _task_from_card(self, card: Dict[str, Any]) -> Dict[str, Any]:
        card_type = card.get("card_type", "progress_update")
        rule_steps = TASK_RULES.get(card_type, TASK_RULES["progress_update"])
        task_id = f"task-{uuid4().hex[:12]}"
        steps = [
            {
                "step_id": step_id,
                "label": step_id.replace("-", " ").title(),
                "risk": self._risk_for_step(step_id, card_type),
                "status": "queued",
            }
            for step_id in rule_steps
        ]
        return {
            "task_id": task_id,
            "tenant_id": card.get("tenant_id", "owner-andre"),
            "project_id": card.get("project_id", "general-intake"),
            "source_card_id": card.get("card_id"),
            "source_card_type": card_type,
            "source_title": card.get("title"),
            "source_ref": card.get("source_ref", {}),
            "created_at": self._now(),
            "updated_at": self._now(),
            "status": "queued",
            "execution_mode": "pc_local_safe_queue",
            "steps": steps,
            "guardrails": [
                "do_not_expose_secret_values",
                "do_not_execute_destructive_actions_without_secondary_confirmation",
                "write_actions_require_executor_guard",
                "report_progress_back_to_mobile",
            ],
        }

    def ingest_approved_cards(
        self,
        tenant_id: str = "owner-andre",
        project_id: str | None = None,
    ) -> Dict[str, Any]:
        queue = self._load_queue()
        processed = set(queue.get("processed_card_ids", []))
        cards = mobile_approval_cockpit_v2_service.list_cards(tenant_id=tenant_id, project_id=project_id, limit=300).get("cards", [])
        eligible = [card for card in cards if card.get("status") in {"approved", "acknowledged"} and card.get("card_id") not in processed]
        created_tasks = []
        for card in eligible:
            task = self._task_from_card(card)
            queue["tasks"].append(task)
            queue["processed_card_ids"].append(card.get("card_id"))
            created_tasks.append(task)
        queue["tasks"] = queue["tasks"][-1000:]
        queue["processed_card_ids"] = queue["processed_card_ids"][-2000:]
        self._save_queue(queue)
        return {
            "ok": True,
            "mode": "approved_card_execution_queue_ingest",
            "created_task_count": len(created_tasks),
            "tasks": created_tasks,
        }

    def list_tasks(
        self,
        tenant_id: str = "owner-andre",
        project_id: str | None = None,
        status: str | None = None,
        limit: int = 100,
    ) -> Dict[str, Any]:
        queue = self._load_queue()
        tasks = [item for item in queue.get("tasks", []) if item.get("tenant_id") == tenant_id]
        if project_id:
            tasks = [item for item in tasks if item.get("project_id") == project_id]
        if status:
            tasks = [item for item in tasks if item.get("status") == status]
        tasks = tasks[-max(min(limit, 300), 1):]
        return {"ok": True, "mode": "approved_card_execution_queue_list", "task_count": len(tasks), "tasks": tasks}

    def update_task_status(
        self,
        task_id: str,
        status: str,
        tenant_id: str = "owner-andre",
        note: str = "",
    ) -> Dict[str, Any]:
        allowed = {"queued", "running", "blocked", "completed", "failed", "cancelled"}
        normalized = status.lower().strip()
        if normalized not in allowed:
            return {"ok": False, "error": "invalid_status", "allowed": sorted(allowed)}
        queue = self._load_queue()
        for task in queue.get("tasks", []):
            if task.get("task_id") == task_id and task.get("tenant_id") == tenant_id:
                task["status"] = normalized
                task["updated_at"] = self._now()
                task.setdefault("status_history", []).append({"status": normalized, "note": note, "at": self._now()})
                self._save_queue(queue)
                return {"ok": True, "mode": "approved_card_execution_queue_update", "task": task}
        return {"ok": False, "error": "task_not_found", "task_id": task_id}

    def build_dashboard(self, tenant_id: str = "owner-andre") -> Dict[str, Any]:
        tasks = self.list_tasks(tenant_id=tenant_id, limit=300).get("tasks", [])
        queued = [item for item in tasks if item.get("status") == "queued"]
        blocked = [item for item in tasks if item.get("status") == "blocked"]
        risky = [item for item in tasks for step in item.get("steps", []) if step.get("risk") != "safe_local_preparation"]
        return {
            "ok": True,
            "mode": "approved_card_execution_queue_dashboard",
            "tenant_id": tenant_id,
            "task_count": len(tasks),
            "queued_count": len(queued),
            "blocked_count": len(blocked),
            "risky_step_count": len(risky),
            "recent_tasks": tasks[-50:],
        }

    def get_package(self) -> Dict[str, Any]:
        return {"ok": True, "mode": "approved_card_execution_queue_package", "package": {"status": self.get_status(), "dashboard": self.build_dashboard()}}


approved_card_execution_queue_service = ApprovedCardExecutionQueueService()
