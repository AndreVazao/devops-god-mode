from typing import Any, Dict, List

from app.services.adaptation_planner_service import adaptation_planner_service
from app.services.browser_control_real_service import browser_control_real_service
from app.services.browser_conversation_intake_service import (
    browser_conversation_intake_service,
)
from app.services.driving_mode_voice_first_service import (
    driving_mode_voice_first_service,
)
from app.services.mobile_cockpit_command_surface_service import (
    mobile_cockpit_command_surface_service,
)
from app.services.operation_queue_service import operation_queue_service


class ContextAwareOrchestrationService:
    def get_context_summary(self) -> Dict[str, Any]:
        browser_next = browser_control_real_service.get_next_action()["next_action"]
        intake_next = browser_conversation_intake_service.get_next_session()["next_session"]
        mobile_next = mobile_cockpit_command_surface_service.get_next_critical_action()[
            "next_critical_action"
        ]
        driving_next = driving_mode_voice_first_service.get_next_safe_action()[
            "next_safe_action"
        ]
        adaptation_best = adaptation_planner_service.get_best_plans()["best_plans"]
        operation_next = operation_queue_service.get_next_intent()["next_intent"]
        return {
            "ok": True,
            "mode": "context_summary",
            "summary": {
                "browser_next_action_id": browser_next["action_id"] if browser_next else None,
                "intake_next_session_id": intake_next["session_id"] if intake_next else None,
                "mobile_next_action_id": mobile_next["action_id"] if mobile_next else None,
                "driving_next_action_id": driving_next["action_id"] if driving_next else None,
                "best_adaptation_id": adaptation_best[0]["adaptation_id"] if adaptation_best else None,
                "operation_next_intent_id": operation_next["intent_id"] if operation_next else None,
            },
        }

    def get_lanes(self) -> Dict[str, Any]:
        browser_next = browser_control_real_service.get_next_action()["next_action"]
        intake_next = browser_conversation_intake_service.get_next_session()["next_session"]
        adaptation_best = adaptation_planner_service.get_best_plans()["best_plans"]
        operation_next = operation_queue_service.get_next_intent()["next_intent"]

        lanes: List[Dict[str, Any]] = []

        if browser_next:
            lanes.append(
                {
                    "lane_id": "lane_browser_and_mobile",
                    "lane_type": "assisted_execution",
                    "priority": "high",
                    "source_modes": [
                        "browser_control_real",
                        "mobile_cockpit_command_surface",
                        "driving_mode_voice_first",
                    ],
                    "lane_summary": "Advance the next browser action through mobile confirmation because the context is ready and guarded.",
                    "lane_status": "ready",
                }
            )

        if intake_next:
            lanes.append(
                {
                    "lane_id": "lane_intake_progression",
                    "lane_type": "capture_progression",
                    "priority": "medium",
                    "source_modes": [
                        "browser_conversation_intake",
                        "conversation_organization",
                    ],
                    "lane_summary": "Continue intake on the prioritized conversation session to improve context quality.",
                    "lane_status": "ready",
                }
            )

        if adaptation_best:
            lanes.append(
                {
                    "lane_id": "lane_adaptation_review",
                    "lane_type": "adaptation_review",
                    "priority": "medium",
                    "source_modes": ["adaptation_planner", "script_extraction_reuse"],
                    "lane_summary": "Review the strongest adaptation candidate after execution pressure is reduced.",
                    "lane_status": "ready",
                }
            )

        if operation_next:
            lanes.append(
                {
                    "lane_id": "lane_operation_queue",
                    "lane_type": "queue_followup",
                    "priority": "medium",
                    "source_modes": ["operation_queue", "mobile_cockpit_command_surface"],
                    "lane_summary": "Keep the next operation intent visible for follow-up after the browser lane.",
                    "lane_status": "ready",
                }
            )

        return {"ok": True, "mode": "orchestration_lanes", "lanes": lanes}

    def get_next_decision(self) -> Dict[str, Any]:
        browser_next = browser_control_real_service.get_next_action()["next_action"]
        driving_next = driving_mode_voice_first_service.get_next_safe_action()[
            "next_safe_action"
        ]
        intake_next = browser_conversation_intake_service.get_next_session()["next_session"]
        adaptation_best = adaptation_planner_service.get_best_plans()["best_plans"]

        decision = None
        if browser_next and driving_next:
            decision = {
                "decision_id": "decision_advance_browser_then_resume_intake",
                "decision_type": "advance_assisted_action",
                "target_mode": "browser_control_real",
                "target_id": driving_next["action_id"],
                "confidence_score": 0.92,
                "requires_confirmation": driving_next["requires_voice_confirmation"],
                "decision_reason": "browser control has next critical action ready and driving mode guard allows safe assisted confirmation",
                "decision_status": "ready",
            }
        elif intake_next:
            decision = {
                "decision_id": "decision_continue_prioritized_intake",
                "decision_type": "continue_capture",
                "target_mode": "browser_conversation_intake",
                "target_id": intake_next["session_id"],
                "confidence_score": 0.84,
                "requires_confirmation": False,
                "decision_reason": "no guarded browser action is waiting, so intake progression is the strongest next step",
                "decision_status": "ready",
            }
        elif adaptation_best:
            decision = {
                "decision_id": "decision_review_best_adaptation",
                "decision_type": "review_adaptation",
                "target_mode": "adaptation_planner",
                "target_id": adaptation_best[0]["adaptation_id"],
                "confidence_score": 0.78,
                "requires_confirmation": False,
                "decision_reason": "execution pressure is low, so the best adaptation candidate becomes the next useful review task",
                "decision_status": "ready",
            }

        return {"ok": True, "mode": "context_next_decision", "next_decision": decision}

    def get_action_split(self) -> Dict[str, Any]:
        next_decision = self.get_next_decision()["next_decision"]
        safe_actions: List[Dict[str, Any]] = []
        guarded_actions: List[Dict[str, Any]] = []
        if next_decision:
            if next_decision["requires_confirmation"]:
                guarded_actions.append(next_decision)
            else:
                safe_actions.append(next_decision)
        return {
            "ok": True,
            "mode": "context_action_split",
            "safe_actions": safe_actions,
            "guarded_actions": guarded_actions,
        }

    def apply_next_decision(self) -> Dict[str, Any]:
        decision = self.get_next_decision()["next_decision"]
        if not decision:
            return {
                "ok": True,
                "mode": "context_decision_applied",
                "result": "no_decision_available",
            }

        if decision["target_mode"] == "browser_control_real":
            result = driving_mode_voice_first_service.confirm_short_action("sim")
        elif decision["target_mode"] == "browser_conversation_intake":
            result = browser_conversation_intake_service.get_capture_progress(
                decision["target_id"]
            )
        else:
            result = adaptation_planner_service.get_best_plans()

        return {
            "ok": True,
            "mode": "context_decision_applied",
            "decision_id": decision["decision_id"],
            "result": result,
        }


context_aware_orchestration_service = ContextAwareOrchestrationService()
