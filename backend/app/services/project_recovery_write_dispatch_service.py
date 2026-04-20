from typing import Any, Dict, List

from app.services.project_recovery_write_create_service import (
    project_recovery_write_create_service,
)


class ProjectRecoveryWriteDispatchService:
    def get_dispatches(self) -> Dict[str, Any]:
        requests = project_recovery_write_create_service.get_create_requests()["requests"]
        dispatches: List[Dict[str, Any]] = []
        for request in requests:
            dispatches.append(
                {
                    "recovery_write_dispatch_id": f"dispatch_{request['recovery_write_create_id']}",
                    "recovery_project_id": request["recovery_project_id"],
                    "recovery_write_create_id": request["recovery_write_create_id"],
                    "dispatch_target_count": request["create_target_count"],
                    "dispatch_status": "planned",
                }
            )
        return {"ok": True, "mode": "recovery_write_dispatches", "dispatches": dispatches}

    def get_dispatch_targets(self, recovery_project_id: str | None = None) -> Dict[str, Any]:
        create_targets = project_recovery_write_create_service.get_create_targets(recovery_project_id)["targets"]
        dispatch_targets: List[Dict[str, Any]] = []
        for target in create_targets:
            dispatch_targets.append(
                {
                    "recovery_write_dispatch_target_id": f"dispatch_{target['recovery_write_create_target_id']}",
                    "recovery_project_id": target["recovery_project_id"],
                    "recovery_write_create_target_id": target["recovery_write_create_target_id"],
                    "dispatch_target_path": target["create_target_path"],
                    "dispatch_mode": "real_local_write_dispatch_payload",
                    "dispatch_target_status": "planned",
                }
            )
        return {"ok": True, "mode": "recovery_write_dispatch_targets", "targets": dispatch_targets}

    def get_dispatch_package(self, recovery_project_id: str) -> Dict[str, Any]:
        dispatch = next(
            item for item in self.get_dispatches()["dispatches"] if item["recovery_project_id"] == recovery_project_id
        )
        package = {
            "dispatch": dispatch,
            "targets": self.get_dispatch_targets(recovery_project_id)["targets"],
            "dispatch_mode": "ready_for_real_local_write_dispatch",
            "package_status": "planned",
        }
        return {"ok": True, "mode": "project_recovery_write_dispatch_package", "package": package}

    def get_next_dispatch_action(self) -> Dict[str, Any]:
        dispatches = self.get_dispatches()["dispatches"]
        next_dispatch = dispatches[0] if dispatches else None
        return {
            "ok": True,
            "mode": "next_project_recovery_write_dispatch_action",
            "next_dispatch_action": {
                "recovery_write_dispatch_id": next_dispatch["recovery_write_dispatch_id"],
                "recovery_project_id": next_dispatch["recovery_project_id"],
                "action": "prepare_real_local_write_dispatch_request",
                "dispatch_status": "planned",
            }
            if next_dispatch
            else None,
        }


project_recovery_write_dispatch_service = ProjectRecoveryWriteDispatchService()
