from __future__ import annotations

import base64
import json
import re
from pathlib import Path
from typing import Any, Dict, List

from app.services.external_asset_intake_service import external_asset_intake_service


class LocalAssetWorkspaceService:
    def __init__(self, workspace_root: str = "data/staged_asset_workspace") -> None:
        self.workspace_root = Path(workspace_root)
        self.workspace_root.mkdir(parents=True, exist_ok=True)

    def _safe_segment(self, value: str | None, fallback: str) -> str:
        raw = (value or "").strip()
        if not raw:
            return fallback
        cleaned = re.sub(r"[^a-zA-Z0-9._-]+", "-", raw).strip("-._")
        return cleaned or fallback

    def _target_path(self, staged_asset: Dict[str, Any]) -> Path:
        project_segment = self._safe_segment(
            staged_asset.get("project_hint"),
            "general",
        )
        asset_id = self._safe_segment(
            staged_asset.get("staged_asset_id"),
            "asset",
        )
        destination_path = staged_asset.get("destination_path")
        if destination_path:
            relative_path = Path(destination_path)
        else:
            asset_role = self._safe_segment(staged_asset.get("asset_role"), "asset")
            suffix = ".txt" if staged_asset.get("content_text") is not None else ".bin"
            relative_path = Path(asset_role) / f"{asset_id}{suffix}"
        return self.workspace_root / project_segment / relative_path

    def get_status(self) -> Dict[str, Any]:
        intake_package = external_asset_intake_service.get_package()["package"]
        return {
            "ok": True,
            "mode": "local_asset_workspace_status",
            "workspace_root": str(self.workspace_root),
            "staged_count": intake_package["staged_count"],
            "inline_ready_count": intake_package["inline_ready_count"],
            "status": "local_asset_workspace_ready",
        }

    def materialize_staged_asset_to_disk(self, staged_asset_id: str) -> Dict[str, Any]:
        staged_asset = external_asset_intake_service.get_staged_asset_by_id(staged_asset_id)
        if not staged_asset:
            return {
                "ok": False,
                "mode": "local_asset_workspace_materialization_result",
                "materialization_status": "staged_asset_not_found",
                "staged_asset_id": staged_asset_id,
            }

        target_path = self._target_path(staged_asset)
        target_path.parent.mkdir(parents=True, exist_ok=True)

        content_text = staged_asset.get("content_text")
        content_base64 = staged_asset.get("content_base64")

        if content_text is not None:
            target_path.write_text(content_text, encoding="utf-8")
            payload_mode = "text"
        elif content_base64 is not None:
            target_path.write_bytes(base64.b64decode(content_base64))
            payload_mode = "binary"
        else:
            return {
                "ok": False,
                "mode": "local_asset_workspace_materialization_result",
                "materialization_status": "reference_only_asset",
                "staged_asset_id": staged_asset_id,
                "source_ref": staged_asset.get("source_ref"),
            }

        manifest_path = target_path.with_suffix(target_path.suffix + ".manifest.json")
        manifest_payload = {
            "staged_asset_id": staged_asset_id,
            "project_hint": staged_asset.get("project_hint"),
            "source_type": staged_asset.get("source_type"),
            "source_ref": staged_asset.get("source_ref"),
            "asset_role": staged_asset.get("asset_role"),
            "destination_path": staged_asset.get("destination_path"),
            "payload_mode": payload_mode,
            "workspace_file": str(target_path),
        }
        manifest_path.write_text(
            json.dumps(manifest_payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        return {
            "ok": True,
            "mode": "local_asset_workspace_materialization_result",
            "materialization_status": "materialized_to_workspace",
            "staged_asset_id": staged_asset_id,
            "workspace_file": str(target_path),
            "workspace_manifest": str(manifest_path),
            "payload_mode": payload_mode,
        }

    def materialize_project_assets_to_disk(self, project_hint: str) -> Dict[str, Any]:
        staged_assets = external_asset_intake_service.get_staged_assets(project_hint=project_hint)[
            "staged_assets"
        ]
        results: List[Dict[str, Any]] = [
            self.materialize_staged_asset_to_disk(item["staged_asset_id"])
            for item in staged_assets
        ]
        return {
            "ok": True,
            "mode": "local_asset_workspace_project_materialization",
            "project_hint": project_hint,
            "materialized_count": len([r for r in results if r.get("ok")]),
            "results": results,
        }

    def get_package(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "mode": "local_asset_workspace_package",
            "package": {
                "status": self.get_status(),
                "workspace_root": str(self.workspace_root),
                "package_status": "local_asset_workspace_ready",
            },
        }


local_asset_workspace_service = LocalAssetWorkspaceService()
