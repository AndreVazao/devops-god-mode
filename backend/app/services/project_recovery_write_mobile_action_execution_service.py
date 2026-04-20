from typing import Any, Dict, List

from app.services.project_recovery_write_remote_command_service import (
    project_recovery_write_remote_command_service,
)


class ProjectRecoveryWriteMobileActionExecutionService:
    def get_mobile_executions(self) -> Dict[str, Any]:
        commands = project_recovery_write_remote_command_service.get_remote_commands()["commands"]
        executions: List[Dict[str, Any]] = []
        for command in commands:
            executions.append(
                {
                    "recovery_write_mobile_execution_id": f"mobile_execution_{command['recovery_project_id']}",
                    "recovery_project_id": command["recovery_project_id"],
                    "executable_action_count": command["commandable_item_count"],
                    "executed_action_count": 0,
                    "mobile_execution_status": "awaiting_mobile_execution" if command["pending_command_count"] else "mobile_execution_ready",
                }
            )
        return {"ok": True, "mode": "recovery_write_mobile_executions", "executions": executions}

    def get_mobile_effects(self, recovery_project_id: str | None = None) -> Dict[str, Any]:
        actions = project_recovery_write_remote_command_service.get_remote_actions(recovery_project_id)["actions"]
        effects: List[Dict[str, Any]] = []
        for action in actions:
            pending = action["command_status"] == "pending"
            effects.append(
                {
                    "recovery_write_mobile_effect_id": f"mobile_effect_{action['recovery_write_remote_action_id']}",
                    "recovery_project_id": action["recovery_project_id"],
                    "recovery_write_remote_action_id": action["recovery_write_remote_action_id"],
                    "execution_effect": "approve_and_advance_requested" if pending else "inspect_requested",
                    "downstream_status": "ready_for_executor_step" if pending else "ready_for_review_only",
                    "effect_status": "planned",
                }
            )
        return {"ok": True, "mode": "recovery_write_mobile_effects", "effects": effects}

    def get_mobile_execution_package(self, recovery_project_id: str) -> Dict[str, Any]:
        execution = next(
            item for item in self.get_mobile_executions()["executions"] if item["recovery_project_id"] == recovery_project_id
        )
        package = {
            "execution": execution,
            "effects": self.get_mobile_effects(recovery_project_id)["effects"],
            "mobile_cockpit_ready": True,
            "package_status": execution["mobile_execution_status"],
        }
        return {"ok": True, "mode": "project_recovery_write_mobile_execution_package", "package": package}

    def get_next_mobile_execution(self) -> Dict[str, Any]:
        effects = self.get_mobile_effects()["effects"]
        next_effect = effects[0] if effects else None
        return {
            "ok": True,
            "mode": "next_project_recovery_write_mobile_execution",
            "next_mobile_execution": {
                "recovery_write_mobile_effect_id": next_effect["recovery_write_mobile_effect_id"],
                "recovery_project_id": next_effect["recovery_project_id"],
                "action": "execute_mobile_remote_action_and_prepare_downstream_step",
                "effect_status": next_effect["effect_status"],
            }
            if next_effect
            else None,
        }


project_recovery_write_mobile_action_execution_service = ProjectRecoveryWriteMobileActionExecutionService()
