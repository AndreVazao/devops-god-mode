from typing import Any, Dict, List


class ContinuousRemoteExecutionService:
    def get_execution_loops(self) -> Dict[str, Any]:
        loops: List[Dict[str, Any]] = [
            {
                "continuous_remote_execution_id": "continuous_remote_execution_01",
                "execution_loop_mode": "apk_pc_compact_command_loop",
                "control_surface": "apk_thin_cockpit",
                "continuity_profile": "short_command_progression",
                "execution_status": "continuous_execution_ready",
            },
            {
                "continuous_remote_execution_id": "continuous_remote_execution_02",
                "execution_loop_mode": "desktop_pc_compact_command_loop",
                "control_surface": "desktop_secondary_surface",
                "continuity_profile": "short_command_progression",
                "execution_status": "continuous_execution_ready",
            },
        ]
        return {"ok": True, "mode": "continuous_remote_execution_loops", "loops": loops}

    def get_execution_actions(self, execution_area: str | None = None) -> Dict[str, Any]:
        actions: List[Dict[str, Any]] = [
            {
                "continuous_execution_action_id": "continuous_execution_action_01",
                "execution_area": "command_progression",
                "action_type": "advance_compact_remote_step",
                "action_label": "Avançar próximo passo remoto compacto",
                "loop_mode": "confirm_then_continue",
                "action_status": "planned",
            },
            {
                "continuous_execution_action_id": "continuous_execution_action_02",
                "execution_area": "status_refresh",
                "action_type": "refresh_compact_state_between_steps",
                "action_label": "Atualizar estado compacto entre passos",
                "loop_mode": "stepwise_refresh",
                "action_status": "planned",
            },
            {
                "continuous_execution_action_id": "continuous_execution_action_03",
                "execution_area": "confirmation_loop",
                "action_type": "keep_short_confirmations_until_task_done",
                "action_label": "Manter confirmações curtas até concluir tarefa",
                "loop_mode": "short_confirm_cycle",
                "action_status": "planned",
            },
        ]
        if execution_area:
            actions = [item for item in actions if item["execution_area"] == execution_area]
        return {"ok": True, "mode": "continuous_remote_execution_actions", "actions": actions}

    def get_execution_package(self) -> Dict[str, Any]:
        package = {
            "loops": self.get_execution_loops()["loops"],
            "actions": self.get_execution_actions()["actions"],
            "mobile_compact": True,
            "package_status": "continuous_execution_ready",
        }
        return {"ok": True, "mode": "continuous_remote_execution_package", "package": package}

    def get_next_execution_action(self) -> Dict[str, Any]:
        actions = self.get_execution_actions()["actions"]
        next_action = actions[0] if actions else None
        return {
            "ok": True,
            "mode": "next_continuous_remote_execution_action",
            "next_execution_action": {
                "continuous_execution_action_id": next_action["continuous_execution_action_id"],
                "execution_area": next_action["execution_area"],
                "action": "advance_remote_task_without_breaking_flow",
                "action_status": next_action["action_status"],
            }
            if next_action
            else None,
        }


continuous_remote_execution_service = ContinuousRemoteExecutionService()
