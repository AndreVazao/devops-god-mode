from typing import Any, Dict, List

from app.services.project_recovery_local_apply_service import (
    project_recovery_local_apply_service,
)


class ProjectRecoveryRealWriteLinkService:
    def get_handoffs(self) -> Dict[str, Any]:
        bundles = project_recovery_local_apply_service.get_local_apply_bundles()["bundles"]
        handoffs: List[Dict[str, Any]] = []
        for bundle in bundles:
            handoffs.append(
                {
                    "handoff_id": f"handoff_{bundle['recovery_project_id']}",
                    "recovery_project_id": bundle["recovery_project_id"],
                    "write_ready_bundle_id": bundle["write_ready_bundle_id"],
                    "write_run_candidate_count": bundle["write_target_count"],
                    "handoff_status": "planned",
                }
            )
        return {"ok": True, "mode": "recovery_real_write_handoffs", "handoffs": handoffs}

    def get_handoff_targets(self, recovery_project_id: str | None = None) -> Dict[str, Any]:
        write_ready_package = None
        targets: List[Dict[str, Any]] = []
        bundles = project_recovery_local_apply_service.get_local_apply_bundles()["bundles"]
        candidate_projects = [
            item["recovery_project_id"] for item in bundles if not recovery_project_id or item["recovery_project_id"] == recovery_project_id
        ]
        for project_id in candidate_projects:
            write_ready_package = project_recovery_local_apply_service.get_write_ready_package(project_id)["package"]
            for target in write_ready_package["write_targets"]:
                targets.append(
                    {
                        "handoff_target_id": f"handoff_{target['recovery_write_target_id']}",
                        "recovery_project_id": target["recovery_project_id"],
                        "write_target_path": target["write_target_path"],
                        "preview_payload_mode": target["content_strategy"],
                        "handoff_target_status": "planned",
                    }
                )
        return {"ok": True, "mode": "recovery_real_write_targets", "targets": targets}

    def get_real_write_package(self, recovery_project_id: str) -> Dict[str, Any]:
        write_ready = project_recovery_local_apply_service.get_write_ready_package(recovery_project_id)["package"]
        handoff = next(
            item for item in self.get_handoffs()["handoffs"] if item["recovery_project_id"] == recovery_project_id
        )
        package = {
            "handoff": handoff,
            "targets": self.get_handoff_targets(recovery_project_id)["targets"],
            "real_local_write_mode": "recovery_payload_handoff",
            "package_status": "planned",
        }
        return {"ok": True, "mode": "project_recovery_real_write_package", "package": package}

    def get_next_handoff_action(self) -> Dict[str, Any]:
        handoffs = self.get_handoffs()["handoffs"]
        next_handoff = handoffs[0] if handoffs else None
        return {
            "ok": True,
            "mode": "next_project_recovery_real_write_handoff_action",
            "next_handoff_action": {
                "handoff_id": next_handoff["handoff_id"],
                "recovery_project_id": next_handoff["recovery_project_id"],
                "action": "prepare_real_local_write_candidates",
                "handoff_status": "planned",
            }
            if next_handoff
            else None,
        }


project_recovery_real_write_link_service = ProjectRecoveryRealWriteLinkService()
