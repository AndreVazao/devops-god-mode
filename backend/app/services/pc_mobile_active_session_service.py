from typing import Any, Dict, List


class PcMobileActiveSessionService:
    def get_sessions(self) -> Dict[str, Any]:
        sessions: List[Dict[str, Any]] = [
            {
                "pc_mobile_active_session_id": "pc_mobile_active_session_01",
                "local_brain": "pc",
                "remote_cockpit": "mobile",
                "link_state": "connected",
                "session_status": "ready",
            },
            {
                "pc_mobile_active_session_id": "pc_mobile_active_session_02",
                "local_brain": "pc",
                "remote_cockpit": "mobile",
                "link_state": "temporary_mobile_loss_buffering_active",
                "session_status": "ready",
            },
        ]
        return {"ok": True, "mode": "pc_mobile_active_sessions", "sessions": sessions}

    def get_buffer_states(self, target_project: str | None = None) -> Dict[str, Any]:
        buffers: List[Dict[str, Any]] = [
            {
                "buffered_sync_state_id": "buffered_sync_state_01",
                "target_project": "DevOps God Mode",
                "buffer_kind": "queued_mobile_commands_and_pending_results",
                "flush_mode": "flush_when_link_is_stable",
                "buffer_status": "ready",
            },
            {
                "buffered_sync_state_id": "buffered_sync_state_02",
                "target_project": "Bot Farm Headless",
                "buffer_kind": "queued_offline_commands",
                "flush_mode": "flush_after_pc_link_returns",
                "buffer_status": "ready",
            },
            {
                "buffered_sync_state_id": "buffered_sync_state_03",
                "target_project": "Barbudos Studio Website",
                "buffer_kind": "pending_preview_results_for_mobile_review",
                "flush_mode": "flush_when_mobile_opens_session",
                "buffer_status": "ready",
            },
        ]
        if target_project:
            buffers = [item for item in buffers if item["target_project"] == target_project]
        return {"ok": True, "mode": "buffered_sync_states", "buffers": buffers}

    def get_session_package(self) -> Dict[str, Any]:
        package = {
            "sessions": self.get_sessions()["sessions"],
            "buffers": self.get_buffer_states()["buffers"],
            "mobile_compact": True,
            "package_status": "pc_mobile_active_session_ready",
        }
        return {"ok": True, "mode": "pc_mobile_active_session_package", "package": package}

    def get_next_session_action(self) -> Dict[str, Any]:
        first_buffer = self.get_buffer_states()["buffers"][0] if self.get_buffer_states()["buffers"] else None
        return {
            "ok": True,
            "mode": "next_pc_mobile_active_session_action",
            "next_session_action": {
                "buffered_sync_state_id": first_buffer["buffered_sync_state_id"],
                "target_project": first_buffer["target_project"],
                "action": "maintain_buffer_then_flush_when_link_is_stable",
                "buffer_status": first_buffer["buffer_status"],
            }
            if first_buffer
            else None,
        }


pc_mobile_active_session_service = PcMobileActiveSessionService()
