from typing import Any, Dict, List


class AssetWorkspaceSyncService:
    def get_asset_syncs(self) -> Dict[str, Any]:
        syncs: List[Dict[str, Any]] = [
            {
                "asset_sync_id": "asset_sync_barbudos_icon_01",
                "target_project": "Barbudos Studio Website",
                "asset_kind": "icon_file",
                "transfer_direction": "mobile_or_workspace_to_local_pc",
                "sync_status": "ready",
            },
            {
                "asset_sync_id": "asset_sync_godmode_reference_01",
                "target_project": "DevOps God Mode",
                "asset_kind": "reference_image_bundle",
                "transfer_direction": "workspace_to_local_pc_for_analysis",
                "sync_status": "ready",
            },
            {
                "asset_sync_id": "asset_sync_build_artifact_01",
                "target_project": "DevOps God Mode",
                "asset_kind": "build_output_package",
                "transfer_direction": "local_pc_to_mobile_or_drive",
                "sync_status": "ready",
            },
        ]
        return {"ok": True, "mode": "asset_syncs", "syncs": syncs}

    def get_workspace_bridges(self) -> Dict[str, Any]:
        bridges: List[Dict[str, Any]] = [
            {
                "workspace_bridge_id": "workspace_bridge_drive_01",
                "workspace_kind": "drive",
                "access_mode": "local_pc_authenticated_bridge",
                "intended_use": "upload_and_download_project_assets",
                "bridge_status": "ready",
            },
            {
                "workspace_bridge_id": "workspace_bridge_dropbox_01",
                "workspace_kind": "dropbox",
                "access_mode": "local_pc_authenticated_bridge",
                "intended_use": "sync_reference_files_and_build_outputs",
                "bridge_status": "ready",
            },
            {
                "workspace_bridge_id": "workspace_bridge_figma_01",
                "workspace_kind": "figma",
                "access_mode": "local_pc_authenticated_bridge",
                "intended_use": "read_assets_palettes_and_design_references",
                "bridge_status": "ready",
            },
        ]
        return {"ok": True, "mode": "workspace_bridges", "bridges": bridges}

    def get_asset_previews(self, target_project: str | None = None) -> Dict[str, Any]:
        previews: List[Dict[str, Any]] = [
            {
                "asset_preview_id": "asset_preview_barbudos_icon_01",
                "target_project": "Barbudos Studio Website",
                "preview_kind": "mobile_visual_approval",
                "approval_mode": "phone_ok_or_revision_request",
                "preview_status": "ready",
            },
            {
                "asset_preview_id": "asset_preview_godmode_palette_01",
                "target_project": "DevOps God Mode",
                "preview_kind": "palette_and_style_preview",
                "approval_mode": "phone_ok_or_revision_request",
                "preview_status": "ready",
            },
            {
                "asset_preview_id": "asset_preview_build_01",
                "target_project": "DevOps God Mode",
                "preview_kind": "build_result_preview",
                "approval_mode": "phone_ok_or_download_request",
                "preview_status": "ready",
            },
        ]
        if target_project:
            previews = [item for item in previews if item["target_project"] == target_project]
        return {"ok": True, "mode": "asset_previews", "previews": previews}

    def get_sync_package(self) -> Dict[str, Any]:
        package = {
            "syncs": self.get_asset_syncs()["syncs"],
            "bridges": self.get_workspace_bridges()["bridges"],
            "previews": self.get_asset_previews()["previews"],
            "mobile_compact": True,
            "package_status": "asset_workspace_sync_ready",
        }
        return {"ok": True, "mode": "asset_workspace_sync_package", "package": package}

    def get_next_sync_action(self) -> Dict[str, Any]:
        first_sync = self.get_asset_syncs()["syncs"][0] if self.get_asset_syncs()["syncs"] else None
        return {
            "ok": True,
            "mode": "next_asset_workspace_sync_action",
            "next_sync_action": {
                "asset_sync_id": first_sync["asset_sync_id"],
                "target_project": first_sync["target_project"],
                "action": "receive_or_fetch_asset_then_prepare_mobile_preview",
                "sync_status": first_sync["sync_status"],
            }
            if first_sync
            else None,
        }


asset_workspace_sync_service = AssetWorkspaceSyncService()
