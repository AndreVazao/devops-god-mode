from typing import Any, Dict, List

from app.services.project_recovery_write_approval_cockpit_service import (
    project_recovery_write_approval_cockpit_service,
)


class ProjectRecoveryWriteRemoteCommandService:
    def get_remote_commands(self) -> Dict[str, Any]:
        cockpits = project_recovery_write_approval_cockpit_service.get_cockpits()["cockpits"]
        commands: List[Dict[str, Any]] = []
        for cockpit in cockpits:
            commands.append(
                {
                    "recovery_write_remote_command_id": f"remote_command_{cockpit['recovery_project_id']}",
                    "recovery_project_id": cockpit["recovery_project_id"],
                    "commandable_item_count": cockpit["pending_approval_count"] + cockpit["ready_target_count"],
                    "pending_command_count": cockpit["pending_approval_count"],
                    "remote_status": "mobile_command_attention_required" if cockpit["pending_approval_count"] else "mobile_command_ready",
                }
            )
        return {"ok": True, "mode": "recovery_write_remote_commands", "commands": commands}

    def get_remote_actions(self, recovery_project_id: str | None = None) -> Dict[str, Any]:
        items = project_recovery_write_approval_cockpit_service.get_approval_items(recovery_project_id)["items"]
        actions: List[Dict[str, Any]] = []
        for item in items:
            pending = item["approval_status"] == "pending"
            action_type = "approve_and_advance" if pending else "inspect_or_skip"
            actions.append(
                {
                    "recovery_write_remote_action_id": f"remote_{item['recovery_write_approval_item_id']}",
                    "recovery_project_id": item["recovery_project_id"],
                    "recovery_write_approval_item_id": item["recovery_write_approval_item_id"],
                    "command_type": action_type,
                    "command_label": item["mobile_action_label"] if pending else f"Inspecionar {item['recovery_write_approval_item_id']}",
                    "command_status": "pending" if pending else "available",
                }
            )
        return {"ok": True, "mode": "recovery_write_remote_actions", "actions": actions}

    def get_remote_command_package(self, recovery_project_id: str) -> Dict[str, Any]:
        command = next(
            item for item in self.get_remote_commands()["commands"] if item["recovery_project_id"] == recovery_project_id
        )
        package = {
            "command": command,
            "actions": self.get_remote_actions(recovery_project_id)["actions"],
            "mobile_cockpit_ready": True,
            "package_status": command["remote_status"],
        }
        return {"ok": True, "mode": "project_recovery_write_remote_command_package", "package": package}

    def get_next_remote_action(self) -> Dict[str, Any]:
        actions = self.get_remote_actions()["actions"]
        next_action = next((item for item in actions if item["command_status"] == "pending"), actions[0] if actions else None)
        return {
            "ok": True,
            "mode": "next_project_recovery_write_remote_action",
            "next_remote_action": {
                "recovery_write_remote_action_id": next_action["recovery_write_remote_action_id"],
                "recovery_project_id": next_action["recovery_project_id"],
                "action": "surface_remote_command_in_mobile_cockpit",
                "command_status": next_action["command_status"],
            }
            if next_action
            else None,
        }


project_recovery_write_remote_command_service = ProjectRecoveryWriteRemoteCommandService()
