from typing import Any, Dict, List

from app.services.project_recovery_write_candidate_service import (
    project_recovery_write_candidate_service,
)


class ProjectRecoveryWriteRunService:
    def get_runs(self) -> Dict[str, Any]:
        candidates = project_recovery_write_candidate_service.get_candidates()["candidates"]
        runs: List[Dict[str, Any]] = []
        for candidate in candidates:
            runs.append(
                {
                    "recovery_write_run_id": f"run_{candidate['write_candidate_id']}",
                    "recovery_project_id": candidate["recovery_project_id"],
                    "write_candidate_id": candidate["write_candidate_id"],
                    "run_target_count": candidate["candidate_target_count"],
                    "run_status": "planned",
                }
            )
        return {"ok": True, "mode": "recovery_write_runs", "runs": runs}

    def get_run_targets(self, recovery_project_id: str | None = None) -> Dict[str, Any]:
        candidate_targets = project_recovery_write_candidate_service.get_candidate_targets(recovery_project_id)["targets"]
        run_targets: List[Dict[str, Any]] = []
        for target in candidate_targets:
            run_targets.append(
                {
                    "recovery_write_run_target_id": f"run_{target['write_candidate_target_id']}",
                    "recovery_project_id": target["recovery_project_id"],
                    "write_candidate_target_id": target["write_candidate_target_id"],
                    "run_target_path": target["target_path"],
                    "run_mode": "real_local_write_prepared_run",
                    "run_target_status": "planned",
                }
            )
        return {"ok": True, "mode": "recovery_write_run_targets", "targets": run_targets}

    def get_run_package(self, recovery_project_id: str) -> Dict[str, Any]:
        run = next(
            item for item in self.get_runs()["runs"] if item["recovery_project_id"] == recovery_project_id
        )
        package = {
            "run": run,
            "targets": self.get_run_targets(recovery_project_id)["targets"],
            "run_mode": "ready_for_real_local_write_queue",
            "package_status": "planned",
        }
        return {"ok": True, "mode": "project_recovery_write_run_package", "package": package}

    def get_next_run_action(self) -> Dict[str, Any]:
        runs = self.get_runs()["runs"]
        next_run = runs[0] if runs else None
        return {
            "ok": True,
            "mode": "next_project_recovery_write_run_action",
            "next_run_action": {
                "recovery_write_run_id": next_run["recovery_write_run_id"],
                "recovery_project_id": next_run["recovery_project_id"],
                "action": "prepare_real_local_write_queue_entry",
                "run_status": "planned",
            }
            if next_run
            else None,
        }


project_recovery_write_run_service = ProjectRecoveryWriteRunService()
