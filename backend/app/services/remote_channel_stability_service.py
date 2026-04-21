from typing import Any, Dict, List


class RemoteChannelStabilityService:
    def get_channels(self) -> Dict[str, Any]:
        channels: List[Dict[str, Any]] = [
            {
                "remote_channel_id": "remote_channel_android_pc_01",
                "channel_mode": "apk_to_pc_command_state",
                "transport_role": "pc_brain_primary_link",
                "resilience_profile": "retry_resume_compact_state",
                "channel_status": "stable_link_planned",
            },
            {
                "remote_channel_id": "remote_channel_desktop_pc_01",
                "channel_mode": "desktop_to_pc_command_state",
                "transport_role": "pc_brain_secondary_link",
                "resilience_profile": "fast_refresh_compact_state",
                "channel_status": "stable_link_planned",
            },
        ]
        return {"ok": True, "mode": "remote_channel_stability_channels", "channels": channels}

    def get_channel_actions(self, channel_area: str | None = None) -> Dict[str, Any]:
        actions: List[Dict[str, Any]] = [
            {
                "remote_channel_action_id": "remote_channel_action_retry_01",
                "channel_area": "transport_resilience",
                "action_type": "retry_and_resume_compact_state",
                "action_label": "Repetir pedido e retomar estado compacto",
                "fallback_mode": "cached_last_state",
                "action_status": "planned",
            },
            {
                "remote_channel_action_id": "remote_channel_action_queue_01",
                "channel_area": "command_queue",
                "action_type": "queue_short_commands_until_pc_ack",
                "action_label": "Enfileirar pedidos curtos até confirmação do PC",
                "fallback_mode": "local_pending_queue",
                "action_status": "planned",
            },
            {
                "remote_channel_action_id": "remote_channel_action_presence_01",
                "channel_area": "presence_sync",
                "action_type": "sync_compact_online_state",
                "action_label": "Sincronizar estado online compacto do PC",
                "fallback_mode": "last_seen_status",
                "action_status": "planned",
            },
        ]
        if channel_area:
            actions = [item for item in actions if item["channel_area"] == channel_area]
        return {"ok": True, "mode": "remote_channel_stability_actions", "actions": actions}

    def get_channel_package(self) -> Dict[str, Any]:
        package = {
            "channels": self.get_channels()["channels"],
            "actions": self.get_channel_actions()["actions"],
            "mobile_compact": True,
            "package_status": "stable_link_planned",
        }
        return {"ok": True, "mode": "remote_channel_stability_package", "package": package}

    def get_next_channel_action(self) -> Dict[str, Any]:
        actions = self.get_channel_actions()["actions"]
        next_action = actions[0] if actions else None
        return {
            "ok": True,
            "mode": "next_remote_channel_action",
            "next_channel_action": {
                "remote_channel_action_id": next_action["remote_channel_action_id"],
                "channel_area": next_action["channel_area"],
                "action": "stabilize_remote_path_between_apk_and_pc",
                "action_status": next_action["action_status"],
            }
            if next_action
            else None,
        }


remote_channel_stability_service = RemoteChannelStabilityService()
