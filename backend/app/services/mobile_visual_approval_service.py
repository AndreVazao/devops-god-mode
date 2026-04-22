from typing import Any, Dict, List


class MobileVisualApprovalService:
    def get_visual_sessions(self) -> Dict[str, Any]:
        sessions: List[Dict[str, Any]] = [
            {
                "visual_approval_session_id": "visual_approval_session_barbudos_01",
                "target_project": "Barbudos Studio Website",
                "asset_preview_id": "asset_preview_barbudos_icon_01",
                "preview_source": "local_pc_generated_preview",
                "approval_status": "ready",
            },
            {
                "visual_approval_session_id": "visual_approval_session_godmode_01",
                "target_project": "DevOps God Mode",
                "asset_preview_id": "asset_preview_godmode_palette_01",
                "preview_source": "workspace_reference_and_local_preview",
                "approval_status": "ready",
            },
            {
                "visual_approval_session_id": "visual_approval_session_build_01",
                "target_project": "DevOps God Mode",
                "asset_preview_id": "asset_preview_build_01",
                "preview_source": "local_pc_build_preview",
                "approval_status": "ready",
            },
        ]
        return {"ok": True, "mode": "mobile_visual_approval_sessions", "sessions": sessions}

    def get_revision_decisions(self, target_project: str | None = None) -> Dict[str, Any]:
        decisions: List[Dict[str, Any]] = [
            {
                "visual_revision_decision_id": "visual_revision_decision_barbudos_01",
                "target_project": "Barbudos Studio Website",
                "decision_kind": "revise_preview",
                "revision_goal": "improve_icon_readability_and_balance",
                "decision_status": "ready",
            },
            {
                "visual_revision_decision_id": "visual_revision_decision_godmode_01",
                "target_project": "DevOps God Mode",
                "decision_kind": "approve_preview",
                "revision_goal": "keep_current_palette_and_spacing",
                "decision_status": "ready",
            },
            {
                "visual_revision_decision_id": "visual_revision_decision_build_01",
                "target_project": "DevOps God Mode",
                "decision_kind": "request_small_adjustment",
                "revision_goal": "improve_preview_compression_and_labeling",
                "decision_status": "ready",
            },
        ]
        if target_project:
            decisions = [item for item in decisions if item["target_project"] == target_project]
        return {"ok": True, "mode": "visual_revision_decisions", "decisions": decisions}

    def get_visual_package(self) -> Dict[str, Any]:
        package = {
            "sessions": self.get_visual_sessions()["sessions"],
            "decisions": self.get_revision_decisions()["decisions"],
            "mobile_compact": True,
            "package_status": "mobile_visual_approval_ready",
        }
        return {"ok": True, "mode": "mobile_visual_approval_package", "package": package}

    def get_next_visual_action(self) -> Dict[str, Any]:
        first_session = self.get_visual_sessions()["sessions"][0] if self.get_visual_sessions()["sessions"] else None
        return {
            "ok": True,
            "mode": "next_mobile_visual_approval_action",
            "next_visual_action": {
                "visual_approval_session_id": first_session["visual_approval_session_id"],
                "target_project": first_session["target_project"],
                "action": "show_preview_and_wait_for_mobile_approval_or_revision",
                "approval_status": first_session["approval_status"],
            }
            if first_session
            else None,
        }


mobile_visual_approval_service = MobileVisualApprovalService()
