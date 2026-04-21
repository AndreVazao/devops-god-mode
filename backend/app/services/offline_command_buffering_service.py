from typing import Any, Dict, List


class OfflineCommandBufferingService:
    def get_buffers(self) -> Dict[str, Any]:
        buffers: List[Dict[str, Any]] = [
            {
                "offline_command_buffer_id": "offline_buffer_apk_01",
                "buffer_side": "apk",
                "buffer_scope": "voice_and_short_commands",
                "replay_mode": "send_when_pc_returns",
                "buffer_status": "buffer_ready",
            },
            {
                "offline_command_buffer_id": "offline_buffer_pc_01",
                "buffer_side": "pc",
                "buffer_scope": "current_task_continuity",
                "replay_mode": "continue_until_new_orders",
                "buffer_status": "buffer_ready",
            },
        ]
        return {"ok": True, "mode": "offline_command_buffers", "buffers": buffers}

    def get_buffer_actions(self, buffer_area: str | None = None) -> Dict[str, Any]:
        actions: List[Dict[str, Any]] = [
            {
                "offline_buffer_action_id": "offline_buffer_action_replay_01",
                "buffer_area": "apk_pending_queue",
                "action_type": "replay_buffered_commands",
                "action_label": "Reenviar pedidos guardados quando o PC voltar",
                "recovery_mode": "ordered_replay",
                "action_status": "planned",
            },
            {
                "offline_buffer_action_id": "offline_buffer_action_continue_01",
                "buffer_area": "pc_current_task",
                "action_type": "continue_current_task_without_phone",
                "action_label": "Continuar tarefa atual no PC sem telefone",
                "recovery_mode": "continue_until_completion_or_pause",
                "action_status": "planned",
            },
            {
                "offline_buffer_action_id": "offline_buffer_action_sync_01",
                "buffer_area": "dual_side_recovery",
                "action_type": "sync_states_when_link_returns",
                "action_label": "Sincronizar estados quando a ligação regressar",
                "recovery_mode": "state_reconcile_then_resume",
                "action_status": "planned",
            },
        ]
        if buffer_area:
            actions = [item for item in actions if item["buffer_area"] == buffer_area]
        return {"ok": True, "mode": "offline_buffer_actions", "actions": actions}

    def get_buffer_package(self) -> Dict[str, Any]:
        package = {
            "buffers": self.get_buffers()["buffers"],
            "actions": self.get_buffer_actions()["actions"],
            "mobile_compact": True,
            "package_status": "buffer_ready",
        }
        return {"ok": True, "mode": "offline_command_buffer_package", "package": package}

    def get_next_buffer_action(self) -> Dict[str, Any]:
        actions = self.get_buffer_actions()["actions"]
        next_action = actions[0] if actions else None
        return {
            "ok": True,
            "mode": "next_offline_buffer_action",
            "next_buffer_action": {
                "offline_buffer_action_id": next_action["offline_buffer_action_id"],
                "buffer_area": next_action["buffer_area"],
                "action": "buffer_now_and_replay_or_continue_later",
                "action_status": next_action["action_status"],
            }
            if next_action
            else None,
        }


offline_command_buffering_service = OfflineCommandBufferingService()
