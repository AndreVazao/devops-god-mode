from __future__ import annotations

from typing import Any, Dict, List

from app.services.operator_approval_gate_service import operator_approval_gate_service
from app.services.operator_conversation_thread_service import operator_conversation_thread_service
from app.services.operator_input_request_service import operator_input_request_service


class OperatorPendingAttentionService:
    def get_status(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "mode": "operator_pending_attention_status",
            "status": "operator_pending_attention_ready",
        }

    def build_attention_feed(self, tenant_id: str | None = None) -> Dict[str, Any]:
        threads = operator_conversation_thread_service.list_threads(tenant_id=tenant_id).get("threads", [])
        gates = operator_approval_gate_service.list_gates(tenant_id=tenant_id).get("gates", [])
        requests = operator_input_request_service.list_requests(tenant_id=tenant_id).get("requests", [])

        pending_gates = [g for g in gates if g.get("status") == "awaiting_operator_decision"]
        pending_inputs = [r for r in requests if r.get("status") == "waiting_operator_input"]

        thread_entries: List[Dict[str, Any]] = []
        for thread in threads:
            thread_id = thread.get("thread_id")
            thread_pending_gates = [g for g in pending_gates if g.get("thread_id") == thread_id]
            thread_pending_inputs = [r for r in pending_inputs if r.get("thread_id") == thread_id]
            badge_count = len(thread_pending_gates) + len(thread_pending_inputs)
            thread_entries.append(
                {
                    "thread_id": thread_id,
                    "conversation_title": thread.get("conversation_title"),
                    "tenant_id": thread.get("tenant_id"),
                    "latest_summary": thread.get("latest_summary", ""),
                    "badge_count": badge_count,
                    "has_pending_attention": badge_count > 0,
                    "pending_gate_count": len(thread_pending_gates),
                    "pending_input_count": len(thread_pending_inputs),
                }
            )

        waiting_threads = [entry for entry in thread_entries if entry.get("has_pending_attention")]
        return {
            "ok": True,
            "mode": "operator_pending_attention_result",
            "attention_status": "pending_attention_feed_ready",
            "tenant_id": tenant_id,
            "thread_count": len(thread_entries),
            "waiting_thread_count": len(waiting_threads),
            "pending_gate_count": len(pending_gates),
            "pending_input_count": len(pending_inputs),
            "threads": thread_entries,
        }

    def get_package(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "mode": "operator_pending_attention_package",
            "package": {
                "status": self.get_status(),
                "package_status": "operator_pending_attention_ready",
            },
        }


operator_pending_attention_service = OperatorPendingAttentionService()
