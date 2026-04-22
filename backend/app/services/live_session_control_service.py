from typing import Any, Dict, List


class LiveSessionControlService:
    def get_controls(self) -> Dict[str, Any]:
        controls: List[Dict[str, Any]] = [
            {
                "live_session_control_id": "live_session_control_01",
                "local_brain": "pc",
                "remote_cockpit": "mobile",
                "control_mode": "active_remote_control",
                "control_status": "ready",
            },
            {
                "live_session_control_id": "live_session_control_02",
                "local_brain": "pc",
                "remote_cockpit": "mobile",
                "control_mode": "degraded_control_buffering_only",
                "control_status": "ready",
            },
        ]
        return {"ok": True, "mode": "live_session_controls", "controls": controls}

    def get_recovery_actions(self, target_project: str | None = None) -> Dict[str, Any]:
        actions: List[Dict[str, Any]] = [
            {
                "session_recovery_action_id": "session_recovery_action_01",
                "target_project": "DevOps God Mode",
                "recovery_kind": "resume_after_link_restoration",
                "resume_mode": "flush_buffer_and_restore_live_control",
                "action_status": "ready",
            },
            {
                "session_recovery_action_id": "session_recovery_action_02",
                "target_project": "Bot Farm Headless",
                "recovery_kind": "resume_after_mobile_return",
                "resume_mode": "flush_queued_commands_then_continue_lane",
                "action_status": "ready",
            },
            {
                "session_recovery_action_id": "session_recovery_action_03",
                "target_project": "Barbudos Studio Website",
                "recovery_kind": "restore_preview_review_loop",
                "resume_mode": "deliver_pending_previews_when_mobile_session_recovers",
                "action_status": "ready",
            },
        ]
        if target_project:
            actions = [item for item in actions if item["target_project"] == target_project]
        return {"ok": True, "mode": "session_recovery_actions", "actions": actions}

    def get_control_package(self) -> Dict[str, Any]:
        package = {
            "controls": self.get_controls()["controls"],
            "actions": self.get_recovery_actions()["actions"],
            "mobile_compact": True,
            "package_status": "live_session_control_ready",
        }
        return {"ok": True, "mode": "live_session_control_package", "package": package}

    def get_next_control_action(self) -> Dict[str, Any]:
        first_action = self.get_recovery_actions()["actions"][0] if self.get_recovery_actions()["actions"] else None
        return {
            "ok": True,
            "mode": "next_live_session_control_action",
            "next_control_action": {
                "session_recovery_action_id": first_action["session_recovery_action_id"],
                "target_project": first_action["target_project"],
                "action": "restore_live_control_after_buffer_flush",
                "action_status": first_action["action_status"],
            }
            if first_action
            else None,
        }


live_session_control_service = LiveSessionControlService()
