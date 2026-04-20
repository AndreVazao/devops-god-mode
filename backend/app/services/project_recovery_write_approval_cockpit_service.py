from typing import Any, Dict, List

from app.services.project_recovery_write_execution_service import (
    project_recovery_write_execution_service,
)


class ProjectRecoveryWriteApprovalCockpitService:
    def get_cockpits(self) -> Dict[str, Any]:
        sessions = project_recovery_write_execution_service.get_execution_sessions()["sessions"]
        cockpits: List[Dict[str, Any]] = []
        for session in sessions:
            results = project_recovery_write_execution_service.get_execution_results(session["recovery_project_id"])["results"]
            pending = [item for item in results if item.get("blocker_reason") == "approval_pending"]
            ready = [item for item in results if item.get("blocker_reason") is None]
            cockpits.append(
                {
                    "recovery_write_approval_cockpit_id": f"approval_cockpit_{session['recovery_project_id']}",
                    "recovery_project_id": session["recovery_project_id"],
                    "pending_approval_count": len(pending),
                    "ready_target_count": len(ready),
                    "cockpit_status": "approval_attention_required" if pending else "ready_for_mobile_confirm",
                }
            )
        return {"ok": True, "mode": "recovery_write_approval_cockpits", "cockpits": cockpits}

    def get_approval_items(self, recovery_project_id: str | None = None) -> Dict[str, Any]:
        results = project_recovery_write_execution_service.get_execution_results(recovery_project_id)["results"]
        items: List[Dict[str, Any]] = []
        for result in results:
            target_label = result["recovery_write_execution_result_id"].replace("execution_result_", "")
            items.append(
                {
                    "recovery_write_approval_item_id": f"approval_{result['recovery_write_execution_result_id']}",
                    "recovery_project_id": result["recovery_project_id"],
                    "recovery_write_execution_result_id": result["recovery_write_execution_result_id"],
                    "required_response": "OK" if result.get("blocker_reason") == "approval_pending" else "NONE",
                    "approval_status": "pending" if result.get("blocker_reason") == "approval_pending" else "not_required",
                    "mobile_action_label": f"Aprovar {target_label}" if result.get("blocker_reason") == "approval_pending" else f"Sem aprovação para {target_label}",
                }
            )
        return {"ok": True, "mode": "recovery_write_approval_items", "items": items}

    def get_cockpit_package(self, recovery_project_id: str) -> Dict[str, Any]:
        cockpit = next(
            item for item in self.get_cockpits()["cockpits"] if item["recovery_project_id"] == recovery_project_id
        )
        items = self.get_approval_items(recovery_project_id)["items"]
        package = {
            "cockpit": cockpit,
            "items": items,
            "mobile_ready": True,
            "package_status": cockpit["cockpit_status"],
        }
        return {"ok": True, "mode": "project_recovery_write_approval_cockpit_package", "package": package}

    def get_next_approval_action(self) -> Dict[str, Any]:
        items = self.get_approval_items()["items"]
        next_item = next((item for item in items if item["approval_status"] == "pending"), items[0] if items else None)
        return {
            "ok": True,
            "mode": "next_project_recovery_write_approval_action",
            "next_approval_action": {
                "recovery_write_approval_item_id": next_item["recovery_write_approval_item_id"],
                "recovery_project_id": next_item["recovery_project_id"],
                "action": "surface_mobile_approval_and_confirm_next_executor_step",
                "approval_status": next_item["approval_status"],
            }
            if next_item
            else None,
        }


project_recovery_write_approval_cockpit_service = ProjectRecoveryWriteApprovalCockpitService()
