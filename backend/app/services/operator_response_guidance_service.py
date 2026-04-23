from __future__ import annotations

from typing import Any, Dict, List

from app.services.operator_conversation_thread_service import operator_conversation_thread_service


class OperatorResponseGuidanceService:
    def get_status(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "mode": "operator_response_guidance_status",
            "status": "operator_response_guidance_ready",
        }

    def build_guidance(self, thread_id: str) -> Dict[str, Any]:
        thread_result = operator_conversation_thread_service.get_thread(thread_id=thread_id)
        if not thread_result.get("ok"):
            return {
                "ok": False,
                "mode": "operator_response_guidance_result",
                "guidance_status": "thread_not_found",
                "thread_id": thread_id,
            }
        thread = thread_result["thread"]
        messages = thread.get("messages", [])
        last_user = next((item for item in reversed(messages) if item.get("role") == "user"), None)
        latest_summary = thread.get("latest_summary", "")
        next_steps: List[str] = thread.get("suggested_next_steps", [])
        reply = {
            "thread_id": thread_id,
            "conversation_title": thread.get("conversation_title"),
            "reply_mode": "continuous_operator_conversation",
            "latest_summary": latest_summary,
            "last_user_message": last_user.get("content") if last_user else "",
            "operator_visible_state": "God Mode is processing the current thread and preserving tenant context.",
            "suggested_next_steps": next_steps,
        }
        return {
            "ok": True,
            "mode": "operator_response_guidance_result",
            "guidance_status": "operator_guidance_ready",
            "reply": reply,
        }

    def get_package(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "mode": "operator_response_guidance_package",
            "package": {
                "status": self.get_status(),
                "package_status": "operator_response_guidance_ready",
            },
        }


operator_response_guidance_service = OperatorResponseGuidanceService()
