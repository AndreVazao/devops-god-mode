from typing import Any, Dict, List

from app.services.project_recovery_write_mobile_action_execution_service import (
    project_recovery_write_mobile_action_execution_service,
)


class BuildArtifactHarvestService:
    def _preferred_output_type(self, recovery_project_id: str) -> str:
        return "apk" if recovery_project_id == "recovery_devops_god_mode_01" else "exe"

    def get_harvests(self) -> Dict[str, Any]:
        executions = project_recovery_write_mobile_action_execution_service.get_mobile_executions()["executions"]
        harvests: List[Dict[str, Any]] = []
        for execution in executions:
            preferred_output_type = self._preferred_output_type(execution["recovery_project_id"])
            artifact_candidate_count = 2 if preferred_output_type == "apk" else 1
            harvests.append(
                {
                    "build_artifact_harvest_id": f"artifact_harvest_{execution['recovery_project_id']}",
                    "recovery_project_id": execution["recovery_project_id"],
                    "artifact_candidate_count": artifact_candidate_count,
                    "preferred_output_type": preferred_output_type,
                    "harvest_status": "ready_to_collect",
                }
            )
        return {"ok": True, "mode": "build_artifact_harvests", "harvests": harvests}

    def get_artifact_items(self, recovery_project_id: str | None = None) -> Dict[str, Any]:
        harvests = self.get_harvests()["harvests"]
        items: List[Dict[str, Any]] = []
        for harvest in harvests:
            if recovery_project_id and harvest["recovery_project_id"] != recovery_project_id:
                continue
            if harvest["preferred_output_type"] == "apk":
                items.extend(
                    [
                        {
                            "build_artifact_item_id": f"artifact_item_{harvest['recovery_project_id']}_apk",
                            "recovery_project_id": harvest["recovery_project_id"],
                            "source_workflow": "android-real-build-progressive",
                            "artifact_name": "GodModeMobile.apk",
                            "normalized_output_name": "DevOps God Mode Mobile.apk",
                            "artifact_status": "ready_for_download",
                        },
                        {
                            "build_artifact_item_id": f"artifact_item_{harvest['recovery_project_id']}_exe",
                            "recovery_project_id": harvest["recovery_project_id"],
                            "source_workflow": "windows-exe-real-build",
                            "artifact_name": "GodModeDesktop.exe",
                            "normalized_output_name": "DevOps God Mode Desktop.exe",
                            "artifact_status": "ready_for_download",
                        },
                    ]
                )
            else:
                items.append(
                    {
                        "build_artifact_item_id": f"artifact_item_{harvest['recovery_project_id']}_exe",
                        "recovery_project_id": harvest["recovery_project_id"],
                        "source_workflow": "windows-exe-real-build",
                        "artifact_name": "GodModeDesktop.exe",
                        "normalized_output_name": "DevOps God Mode Desktop.exe",
                        "artifact_status": "ready_for_download",
                    }
                )
        return {"ok": True, "mode": "build_artifact_items", "items": items}

    def get_harvest_package(self, recovery_project_id: str) -> Dict[str, Any]:
        harvest = next(
            item for item in self.get_harvests()["harvests"] if item["recovery_project_id"] == recovery_project_id
        )
        package = {
            "harvest": harvest,
            "items": self.get_artifact_items(recovery_project_id)["items"],
            "download_ready": True,
            "rename_ready": True,
            "package_status": harvest["harvest_status"],
        }
        return {"ok": True, "mode": "build_artifact_harvest_package", "package": package}

    def get_next_harvest_action(self) -> Dict[str, Any]:
        harvests = self.get_harvests()["harvests"]
        next_harvest = harvests[0] if harvests else None
        return {
            "ok": True,
            "mode": "next_build_artifact_harvest_action",
            "next_harvest_action": {
                "build_artifact_harvest_id": next_harvest["build_artifact_harvest_id"],
                "recovery_project_id": next_harvest["recovery_project_id"],
                "action": "download_artifact_from_actions_and_normalize_final_filename",
                "harvest_status": next_harvest["harvest_status"],
            }
            if next_harvest
            else None,
        }


build_artifact_harvest_service = BuildArtifactHarvestService()
