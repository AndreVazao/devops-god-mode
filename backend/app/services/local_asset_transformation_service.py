from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

from app.services.local_asset_workspace_service import local_asset_workspace_service


class LocalAssetTransformationService:
    def get_status(self) -> Dict[str, Any]:
        workspace = local_asset_workspace_service.get_status()
        return {
            "ok": True,
            "mode": "local_asset_transformation_status",
            "workspace_root": workspace["workspace_root"],
            "status": "local_asset_transformation_ready",
        }

    def _resolve_path(self, workspace_file: str) -> Path:
        return Path(workspace_file)

    def transform_text_asset(
        self,
        workspace_file: str,
        operation: str,
        transform_value: str,
        output_suffix: str = ".generated",
    ) -> Dict[str, Any]:
        source_path = self._resolve_path(workspace_file)
        if not source_path.exists():
            return {
                "ok": False,
                "mode": "local_asset_transformation_result",
                "transformation_status": "workspace_file_not_found",
                "workspace_file": workspace_file,
            }

        content = source_path.read_text(encoding="utf-8")
        if operation == "prefix":
            transformed = transform_value + content
        elif operation == "suffix":
            transformed = content + transform_value
        elif operation == "replace":
            try:
                old_value, new_value = transform_value.split("=>", 1)
            except ValueError:
                return {
                    "ok": False,
                    "mode": "local_asset_transformation_result",
                    "transformation_status": "invalid_replace_expression",
                    "workspace_file": workspace_file,
                }
            transformed = content.replace(old_value, new_value)
        else:
            return {
                "ok": False,
                "mode": "local_asset_transformation_result",
                "transformation_status": "unsupported_operation",
                "operation": operation,
            }

        output_path = source_path.parent / f"{source_path.stem}{output_suffix}{source_path.suffix}"
        output_path.write_text(transformed, encoding="utf-8")

        manifest_path = output_path.with_suffix(output_path.suffix + ".transform.json")
        manifest_payload = {
            "source_file": str(source_path),
            "output_file": str(output_path),
            "operation": operation,
            "transform_value": transform_value,
        }
        manifest_path.write_text(
            json.dumps(manifest_payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        return {
            "ok": True,
            "mode": "local_asset_transformation_result",
            "transformation_status": "transformed",
            "source_file": str(source_path),
            "output_file": str(output_path),
            "transform_manifest": str(manifest_path),
            "operation": operation,
        }

    def duplicate_workspace_asset(
        self,
        workspace_file: str,
        duplicate_name: str,
    ) -> Dict[str, Any]:
        source_path = self._resolve_path(workspace_file)
        if not source_path.exists():
            return {
                "ok": False,
                "mode": "local_asset_transformation_duplicate_result",
                "duplicate_status": "workspace_file_not_found",
                "workspace_file": workspace_file,
            }

        extension = source_path.suffix
        duplicate_path = source_path.parent / f"{duplicate_name}{extension}"
        duplicate_path.write_bytes(source_path.read_bytes())

        return {
            "ok": True,
            "mode": "local_asset_transformation_duplicate_result",
            "duplicate_status": "duplicated",
            "source_file": str(source_path),
            "duplicate_file": str(duplicate_path),
        }

    def get_package(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "mode": "local_asset_transformation_package",
            "package": {
                "status": self.get_status(),
                "workspace": local_asset_workspace_service.get_package(),
                "package_status": "local_asset_transformation_ready",
            },
        }


local_asset_transformation_service = LocalAssetTransformationService()
