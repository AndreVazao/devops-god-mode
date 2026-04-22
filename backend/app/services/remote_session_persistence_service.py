from typing import Any, Dict, List


class RemoteSessionPersistenceService:
    def get_sessions(self) -> Dict[str, Any]:
        sessions: List[Dict[str, Any]] = [
            {
                "remote_session_id": "remote_session_phone_pc_01",
                "session_scope": "phone_requests_waiting_for_pc_return",
                "continuity_mode": "store_on_phone_then_send_to_pc",
                "state_profile": "pending_orders_and_context",
                "session_status": "resume_ready",
            },
            {
                "remote_session_id": "remote_session_pc_01",
                "session_scope": "pc_long_running_work_context",
                "continuity_mode": "continue_without_phone_until_blocked_or_finished",
                "state_profile": "active_work_and_clarification_gates",
                "session_status": "resume_ready",
            },
        ]
        return {"ok": True, "mode": "remote_session_persistence_sessions", "sessions": sessions}

    def get_session_actions(self, session_area: str | None = None) -> Dict[str, Any]:
        actions: List[Dict[str, Any]] = [
            {
                "remote_session_action_id": "remote_session_action_resume_01",
                "session_area": "pc_resume",
                "action_type": "resume_long_running_pc_context",
                "action_label": "Retomar contexto longo no PC sem reiniciar o fluxo",
                "resume_mode": "continue_until_blocked_or_finished",
                "action_status": "ready",
            },
            {
                "remote_session_action_id": "remote_session_action_queue_01",
                "session_area": "phone_buffer_recovery",
                "action_type": "restore_phone_pending_orders_for_pc_delivery",
                "action_label": "Restaurar pedidos guardados no telefone para enviar ao PC",
                "resume_mode": "ordered_delivery_when_pc_returns",
                "action_status": "ready",
            },
            {
                "remote_session_action_id": "remote_session_action_presence_01",
                "session_area": "connectivity_memory",
                "action_type": "recover_last_known_connectivity_state",
                "action_label": "Recuperar último estado conhecido entre PC e telefone",
                "resume_mode": "presence_restore",
                "action_status": "ready",
            },
        ]
        if session_area:
            actions = [item for item in actions if item["session_area"] == session_area]
        return {"ok": True, "mode": "remote_session_persistence_actions", "actions": actions}

    def get_session_package(self) -> Dict[str, Any]:
        package = {
            "sessions": self.get_sessions()["sessions"],
            "actions": self.get_session_actions()["actions"],
            "mobile_compact": True,
            "offline_rule": "phone_keeps_orders_until_pc_returns",
            "pc_rule": "pc_keeps_working_without_phone",
            "package_status": "resume_ready",
        }
        return {"ok": True, "mode": "remote_session_persistence_package", "package": package}

    def get_next_session_action(self) -> Dict[str, Any]:
        actions = self.get_session_actions()["actions"]
        next_action = actions[0] if actions else None
        return {
            "ok": True,
            "mode": "next_remote_session_action",
            "next_session_action": {
                "remote_session_action_id": next_action["remote_session_action_id"],
                "session_area": next_action["session_area"],
                "action": next_action["action_type"],
                "action_status": next_action["action_status"],
            }
            if next_action
            else None,
        }


remote_session_persistence_service = RemoteSessionPersistenceService()
