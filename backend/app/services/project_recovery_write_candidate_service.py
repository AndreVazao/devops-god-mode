from typing import Any, Dict, List

from app.services.project_recovery_real_write_link_service import (
    project_recovery_real_write_link_service,
)


class ProjectRecoveryWriteCandidateService:
    def get_candidates(self) -> Dict[str, Any]:
        handoffs = project_recovery_real_write_link_service.get_handoffs()["handoffs"]
        candidates: List[Dict[str, Any]] = []
        for handoff in handoffs:
            candidates.append(
                {
                    "write_candidate_id": f"write_candidate_{handoff['recovery_project_id']}",
                    "recovery_project_id": handoff["recovery_project_id"],
                    "handoff_id": handoff["handoff_id"],
                    "candidate_target_count": handoff["write_run_candidate_count"],
                    "candidate_status": "planned",
                }
            )
        return {"ok": True, "mode": "recovery_write_candidates", "candidates": candidates}

    def get_candidate_targets(self, recovery_project_id: str | None = None) -> Dict[str, Any]:
        targets = project_recovery_real_write_link_service.get_handoff_targets(recovery_project_id)["targets"]
        candidate_targets: List[Dict[str, Any]] = []
        for target in targets:
            candidate_targets.append(
                {
                    "write_candidate_target_id": f"candidate_{target['handoff_target_id']}",
                    "recovery_project_id": target["recovery_project_id"],
                    "handoff_target_id": target["handoff_target_id"],
                    "target_path": target["write_target_path"],
                    "candidate_mode": "real_local_write_candidate",
                    "candidate_target_status": "planned",
                }
            )
        return {"ok": True, "mode": "recovery_write_candidate_targets", "targets": candidate_targets}

    def get_candidate_package(self, recovery_project_id: str) -> Dict[str, Any]:
        candidate = next(
            item for item in self.get_candidates()["candidates"] if item["recovery_project_id"] == recovery_project_id
        )
        package = {
            "candidate": candidate,
            "targets": self.get_candidate_targets(recovery_project_id)["targets"],
            "candidate_mode": "ready_for_real_local_write_candidate_generation",
            "package_status": "planned",
        }
        return {"ok": True, "mode": "project_recovery_write_candidate_package", "package": package}

    def get_next_candidate_action(self) -> Dict[str, Any]:
        candidates = self.get_candidates()["candidates"]
        next_candidate = candidates[0] if candidates else None
        return {
            "ok": True,
            "mode": "next_project_recovery_write_candidate_action",
            "next_candidate_action": {
                "write_candidate_id": next_candidate["write_candidate_id"],
                "recovery_project_id": next_candidate["recovery_project_id"],
                "action": "prepare_real_local_write_run_candidates",
                "candidate_status": "planned",
            }
            if next_candidate
            else None,
        }


project_recovery_write_candidate_service = ProjectRecoveryWriteCandidateService()
