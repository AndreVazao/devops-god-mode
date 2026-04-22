from typing import Any, Dict, List

from app.services.offline_command_buffering_service import (
    offline_command_buffering_service,
)
from app.services.remote_session_persistence_service import (
    remote_session_persistence_service,
)


class ContinuousRemoteExecutionService:
    def _command_groups(self) -> Dict[str, List[Dict[str, Any]]]:
        commands = offline_command_buffering_service.get_commands()["commands"]
        return {
            "pc_ready": [
                item
                for item in commands
                if item.get("sync_status") == "ready_for_pc_execution"
                and item.get("execution_status") == "queued"
            ],
            "pc_active": [
                item
                for item in commands
                if item.get("execution_status") in {"executing", "waiting_for_clarification", "paused"}
            ],
            "phone_buffered": [
                item
                for item in commands
                if item.get("sync_status") == "buffered_on_phone_until_pc_returns"
            ],
            "completed": [
                item for item in commands if item.get("execution_status") == "completed"
            ],
        }

    def get_execution_loops(self) -> Dict[str, Any]:
        connectivity = offline_command_buffering_service.get_connectivity()["connectivity"]
        groups = self._command_groups()
        loops: List[Dict[str, Any]] = [
            {
                "continuous_remote_execution_id": "continuous_remote_execution_01",
                "execution_loop_mode": "phone_to_pc_autonomy_loop",
                "control_surface": "phone_thin_cockpit",
                "continuity_profile": "pc_continues_until_finished_or_blocked",
                "pending_count": len(groups["phone_buffered"]),
                "link_mode": connectivity["link_mode"],
                "execution_status": (
                    "waiting_for_pc_return"
                    if groups["phone_buffered"] and not connectivity["pc_online"]
                    else "continuous_execution_ready"
                ),
            },
            {
                "continuous_remote_execution_id": "continuous_remote_execution_02",
                "execution_loop_mode": "pc_direct_autonomy_loop",
                "control_surface": "pc_primary_surface",
                "continuity_profile": "pc_continues_after_single_order",
                "pending_count": len(groups["pc_ready"]) + len(groups["pc_active"]),
                "link_mode": connectivity["link_mode"],
                "execution_status": (
                    "clarification_needed"
                    if any(
                        item.get("execution_status") == "waiting_for_clarification"
                        for item in groups["pc_active"]
                    )
                    else "continuous_execution_ready"
                    if connectivity["pc_online"]
                    else "waiting_for_pc"
                ),
            },
        ]
        return {"ok": True, "mode": "continuous_remote_execution_loops", "loops": loops}

    def get_execution_actions(self, execution_area: str | None = None) -> Dict[str, Any]:
        connectivity = offline_command_buffering_service.get_connectivity()["connectivity"]
        groups = self._command_groups()
        session_package = remote_session_persistence_service.get_session_package()["package"]
        clarification_needed = any(
            item.get("execution_status") == "waiting_for_clarification"
            for item in groups["pc_active"]
        )
        actions: List[Dict[str, Any]] = [
            {
                "continuous_execution_action_id": "continuous_execution_action_01",
                "execution_area": "autonomous_progression",
                "action_type": "continue_work_until_finished_or_clarification",
                "action_label": "Continuar trabalho até terminar ou surgir bloqueio real",
                "loop_mode": "single_order_long_run",
                "pending_count": len(groups["pc_ready"]) + len(groups["pc_active"]),
                "action_status": "ready" if connectivity["pc_online"] else "waiting_for_pc",
            },
            {
                "continuous_execution_action_id": "continuous_execution_action_02",
                "execution_area": "clarification_gate",
                "action_type": "ask_only_when_missing_direction_blocks_progress",
                "action_label": "Perguntar só quando faltar direção real",
                "loop_mode": "blocker_only_questions",
                "pending_count": len(
                    [
                        item
                        for item in groups["pc_active"]
                        if item.get("execution_status") == "waiting_for_clarification"
                    ]
                ),
                "action_status": "ready" if clarification_needed else "idle",
            },
            {
                "continuous_execution_action_id": "continuous_execution_action_03",
                "execution_area": "offline_continuity",
                "action_type": "keep_pc_running_even_if_phone_disconnects",
                "action_label": "Manter o PC a trabalhar mesmo se o telefone cair",
                "loop_mode": "pc_independent_execution",
                "pending_count": session_package["counts"]["pc_active"] + session_package["counts"]["pc_ready"],
                "action_status": "ready" if connectivity["pc_online"] else "waiting_for_pc",
            },
            {
                "continuous_execution_action_id": "continuous_execution_action_04",
                "execution_area": "phone_replay",
                "action_type": "replay_phone_orders_to_pc_when_link_returns",
                "action_label": "Passar pedidos do telefone para o PC quando o link regressar",
                "loop_mode": "ordered_replay_then_execute",
                "pending_count": len(groups["phone_buffered"]),
                "action_status": (
                    "ready"
                    if connectivity["pc_online"] and groups["phone_buffered"]
                    else "waiting_for_pc"
                    if groups["phone_buffered"]
                    else "idle"
                ),
            },
        ]
        if execution_area:
            actions = [item for item in actions if item["execution_area"] == execution_area]
        return {"ok": True, "mode": "continuous_remote_execution_actions", "actions": actions}

    def get_execution_package(self) -> Dict[str, Any]:
        connectivity = offline_command_buffering_service.get_connectivity()["connectivity"]
        groups = self._command_groups()
        package = {
            "loops": self.get_execution_loops()["loops"],
            "actions": self.get_execution_actions()["actions"],
            "connectivity": connectivity,
            "mobile_compact": True,
            "autonomy_rule": "pc_keeps_working_after_single_order",
            "question_rule": "ask_only_for_real_missing_direction",
            "counts": {
                "pc_ready": len(groups["pc_ready"]),
                "pc_active": len(groups["pc_active"]),
                "phone_buffered": len(groups["phone_buffered"]),
                "completed": len(groups["completed"]),
            },
            "package_status": "continuous_execution_ready",
        }
        return {"ok": True, "mode": "continuous_remote_execution_package", "package": package}

    def get_next_execution_action(self) -> Dict[str, Any]:
        actions = self.get_execution_actions()["actions"]
        next_action = next(
            (item for item in actions if item.get("action_status") == "ready"),
            actions[0] if actions else None,
        )
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
