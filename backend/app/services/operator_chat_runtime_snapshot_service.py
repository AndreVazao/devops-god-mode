from __future__ import annotations

from typing import Any, Dict

from app.services.operator_action_journal_service import operator_action_journal_service
from app.services.operator_approval_gate_service import operator_approval_gate_service
from app.services.operator_conversation_thread_service import operator_conversation_thread_service
from app.services.operator_input_request_service import operator_input_request_service
from app.services.operator_pending_attention_service import operator_pending_attention_service
from app.services.operator_popup_delivery_service import operator_popup_delivery_service
from app.services.operator_resumable_action_service import operator_resumable_action_service
from app.services.operator_response_guidance_service import operator_response_guidance_service


class OperatorChatRuntimeSnapshotService:
    def get_status(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "mode": "operator_chat_runtime_snapshot_status",
            "status": "operator_chat_runtime_snapshot_ready",
        }

    def build_snapshot(self, tenant_id: str, thread_id: str | None = None) -> Dict[str, Any]:
        threads_result = operator_conversation_thread_service.list_threads(tenant_id=tenant_id)
        attention = operator_pending_attention_service.build_attention_feed(tenant_id=tenant_id)
        journal = operator_action_journal_service.list_entries(tenant_id=tenant_id, limit=25)
        threads = threads_result.get("threads", [])
        active_thread = None
        guidance = None
        input_requests = []
        approval_gates = []
        popup_deliveries = []
        resumable_actions = []
        thread_journal_entries = []

        if thread_id:
            active_thread = operator_conversation_thread_service.get_thread(thread_id=thread_id)
            guidance = operator_response_guidance_service.build_guidance(thread_id=thread_id)
            input_requests = operator_input_request_service.list_requests(thread_id=thread_id).get("requests", [])
            approval_gates = operator_approval_gate_service.list_gates(thread_id=thread_id).get("gates", [])
            popup_deliveries = operator_popup_delivery_service.list_deliveries(thread_id=thread_id).get("deliveries", [])
            resumable_actions = operator_resumable_action_service.list_actions(thread_id=thread_id).get("actions", [])
            thread_journal_entries = operator_action_journal_service.list_entries(thread_id=thread_id, limit=50).get("entries", [])

        return {
            "ok": True,
            "mode": "operator_chat_runtime_snapshot_result",
            "snapshot_status": "operator_chat_runtime_snapshot_ready",
            "tenant_id": tenant_id,
            "thread_count": len(threads),
            "waiting_thread_count": attention.get("waiting_thread_count", 0),
            "pending_gate_count": attention.get("pending_gate_count", 0),
            "pending_input_count": attention.get("pending_input_count", 0),
            "journal_entry_count": journal.get("entry_count", 0),
            "threads": threads,
            "attention": attention,
            "active_thread": active_thread,
            "guidance": guidance,
            "input_requests": input_requests,
            "approval_gates": approval_gates,
            "popup_deliveries": popup_deliveries,
            "resumable_actions": resumable_actions,
            "journal_entries": journal.get("entries", []),
            "thread_journal_entries": thread_journal_entries,
        }

    def get_package(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "mode": "operator_chat_runtime_snapshot_package",
            "package": {
                "status": self.get_status(),
                "package_status": "operator_chat_runtime_snapshot_ready",
            },
        }


operator_chat_runtime_snapshot_service = OperatorChatRuntimeSnapshotService()
