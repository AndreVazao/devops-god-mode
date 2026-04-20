from typing import Any, Dict, List

from app.services.project_recovery_write_submit_service import (
    project_recovery_write_submit_service,
)


class ProjectRecoveryWriteCreateService:
    def get_create_requests(self) -> Dict[str, Any]:
        submissions = project_recovery_write_submit_service.get_submissions()["submissions"]
        requests: List[Dict[str, Any]] = []
        for submission in submissions:
            requests.append(
                {
                    "recovery_write_create_id": f"create_{submission['recovery_write_submit_id']}",
                    "recovery_project_id": submission["recovery_project_id"],
                    "recovery_write_submit_id": submission["recovery_write_submit_id"],
                    "create_target_count": submission["submit_target_count"],
                    "create_status": "planned",
                }
            )
        return {"ok": True, "mode": "recovery_write_create_requests", "requests": requests}

    def get_create_targets(self, recovery_project_id: str | None = None) -> Dict[str, Any]:
        submit_targets = project_recovery_write_submit_service.get_submit_targets(recovery_project_id)["targets"]
        create_targets: List[Dict[str, Any]] = []
        for target in submit_targets:
            create_targets.append(
                {
                    "recovery_write_create_target_id": f"create_{target['recovery_write_submit_target_id']}",
                    "recovery_project_id": target["recovery_project_id"],
                    "recovery_write_submit_target_id": target["recovery_write_submit_target_id"],
                    "create_target_path": target["submit_target_path"],
                    "create_mode": "real_local_write_create_payload",
                    "create_target_status": "planned",
                }
            )
        return {"ok": True, "mode": "recovery_write_create_targets", "targets": create_targets}

    def get_create_package(self, recovery_project_id: str) -> Dict[str, Any]:
        request = next(
            item for item in self.get_create_requests()["requests"] if item["recovery_project_id"] == recovery_project_id
        )
        package = {
            "request": request,
            "targets": self.get_create_targets(recovery_project_id)["targets"],
            "create_mode": "ready_for_real_local_write_create",
            "package_status": "planned",
        }
        return {"ok": True, "mode": "project_recovery_write_create_package", "package": package}

    def get_next_create_action(self) -> Dict[str, Any]:
        requests = self.get_create_requests()["requests"]
        next_request = requests[0] if requests else None
        return {
            "ok": True,
            "mode": "next_project_recovery_write_create_action",
            "next_create_action": {
                "recovery_write_create_id": next_request["recovery_write_create_id"],
                "recovery_project_id": next_request["recovery_project_id"],
                "action": "prepare_real_local_write_create_request",
                "create_status": "planned",
            }
            if next_request
            else None,
        }


project_recovery_write_create_service = ProjectRecoveryWriteCreateService()
