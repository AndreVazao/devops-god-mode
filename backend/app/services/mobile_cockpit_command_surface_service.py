from typing import Any, Dict, List

from app.services.browser_control_real_service import browser_control_real_service
from app.services.browser_conversation_intake_service import (
    browser_conversation_intake_service,
)
from app.services.operation_queue_service import operation_queue_service
from app.services.runtime_supervisor_guidance_service import (
    runtime_supervisor_guidance_service,
)


class MobileCockpitCommandSurfaceService:
    def _runtime_summary(self) -> Dict[str, Any]:
        return runtime_supervisor_guidance_service.get_summary()["summary"]

    def get_summary(self) -> Dict[str, Any]:
        runtime_summary = self._runtime_summary()
        next_browser_action = browser_control_real_service.get_next_action()["next_action"]
        next_intent = operation_queue_service.get_next_intent()["next_intent"]
        next_intake = browser_conversation_intake_service.get_next_session()["next_session"]
        return {
            "ok": True,
            "mode": "mobile_cockpit_summary",
            "summary": {
                "runtime_status": runtime_summary.get("runtime_health"),
                "recommended_action": runtime_summary.get("recommended_next_action"),
                "next_browser_action_id": next_browser_action["action_id"] if next_browser_action else None,
                "next_intent_id": next_intent["intent_id"] if next_intent else None,
                "next_intake_session_id": next_intake["session_id"] if next_intake else None,
            },
        }

    def get_cards(self) -> Dict[str, Any]:
        runtime_summary = self._runtime_summary()
        next_browser_action = browser_control_real_service.get_next_action()["next_action"]
        next_intent = operation_queue_service.get_next_intent()["next_intent"]
        next_intake = browser_conversation_intake_service.get_next_session()["next_session"]

        cards: List[Dict[str, Any]] = [
            {
                "card_id": "card_runtime_guidance",
                "card_type": "runtime",
                "title": "Estado do runtime",
                "summary": runtime_summary.get("recommended_next_action")
                or "Runtime pronto para orientação operacional.",
                "priority": "high",
                "source_mode": "runtime_supervisor_guidance",
                "status": runtime_summary.get("runtime_health", "ready"),
            }
        ]

        if next_browser_action:
            cards.append(
                {
                    "card_id": "card_browser_next_action",
                    "card_type": "browser_control",
                    "title": "Próxima ação do browser",
                    "summary": f"{next_browser_action['action_type']} em {next_browser_action['target_hint']}",
                    "priority": "high",
                    "source_mode": "browser_control_real",
                    "status": next_browser_action.get("action_status", "ready"),
                }
            )

        if next_intake:
            cards.append(
                {
                    "card_id": "card_intake_next_session",
                    "card_type": "browser_intake",
                    "title": "Próxima sessão de intake",
                    "summary": f"{next_intake['conversation_title']} com objetivo {next_intake['intake_goal']}",
                    "priority": "medium",
                    "source_mode": "browser_conversation_intake",
                    "status": next_intake.get("capture_status", "queued"),
                }
            )

        if next_intent:
            cards.append(
                {
                    "card_id": "card_operation_queue",
                    "card_type": "operation_queue",
                    "title": "Próxima intenção operacional",
                    "summary": next_intent.get("title") or next_intent.get("intent_id"),
                    "priority": "medium",
                    "source_mode": "operation_queue",
                    "status": next_intent.get("intent_status", "queued"),
                }
            )

        return {"ok": True, "mode": "mobile_cockpit_cards", "cards": cards}

    def get_quick_actions(self) -> Dict[str, Any]:
        next_browser_action = browser_control_real_service.get_next_action()["next_action"]
        next_intake = browser_conversation_intake_service.get_next_session()["next_session"]
        quick_actions: List[Dict[str, Any]] = []

        if next_browser_action:
            quick_actions.append(
                {
                    "action_id": "quick_advance_browser_action",
                    "action_type": "advance_browser_action",
                    "label": "Avançar próxima ação do browser",
                    "target_id": next_browser_action["control_id"],
                    "requires_confirmation": True,
                    "action_status": "ready",
                    "action_payload": {
                        "control_id": next_browser_action["control_id"],
                        "action_id": next_browser_action["action_id"],
                    },
                }
            )

        if next_intake:
            quick_actions.append(
                {
                    "action_id": "quick_seed_or_continue_intake",
                    "action_type": "continue_intake",
                    "label": "Continuar intake prioritário",
                    "target_id": next_intake["session_id"],
                    "requires_confirmation": False,
                    "action_status": "ready",
                    "action_payload": {"session_id": next_intake["session_id"]},
                }
            )

        return {
            "ok": True,
            "mode": "mobile_cockpit_quick_actions",
            "quick_actions": quick_actions,
        }

    def get_next_critical_action(self) -> Dict[str, Any]:
        quick_actions = self.get_quick_actions()["quick_actions"]
        return {
            "ok": True,
            "mode": "mobile_cockpit_next_critical_action",
            "next_critical_action": quick_actions[0] if quick_actions else None,
        }

    def advance_quick_action(self, action_id: str) -> Dict[str, Any]:
        quick_actions = self.get_quick_actions()["quick_actions"]
        action = next((item for item in quick_actions if item["action_id"] == action_id), None)
        if not action:
            raise ValueError("quick_action_not_found")

        if action["action_type"] == "advance_browser_action":
            payload = action["action_payload"]
            result = browser_control_real_service.advance_action(
                control_id=payload["control_id"],
                action_id=payload["action_id"],
                completion_note="advanced from mobile cockpit",
            )
        else:
            payload = action["action_payload"]
            result = browser_conversation_intake_service.get_capture_progress(
                payload["session_id"]
            )

        return {
            "ok": True,
            "mode": "mobile_cockpit_quick_action_advanced",
            "action_id": action_id,
            "result": result,
        }


mobile_cockpit_command_surface_service = MobileCockpitCommandSurfaceService()
