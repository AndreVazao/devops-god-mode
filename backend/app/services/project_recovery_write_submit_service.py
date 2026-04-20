from typing import Any, Dict, List

from app.services.project_recovery_write_queue_service import (
    project_recovery_write_queue_service,
)


class ProjectRecoveryWriteSubmitService:
    def get_submissions(self) -> Dict[str, Any]:
        entries = project_recovery_write_queue_service.get_queue_entries()["entries"]
        submissions: List[Dict[str, Any]] = []
        for entry in entries:
            submissions.append(
                {
                    "recovery_write_submit_id": f"submit_{entry['recovery_write_queue_id']}",
                    "recovery_project_id": entry["recovery_project_id"],
                    "recovery_write_queue_id": entry["recovery_write_queue_id"],
                    "submit_target_count": entry["queue_target_count"],
                    "submit_status": "planned",
                }
            )
        return {"ok": True, "mode": "recovery_write_submissions", "submissions": submissions}

    def get_submit_targets(self, recovery_project_id: str | None = None) -> Dict[str, Any]:
        queue_targets = project_recovery_write_queue_service.get_queue_targets(recovery_project_id)["targets"]
        submit_targets: List[Dict[str, Any]] = []
        for target in queue_targets:
            submit_targets.append(
                {
                    "recovery_write_submit_target_id": f"submit_{target['recovery_write_queue_target_id']}",
                    "recovery_project_id": target["recovery_project_id"],
                    "recovery_write_queue_target_id": target["recovery_write_queue_target_id"],
                    "submit_target_path": target["queue_target_path"],
                    "submit_mode": "real_local_write_submission",
                    "submit_target_status": "planned",
                }
            )
        return {"ok": True, "mode": "recovery_write_submit_targets", "targets": submit_targets}

    def get_submit_package(self, recovery_project_id: str) -> Dict[str, Any]:
        submission = next(
            item for item in self.get_submissions()["submissions"] if item["recovery_project_id"] == recovery_project_id
        )
        package = {
            "submission": submission,
            "targets": self.get_submit_targets(recovery_project_id)["targets"],
            "submit_mode": "ready_for_real_local_write_submission",
            "package_status": "planned",
        }
        return {"ok": True, "mode": "project_recovery_write_submit_package", "package": package}

    def get_next_submit_action(self) -> Dict[str, Any]:
        submissions = self.get_submissions()["submissions"]
        next_submission = submissions[0] if submissions else None
        return {
            "ok": True,
            "mode": "next_project_recovery_write_submit_action",
            "next_submit_action": {
                "recovery_write_submit_id": next_submission["recovery_write_submit_id"],
                "recovery_project_id": next_submission["recovery_project_id"],
                "action": "prepare_real_local_write_creation_payload",
                "submit_status": "planned",
            }
            if next_submission
            else None,
        }


project_recovery_write_submit_service = ProjectRecoveryWriteSubmitService()
