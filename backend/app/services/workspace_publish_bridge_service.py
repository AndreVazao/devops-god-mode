from __future__ import annotations

import base64
from pathlib import Path
from typing import Any, Dict

from app.services.external_asset_intake_service import external_asset_intake_service
from app.services.external_asset_publish_execution_service import (
    external_asset_publish_execution_service,
)
from app.services.local_asset_workspace_service import local_asset_workspace_service


class WorkspacePublishBridgeService:
    def get_status(self) -> Dict[str, Any]:
        workspace = local_asset_workspace_service.get_status()
        intake = external_asset_intake_service.get_status()
        publish = external_asset_publish_execution_service.get_status()
        return {
            "ok": True,
            "mode": "workspace_publish_bridge_status",
            "workspace_root": workspace["workspace_root"],
            "staged_count": intake["staged_count"],
            "inline_ready_count": intake["inline_ready_count"],
            "publish_status": publish["status"],
            "status": "workspace_publish_bridge_ready",
        }

    def restage_workspace_file(
        self,
        workspace_file: str,
        asset_role: str,
        source_ref: str,
        project_hint: str | None = None,
        repository_full_name: str | None = None,
        destination_path: str | None = None,
        content_kind: str | None = None,
    ) -> Dict[str, Any]:
        path = Path(workspace_file)
        if not path.exists():
            return {
                "ok": False,
                "mode": "workspace_publish_bridge_restage_result",
                "restage_status": "workspace_file_not_found",
                "workspace_file": workspace_file,
            }

        suffix = path.suffix.lower()
        text_suffixes = {".txt", ".md", ".json", ".svg", ".html", ".css", ".js", ".ts", ".xml"}
        if suffix in text_suffixes:
            staged = external_asset_intake_service.stage_asset_request(
                source_type="local_workspace_file",
                source_ref=source_ref,
                asset_role=asset_role,
                project_hint=project_hint,
                repository_full_name=repository_full_name,
                destination_path=destination_path,
                content_text=path.read_text(encoding="utf-8"),
                content_kind=content_kind or "workspace_text",
            )
            payload_mode = "text"
        else:
            staged = external_asset_intake_service.stage_asset_request(
                source_type="local_workspace_file",
                source_ref=source_ref,
                asset_role=asset_role,
                project_hint=project_hint,
                repository_full_name=repository_full_name,
                destination_path=destination_path,
                content_base64=base64.b64encode(path.read_bytes()).decode("utf-8"),
                content_kind=content_kind or "workspace_binary",
            )
            payload_mode = "binary"

        return {
            "ok": True,
            "mode": "workspace_publish_bridge_restage_result",
            "restage_status": "restaged_from_workspace",
            "payload_mode": payload_mode,
            "workspace_file": workspace_file,
            "staged_asset": staged["staged_asset"],
        }

    async def publish_workspace_file(
        self,
        workspace_file: str,
        asset_role: str,
        source_ref: str,
        repository_full_name: str,
        destination_path: str,
        project_hint: str | None = None,
        branch: str | None = None,
        content_kind: str | None = None,
        dry_run: bool = True,
    ) -> Dict[str, Any]:
        restaged = self.restage_workspace_file(
            workspace_file=workspace_file,
            asset_role=asset_role,
            source_ref=source_ref,
            project_hint=project_hint,
            repository_full_name=repository_full_name,
            destination_path=destination_path,
            content_kind=content_kind,
        )
        if not restaged.get("ok"):
            return {
                "ok": False,
                "mode": "workspace_publish_bridge_publish_result",
                "publish_status": "restage_failed",
                "restage": restaged,
            }

        publish_result = await external_asset_publish_execution_service.execute_publish_plan(
            repository_full_name=repository_full_name,
            project_hint=project_hint,
            branch=branch,
            dry_run=dry_run,
        )
        return {
            "ok": True,
            "mode": "workspace_publish_bridge_publish_result",
            "publish_status": "dry_run_ready" if dry_run else "publish_attempted",
            "restage": restaged,
            "publish_result": publish_result,
            "dry_run": dry_run,
        }

    async def dry_run_publish_workspace_file(
        self,
        workspace_file: str,
        asset_role: str,
        source_ref: str,
        repository_full_name: str,
        destination_path: str,
        project_hint: str | None = None,
        branch: str | None = None,
        content_kind: str | None = None,
    ) -> Dict[str, Any]:
        return await self.publish_workspace_file(
            workspace_file=workspace_file,
            asset_role=asset_role,
            source_ref=source_ref,
            repository_full_name=repository_full_name,
            destination_path=destination_path,
            project_hint=project_hint,
            branch=branch,
            content_kind=content_kind,
            dry_run=True,
        )

    def get_package(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "mode": "workspace_publish_bridge_package",
            "package": {
                "status": self.get_status(),
                "workspace": local_asset_workspace_service.get_package(),
                "intake": external_asset_intake_service.get_package(),
                "publish": external_asset_publish_execution_service.get_package(),
                "package_status": "workspace_publish_bridge_ready",
            },
        }


workspace_publish_bridge_service = WorkspacePublishBridgeService()
