from typing import Any, Dict, List


class MobileCockpitSyncService:
    def get_mobile_commands(self) -> Dict[str, Any]:
        commands: List[Dict[str, Any]] = [
            {
                "mobile_command_sync_id": "mobile_command_sync_godmode_01",
                "source_node": "mobile_apk",
                "target_node": "local_pc",
                "command_kind": "continue_selected_project",
                "sync_status": "ready",
            },
            {
                "mobile_command_sync_id": "mobile_command_sync_botfarm_01",
                "source_node": "mobile_apk",
                "target_node": "local_pc",
                "command_kind": "continue_botfarm_lane",
                "sync_status": "ready",
            },
            {
                "mobile_command_sync_id": "mobile_command_sync_barbudos_01",
                "source_node": "mobile_apk",
                "target_node": "local_pc",
                "command_kind": "continue_barbudos_project",
                "sync_status": "ready",
            },
        ]
        return {"ok": True, "mode": "mobile_cockpit_commands", "commands": commands}

    def get_mobile_results(self, target_project: str | None = None) -> Dict[str, Any]:
        results: List[Dict[str, Any]] = [
            {
                "mobile_result_sync_id": "mobile_result_sync_godmode_01",
                "target_project": "DevOps God Mode",
                "result_kind": "execution_summary",
                "delivery_mode": "return_to_mobile_cockpit",
                "sync_status": "ready",
            },
            {
                "mobile_result_sync_id": "mobile_result_sync_botfarm_01",
                "target_project": "Bot Farm Headless",
                "result_kind": "lane_progress_update",
                "delivery_mode": "return_to_mobile_cockpit",
                "sync_status": "ready",
            },
            {
                "mobile_result_sync_id": "mobile_result_sync_barbudos_01",
                "target_project": "Barbudos Studio Website",
                "result_kind": "project_follow_up_summary",
                "delivery_mode": "return_to_mobile_cockpit",
                "sync_status": "ready",
            },
        ]
        if target_project:
            results = [item for item in results if item["target_project"] == target_project]
        return {"ok": True, "mode": "mobile_cockpit_results", "results": results}

    def get_sync_package(self) -> Dict[str, Any]:
        package = {
            "commands": self.get_mobile_commands()["commands"],
            "results": self.get_mobile_results()["results"],
            "mobile_compact": True,
            "package_status": "mobile_cockpit_sync_ready",
        }
        return {"ok": True, "mode": "mobile_cockpit_sync_package", "package": package}

    def get_next_sync_action(self) -> Dict[str, Any]:
        first_command = self.get_mobile_commands()["commands"][0] if self.get_mobile_commands()["commands"] else None
        return {
            "ok": True,
            "mode": "next_mobile_cockpit_sync_action",
            "next_sync_action": {
                "mobile_command_sync_id": first_command["mobile_command_sync_id"],
                "action": "receive_mobile_command_and_queue_for_local_execution",
                "sync_status": first_command["sync_status"],
            }
            if first_command
            else None,
        }


mobile_cockpit_sync_service = MobileCockpitSyncService()
