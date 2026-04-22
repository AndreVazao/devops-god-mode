from typing import Any, Dict, List


class ApprovedAssetReapplyService:
    def get_reapply_sessions(self) -> Dict[str, Any]:
        sessions: List[Dict[str, Any]] = [
            {
                "approved_asset_reapply_id": "approved_asset_reapply_barbudos_01",
                "target_project": "Barbudos Studio Website",
                "asset_preview_id": "asset_preview_barbudos_icon_01",
                "reapply_mode": "apply_mobile_approved_asset_to_local_project",
                "reapply_status": "ready",
            },
            {
                "approved_asset_reapply_id": "approved_asset_reapply_godmode_01",
                "target_project": "DevOps God Mode",
                "asset_preview_id": "asset_preview_godmode_palette_01",
                "reapply_mode": "apply_mobile_approved_palette_to_local_theme_assets",
                "reapply_status": "ready",
            },
            {
                "approved_asset_reapply_id": "approved_asset_reapply_build_01",
                "target_project": "DevOps God Mode",
                "asset_preview_id": "asset_preview_build_01",
                "reapply_mode": "apply_mobile_approved_preview_adjustments_to_local_build_labels",
                "reapply_status": "ready",
            },
        ]
        return {"ok": True, "mode": "approved_asset_reapply_sessions", "sessions": sessions}

    def get_reapply_actions(self, target_project: str | None = None) -> Dict[str, Any]:
        actions: List[Dict[str, Any]] = [
            {
                "visual_reapply_action_id": "visual_reapply_action_barbudos_01",
                "target_project": "Barbudos Studio Website",
                "decision_kind": "revise_preview",
                "apply_target": "branding_icon_pipeline",
                "action_status": "ready",
            },
            {
                "visual_reapply_action_id": "visual_reapply_action_godmode_01",
                "target_project": "DevOps God Mode",
                "decision_kind": "approve_preview",
                "apply_target": "theme_palette_pipeline",
                "action_status": "ready",
            },
            {
                "visual_reapply_action_id": "visual_reapply_action_build_01",
                "target_project": "DevOps God Mode",
                "decision_kind": "request_small_adjustment",
                "apply_target": "build_preview_label_pipeline",
                "action_status": "ready",
            },
        ]
        if target_project:
            actions = [item for item in actions if item["target_project"] == target_project]
        return {"ok": True, "mode": "visual_reapply_actions", "actions": actions}

    def get_reapply_package(self) -> Dict[str, Any]:
        package = {
            "sessions": self.get_reapply_sessions()["sessions"],
            "actions": self.get_reapply_actions()["actions"],
            "mobile_compact": True,
            "package_status": "approved_asset_reapply_ready",
        }
        return {"ok": True, "mode": "approved_asset_reapply_package", "package": package}

    def get_next_reapply_action(self) -> Dict[str, Any]:
        first_session = self.get_reapply_sessions()["sessions"][0] if self.get_reapply_sessions()["sessions"] else None
        return {
            "ok": True,
            "mode": "next_approved_asset_reapply_action",
            "next_reapply_action": {
                "approved_asset_reapply_id": first_session["approved_asset_reapply_id"],
                "target_project": first_session["target_project"],
                "action": "apply_visual_decision_to_local_asset_pipeline",
                "reapply_status": first_session["reapply_status"],
            }
            if first_session
            else None,
        }


approved_asset_reapply_service = ApprovedAssetReapplyService()
