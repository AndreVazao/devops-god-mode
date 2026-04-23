from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Dict, List


class OperatorResumableActionService:
    def __init__(self, store_path: str = "data/operator_resumable_actions.json") -> None:
        self.store_path = Path(store_path)
        self.store_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.store_path.exists():
            self.store_path.write_text(json.dumps({"actions": []}, ensure_ascii=False, indent=2), encoding="utf-8")

    def _read_store(self) -> Dict[str, Any]:
        return json.loads(self.store_path.read_text(encoding="utf-8"))

    def _write_store(self, payload: Dict[str, Any]) -> None:
        self.store_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    def get_status(self) -> Dict[str, Any]:
        store = self._read_store()
        return {
            "ok": True,
            "mode": "operator_resumable_action_status",
            "store_path": str(self.store_path),
            "action_count": len(store.get("actions", [])),
            "status": "operator_resumable_action_ready",
        }

    def create_action(
        self,
        tenant_id: str,
        thread_id: str,
        provider_name: str,
        action_kind: str,
        purpose_summary: str,
        resume_strategy: str = "retry_from_latest_safe_checkpoint",
        requires_fresh_provider_session: bool = False,
    ) -> Dict[str, Any]:
        store = self._read_store()
        action_id = f"resume-{len(store.get('actions', [])) + 1:05d}"
        action = {
            "action_id": action_id,
            "tenant_id": tenant_id,
            "thread_id": thread_id,
            "provider_name": provider_name,
            "action_kind": action_kind,
            "purpose_summary": purpose_summary,
            "resume_strategy": resume_strategy,
            "requires_fresh_provider_session": requires_fresh_provider_session,
            "status": "waiting_operator_sync",
            "created_at": datetime.now(UTC).isoformat(),
            "last_checkpoint": "operator_input_requested",
            "replay_count": 0,
            "last_resume_at": None,
            "last_resume_result": None,
        }
        actions = store.get("actions", [])
        actions.append(action)
        store["actions"] = actions
        self._write_store(store)
        return {
            "ok": True,
            "mode": "operator_resumable_action_create_result",
            "create_status": "resumable_action_created",
            "action": action,
        }

    def submit_offline_sync(self, action_id: str, payload_summary: str) -> Dict[str, Any]:
        store = self._read_store()
        actions: List[Dict[str, Any]] = store.get("actions", [])
        action = next((item for item in actions if item.get("action_id") == action_id), None)
        if action is None:
            return {
                "ok": False,
                "mode": "operator_resumable_action_sync_result",
                "sync_status": "action_not_found",
                "action_id": action_id,
            }
        action["status"] = "sync_received_pending_resume"
        action["offline_payload_summary"] = payload_summary
        self._write_store(store)
        return {
            "ok": True,
            "mode": "operator_resumable_action_sync_result",
            "sync_status": "offline_sync_received",
            "action_id": action_id,
            "resume_strategy": action.get("resume_strategy"),
        }

    def resume_action(self, action_id: str, provider_session_still_valid: bool) -> Dict[str, Any]:
        store = self._read_store()
        actions: List[Dict[str, Any]] = store.get("actions", [])
        action = next((item for item in actions if item.get("action_id") == action_id), None)
        if action is None:
            return {
                "ok": False,
                "mode": "operator_resumable_action_resume_result",
                "resume_status": "action_not_found",
                "action_id": action_id,
            }
        action["replay_count"] = int(action.get("replay_count", 0)) + 1
        action["last_resume_at"] = datetime.now(UTC).isoformat()
        if provider_session_still_valid and not action.get("requires_fresh_provider_session", False):
            action["status"] = "resumed_from_checkpoint"
            action["last_resume_result"] = "continued_from_latest_safe_checkpoint"
        elif provider_session_still_valid and action.get("requires_fresh_provider_session", False):
            action["status"] = "restarted_for_fresh_session"
            action["last_resume_result"] = "provider_flow_restarted_before_reapplying_operator_data"
        else:
            action["status"] = "provider_session_expired_restart_required"
            action["last_resume_result"] = "provider_login_timed_out_restart_required_before_reapplying_operator_data"
        self._write_store(store)
        return {
            "ok": True,
            "mode": "operator_resumable_action_resume_result",
            "resume_status": action["status"],
            "action_id": action_id,
            "replay_count": action["replay_count"],
            "last_resume_result": action["last_resume_result"],
        }

    def list_actions(self, tenant_id: str | None = None, thread_id: str | None = None) -> Dict[str, Any]:
        store = self._read_store()
        actions = store.get("actions", [])
        if tenant_id:
            actions = [item for item in actions if item.get("tenant_id") == tenant_id]
        if thread_id:
            actions = [item for item in actions if item.get("thread_id") == thread_id]
        return {
            "ok": True,
            "mode": "operator_resumable_action_list_result",
            "action_count": len(actions),
            "actions": actions,
        }

    def get_package(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "mode": "operator_resumable_action_package",
            "package": {
                "status": self.get_status(),
                "package_status": "operator_resumable_action_ready",
            },
        }


operator_resumable_action_service = OperatorResumableActionService()
