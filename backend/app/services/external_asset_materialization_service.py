from __future__ import annotations

import base64
from typing import Any, Dict

from app.services.external_asset_intake_service import external_asset_intake_service
from app.services.github_service import github_service


class ExternalAssetMaterializationService:
    def get_status(self) -> Dict[str, Any]:
        intake_package = external_asset_intake_service.get_package()["package"]
        return {
            "ok": True,
            "mode": "external_asset_materialization_status",
            "github_configured": github_service.is_configured(),
            "staged_count": intake_package["staged_count"],
            "inline_ready_count": intake_package["inline_ready_count"],
            "status": "external_asset_materialization_ready",
        }

    async def materialize_github_file_to_stage(
        self,
        repository_full_name: str,
        file_path: str,
        asset_role: str,
        project_hint: str | None = None,
        destination_path: str | None = None,
        ref: str | None = None,
    ) -> Dict[str, Any]:
        file_result = await github_service.get_repository_file(
            repository_full_name=repository_full_name,
            path=file_path,
            ref=ref,
        )
        if not file_result.get("ok"):
            return {
                "ok": False,
                "mode": "external_asset_materialization_result",
                "materialization_status": "source_file_not_found",
                "source": file_result,
            }

        content_text = file_result.get("content_text")
        content_kind = "text"
        content_base64 = None
        if content_text is None:
            download_url = file_result.get("download_url") or f"github://{repository_full_name}/{file_path}"
            return {
                "ok": False,
                "mode": "external_asset_materialization_result",
                "materialization_status": "binary_materialization_not_supported_yet",
                "source_download_url": download_url,
                "source": file_result,
            }

        staged = external_asset_intake_service.stage_asset_request(
            source_type="github_repository_file",
            source_ref=f"github://{repository_full_name}/{file_path}",
            asset_role=asset_role,
            project_hint=project_hint,
            repository_full_name=repository_full_name,
            destination_path=destination_path,
            content_text=content_text,
            content_base64=content_base64,
            content_kind=content_kind,
        )
        return {
            "ok": True,
            "mode": "external_asset_materialization_result",
            "materialization_status": "materialized_to_stage",
            "source": file_result,
            "staged_asset": staged["staged_asset"],
        }

    def get_package(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "mode": "external_asset_materialization_package",
            "package": {
                "status": self.get_status(),
                "intake_package": external_asset_intake_service.get_package(),
                "package_status": "external_asset_materialization_ready",
            },
        }


external_asset_materialization_service = ExternalAssetMaterializationService()
