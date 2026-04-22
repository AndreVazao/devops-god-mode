from typing import Any, Dict, List


class ContinuousRemoteExecutionService:
    def get_execution_loops(self) -> Dict[str, Any]:
        loops: List[Dict[str, Any]] = [
            {
                "continuous_remote_execution_id": "continuous_remote_execution_01",
                "execution_loop_mode": "phone_to_pc_autonomy_loop",
                "control_surface": "phone_thin_cockpit",
                "continuity_profile": "pc_continues_until_finished_or_blocked",
                "execution_status": "continuous_execution_ready",
            },
            {
                "continuous_remote_execution_id": "continuous_remote_execution_02",
                "execution_loop_mode": "pc_direct_autonomy_loop",
                "control_surface": "pc_primary_surface",
                "continuity_profile": "pc_continues_after_single_order",
                "execution_status": "continuous_execution_ready",
            },
        ]
        return {"ok": True, "mode": "continuous_remote_execution_loops", "loops": loops}

    def get_execution_actions(self, execution_area: str | None = None) -> Dict[str, Any]:
        actions: List[Dict[str, Any]] = [
            {
                "continuous_execution_action_id": "continuous_execution_action_01",
                "execution_area": "autonomous_progression",
                "action_type": "continue_work_until_finished_or_clarification",
                "action_label": "Continuar trabalho até terminar ou surgir bloqueio real",
                "loop_mode": "single_order_long_run",
                "action_status": "ready",
            },
            {
                "continuous_execution_action_id": "continuous_execution_action_02",
                "execution_area": "clarification_gate",
                "action_type": "ask_only_when_missing_direction_blocks_progress",
                "action_label": "Perguntar só quando faltar direção real",
                "loop_mode": "blocker_only_questions",
                "action_status": "ready",
            },
            {
                "continuous_execution_action_id": "continuous_execution_action_03",
                "execution_area": "offline_continuity",
                "action_type": "keep_pc_running_even_if_phone_disconnects",
                "action_label": "Manter o PC a trabalhar mesmo se o telefone cair",
                "loop_mode": "pc_independent_execution",
                "action_status": "ready",
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
            "autonomy_rule": "pc_keeps_working_after_single_order",
            "question_rule": "ask_only_for_real_missing_direction",
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
                "action": next_action["action_type"],
                "action_status": next_action["action_status"],
            }
            if next_action
            else None,
        }


continuous_remote_execution_service = ContinuousRemoteExecutionService()
