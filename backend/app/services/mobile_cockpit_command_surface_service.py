from typing import Any, Dict, List

from app.services.browser_control_real_service import browser_control_real_service
from app.services.browser_conversation_intake_service import (
    browser_conversation_intake_service,
)
from app.services.continuous_remote_execution_service import (
    continuous_remote_execution_service,
)
from app.services.offline_command_buffering_service import (
    offline_command_buffering_service,
)
from app.services.operation_queue_service import operation_queue_service
from app.services.remote_session_persistence_service import (
    remote_session_persistence_service,
)
from app.services.runtime_supervisor_guidance_service import (
    runtime_supervisor_guidance_service,
)


class MobileCockpitCommandSurfaceService:
    def _runtime_summary(self) -> Dict[str, Any]:
        return runtime_supervisor_guidance_service.get_summary()["summary"]

    def _session_package(self) -> Dict[str, Any]:
        return remote_session_persistence_service.get_session_package()["package"]

    def _execution_package(self) -> Dict[str, Any]:
        return continuous_remote_execution_service.get_execution_package()["package"]

    def _buffer_package(self) -> Dict[str, Any]:
        return offline_command_buffering_service.get_buffer_package()["package"]

    def get_summary(self) -> Dict[str, Any]:
        runtime_summary = self._runtime_summary()
        next_browser_action = browser_control_real_service.get_next_action()["next_action"]
        next_intent = operation_queue_service.get_next_intent()["next_intent"]
        next_intake = browser_conversation_intake_service.get_next_session()["next_session"]
        session_package = self._session_package()
        execution_package = self._execution_package()
        return {
            "ok": True,
            "mode": "mobile_cockpit_summary",
            "summary": {
                "runtime_status": runtime_summary.get("runtime_health"),
                "recommended_action": runtime_summary.get("recommended_next_action"),
                "link_mode": runtime_summary.get("link_mode"),
                "phone_buffered": session_package["counts"]["phone_buffered"],
                "pc_ready": execution_package["counts"]["pc_ready"],
                "pc_active": execution_package["counts"]["pc_active"],
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
        session_package = self._session_package()
        execution_package = self._execution_package()

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
            },
            {
                "card_id": "card_autonomy_overview",
                "card_type": "autonomy",
                "title": "Autonomia PC + telefone",
                "summary": f"Link {runtime_summary.get('link_mode')} | telefone em buffer {session_package['counts']['phone_buffered']} | PC ativo {execution_package['counts']['pc_active']}",
                "priority": "high",
                "source_mode": "persistent_runtime_state",
                "status": "ready",
            },
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
        runtime_summary = self._runtime_summary()
        session_package = self._session_package()
        buffer_package = self._buffer_package()
        quick_actions: List[Dict[str, Any]] = []

        if session_package["counts"]["phone_buffered"] > 0 and runtime_summary.get("link_mode") in {"both_online", "pc_only"}:
            quick_actions.append(
                {
                    "action_id": "quick_sync_phone_buffer",
                    "action_type": "sync_phone_buffer_to_pc",
                    "label": "Sincronizar pedidos do telefone para o PC",
                    "target_id": "phone_pending_queue",
                    "requires_confirmation": False,
                    "action_status": "ready",
                    "action_payload": {},
                }
            )

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

        if buffer_package["commands"]:
            quick_actions.append(
                {
                    "action_id": "quick_open_pc_autonomy_state",
                    "action_type": "inspect_pc_autonomy_state",
                    "label": "Ver estado da autonomia PC",
                    "target_id": "pc_autonomy_state",
                    "requires_confirmation": False,
                    "action_status": "ready",
                    "action_payload": {},
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
        elif action["action_type"] == "continue_intake":
            payload = action["action_payload"]
            result = browser_conversation_intake_service.get_capture_progress(
                payload["session_id"]
            )
        elif action["action_type"] == "sync_phone_buffer_to_pc":
            result = offline_command_buffering_service.sync_buffered_commands_to_pc()
        else:
            result = {
                "ok": True,
                "mode": "pc_autonomy_state_snapshot",
                "summary": self.get_summary()["summary"],
            }

        return {
            "ok": True,
            "mode": "mobile_cockpit_quick_action_advanced",
            "action_id": action_id,
            "result": result,
        }


mobile_cockpit_command_surface_service = MobileCockpitCommandSurfaceService()
