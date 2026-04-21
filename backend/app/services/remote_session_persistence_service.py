from typing import Any, Dict, List


class RemoteSessionPersistenceService:
    def get_sessions(self) -> Dict[str, Any]:
        sessions: List[Dict[str, Any]] = [
            {
                "remote_session_id": "remote_session_android_pc_01",
                "session_scope": "apk_pc_command_context",
                "continuity_mode": "resume_last_compact_state",
                "state_profile": "short_operational_memory",
                "session_status": "resume_ready",
            },
            {
                "remote_session_id": "remote_session_desktop_pc_01",
                "session_scope": "desktop_pc_command_context",
                "continuity_mode": "resume_recent_context",
                "state_profile": "short_operational_memory",
                "session_status": "resume_ready",
            },
        ]
        return {"ok": True, "mode": "remote_session_persistence_sessions", "sessions": sessions}

    def get_session_actions(self, session_area: str | None = None) -> Dict[str, Any]:
        actions: List[Dict[str, Any]] = [
            {
                "remote_session_action_id": "remote_session_action_resume_01",
                "session_area": "state_resume",
                "action_type": "resume_last_confirmed_context",
                "action_label": "Retomar último contexto confirmado",
                "resume_mode": "compact_state_restore",
                "action_status": "planned",
            },
            {
                "remote_session_action_id": "remote_session_action_queue_01",
                "session_area": "pending_command_resume",
                "action_type": "restore_short_pending_queue",
                "action_label": "Restaurar fila curta de pedidos pendentes",
                "resume_mode": "pending_queue_restore",
                "action_status": "planned",
            },
            {
                "remote_session_action_id": "remote_session_action_presence_01",
                "session_area": "session_presence",
                "action_type": "recover_last_known_pc_presence",
                "action_label": "Recuperar última presença conhecida do PC",
                "resume_mode": "presence_restore",
                "action_status": "planned",
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
                "action": "resume_remote_work_without_restarting_flow",
                "action_status": next_action["action_status"],
            }
            if next_action
            else None,
        }


remote_session_persistence_service = RemoteSessionPersistenceService()
