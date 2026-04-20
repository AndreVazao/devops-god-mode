from typing import Any, Dict, List

from app.services.project_recovery_write_materialize_service import (
    project_recovery_write_materialize_service,
)


class ProjectRecoveryWriteExecutionService:
    def _statuses_from_risk(self, risk_level: str) -> Dict[str, str | None]:
        if risk_level in {"medium", "high", "critical"}:
            return {
                "patch_status": "waiting_for_approval",
                "preview_status": "blocked_waiting_for_patch",
                "apply_run_status": "blocked_waiting_for_preview",
                "real_write_status": "blocked_waiting_for_apply_run",
                "blocker_reason": "approval_pending",
            }
        return {
            "patch_status": "ready_to_apply",
            "preview_status": "ready_to_create",
            "apply_run_status": "ready_to_create",
            "real_write_status": "ready_to_create",
            "blocker_reason": None,
        }

    def get_execution_sessions(self) -> Dict[str, Any]:
        bridges = project_recovery_write_materialize_service.get_materialize_bridges()["bridges"]
        sessions: List[Dict[str, Any]] = []
        for bridge in bridges:
            targets = project_recovery_write_materialize_service.get_materialize_targets(bridge["recovery_project_id"])["targets"]
            blocker_count = len([item for item in targets if item["risk_level"] in {"medium", "high", "critical"}])
            sessions.append(
                {
                    "recovery_write_execution_id": f"execution_{bridge['recovery_project_id']}",
                    "recovery_project_id": bridge["recovery_project_id"],
                    "recovery_write_materialize_id": bridge["recovery_write_materialize_id"],
                    "execution_target_count": len(targets),
                    "execution_status": "running_with_approval_blockers" if blocker_count else "ready_for_executor_creation",
                    "blocker_count": blocker_count,
                }
            )
        return {"ok": True, "mode": "recovery_write_execution_sessions", "sessions": sessions}

    def get_execution_results(self, recovery_project_id: str | None = None) -> Dict[str, Any]:
        targets = project_recovery_write_materialize_service.get_materialize_targets(recovery_project_id)["targets"]
        results: List[Dict[str, Any]] = []
        for target in targets:
            statuses = self._statuses_from_risk(target["risk_level"])
            results.append(
                {
                    "recovery_write_execution_result_id": f"execution_result_{target['recovery_write_materialize_target_id']}",
                    "recovery_project_id": target["recovery_project_id"],
                    "recovery_write_materialize_target_id": target["recovery_write_materialize_target_id"],
                    "patch_status": statuses["patch_status"],
                    "preview_status": statuses["preview_status"],
                    "apply_run_status": statuses["apply_run_status"],
                    "real_write_status": statuses["real_write_status"],
                    "blocker_reason": statuses["blocker_reason"],
                }
            )
        return {"ok": True, "mode": "recovery_write_execution_results", "results": results}

    def get_execution_package(self, recovery_project_id: str) -> Dict[str, Any]:
        session = next(
            item for item in self.get_execution_sessions()["sessions"] if item["recovery_project_id"] == recovery_project_id
        )
        return {
            "ok": True,
            "mode": "project_recovery_write_execution_package",
            "package": {
                "session": session,
                "results": self.get_execution_results(recovery_project_id)["results"],
                "package_status": session["execution_status"],
            },
        }

    def get_next_execution_action(self) -> Dict[str, Any]:
        sessions = self.get_execution_sessions()["sessions"]
        next_session = sessions[0] if sessions else None
        return {
            "ok": True,
            "mode": "next_project_recovery_write_execution_action",
            "next_execution_action": {
                "recovery_write_execution_id": next_session["recovery_write_execution_id"],
                "recovery_project_id": next_session["recovery_project_id"],
                "action": "resolve_approvals_and_create_executor_requests",
                "execution_status": next_session["execution_status"],
            }
            if next_session
            else None,
        }


project_recovery_write_execution_service = ProjectRecoveryWriteExecutionService()
