from typing import Any, Dict, List

from app.services.project_recovery_write_run_service import (
    project_recovery_write_run_service,
)


class ProjectRecoveryWriteQueueService:
    def get_queue_entries(self) -> Dict[str, Any]:
        runs = project_recovery_write_run_service.get_runs()["runs"]
        entries: List[Dict[str, Any]] = []
        for run in runs:
            entries.append(
                {
                    "recovery_write_queue_id": f"queue_{run['recovery_write_run_id']}",
                    "recovery_project_id": run["recovery_project_id"],
                    "recovery_write_run_id": run["recovery_write_run_id"],
                    "queue_target_count": run["run_target_count"],
                    "queue_status": "planned",
                }
            )
        return {"ok": True, "mode": "recovery_write_queue_entries", "entries": entries}

    def get_queue_targets(self, recovery_project_id: str | None = None) -> Dict[str, Any]:
        run_targets = project_recovery_write_run_service.get_run_targets(recovery_project_id)["targets"]
        queue_targets: List[Dict[str, Any]] = []
        for target in run_targets:
            queue_targets.append(
                {
                    "recovery_write_queue_target_id": f"queue_{target['recovery_write_run_target_id']}",
                    "recovery_project_id": target["recovery_project_id"],
                    "recovery_write_run_target_id": target["recovery_write_run_target_id"],
                    "queue_target_path": target["run_target_path"],
                    "queue_mode": "real_local_write_queue_entry",
                    "queue_target_status": "planned",
                }
            )
        return {"ok": True, "mode": "recovery_write_queue_targets", "targets": queue_targets}

    def get_queue_package(self, recovery_project_id: str) -> Dict[str, Any]:
        entry = next(
            item for item in self.get_queue_entries()["entries"] if item["recovery_project_id"] == recovery_project_id
        )
        package = {
            "entry": entry,
            "targets": self.get_queue_targets(recovery_project_id)["targets"],
            "queue_mode": "ready_for_real_local_write_submission",
            "package_status": "planned",
        }
        return {"ok": True, "mode": "project_recovery_write_queue_package", "package": package}

    def get_next_queue_action(self) -> Dict[str, Any]:
        entries = self.get_queue_entries()["entries"]
        next_entry = entries[0] if entries else None
        return {
            "ok": True,
            "mode": "next_project_recovery_write_queue_action",
            "next_queue_action": {
                "recovery_write_queue_id": next_entry["recovery_write_queue_id"],
                "recovery_project_id": next_entry["recovery_project_id"],
                "action": "prepare_real_local_write_submission",
                "queue_status": "planned",
            }
            if next_entry
            else None,
        }


project_recovery_write_queue_service = ProjectRecoveryWriteQueueService()
