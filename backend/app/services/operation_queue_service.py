from typing import Any, Dict, List

from app.services.action_center_service import action_center_service
from app.services.runtime_supervisor_guidance_service import runtime_supervisor_guidance_service


class OperationQueueService:
    def _build_queue(self) -> List[Dict[str, Any]]:
        quick_actions = action_center_service.get_quick_actions()["quick_actions"]
        recommended = runtime_supervisor_guidance_service.get_recommended_next_action()[
            "recommended_next_action"
        ]

        queue: List[Dict[str, Any]] = []
        for action in quick_actions:
            queue.append(
                {
                    "intent_id": f"intent_{action}",
                    "source": "action_center",
                    "runtime_mode": "pc_and_phone_primary",
                    "action_name": action,
                    "priority": "high" if action == recommended else "normal",
                    "requires_approval": action.startswith("start_"),
                    "preview_summary": f"Prepare operation for {action}.",
                    "intent_status": "queued",
                }
            )
        return queue

    def get_queue(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "mode": "operation_queue",
            "queue": self._build_queue(),
        }

    def get_next_intent(self) -> Dict[str, Any]:
        queue = self._build_queue()
        next_intent = queue[0] if queue else None
        return {
            "ok": True,
            "mode": "operation_next_intent",
            "next_intent": next_intent,
        }

    def get_preview(self) -> Dict[str, Any]:
        next_intent = self.get_next_intent()["next_intent"]
        return {
            "ok": True,
            "mode": "operation_intent_preview",
            "preview": {
                "intent_id": next_intent["intent_id"] if next_intent else None,
                "action_name": next_intent["action_name"] if next_intent else None,
                "requires_approval": next_intent["requires_approval"] if next_intent else False,
                "preview_summary": next_intent["preview_summary"] if next_intent else None,
            },
        }


operation_queue_service = OperationQueueService()
