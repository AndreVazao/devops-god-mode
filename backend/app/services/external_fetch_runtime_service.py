from __future__ import annotations

import base64
import mimetypes
from pathlib import Path
from typing import Any, Dict
from urllib.parse import urlparse

import httpx

from app.services.external_asset_intake_service import external_asset_intake_service


class ExternalFetchRuntimeService:
    def __init__(self, download_root: str = "data/external_fetch_runtime") -> None:
        self.download_root = Path(download_root)
        self.download_root.mkdir(parents=True, exist_ok=True)

    def _infer_filename(self, source_url: str, fallback: str = "downloaded_asset") -> str:
        parsed = urlparse(source_url)
        candidate = Path(parsed.path).name.strip()
        return candidate or fallback

    def _infer_content_kind(self, filename: str, content_type: str | None) -> str:
        lowered = filename.lower()
        if lowered.endswith(".svg"):
            return "svg_text"
        if lowered.endswith((".json", ".txt", ".md", ".html", ".css", ".js", ".ts", ".xml")):
            return "text"
        if content_type and content_type.startswith("text/"):
            return "text"
        return "binary"

    def get_status(self) -> Dict[str, Any]:
        intake_status = external_asset_intake_service.get_status()
        return {
            "ok": True,
            "mode": "external_fetch_runtime_status",
            "download_root": str(self.download_root),
            "staged_count": intake_status["staged_count"],
            "inline_ready_count": intake_status["inline_ready_count"],
            "status": "external_fetch_runtime_ready",
        }

    async def fetch_url_to_stage(
        self,
        source_url: str,
        asset_role: str,
        project_hint: str | None = None,
        repository_full_name: str | None = None,
        destination_path: str | None = None,
        source_type: str = "external_url",
    ) -> Dict[str, Any]:
        filename = self._infer_filename(source_url)
        target_dir = self.download_root / (project_hint or "general")
        target_dir.mkdir(parents=True, exist_ok=True)
        download_path = target_dir / filename

        async with httpx.AsyncClient(follow_redirects=True, timeout=30.0) as client:
            response = await client.get(source_url)
            response.raise_for_status()
            raw_bytes = response.content
            content_type = response.headers.get("content-type")

        download_path.write_bytes(raw_bytes)
        content_kind = self._infer_content_kind(filename, content_type)

        if content_kind in {"text", "svg_text"}:
            content_text = raw_bytes.decode("utf-8", errors="ignore")
            staged = external_asset_intake_service.stage_asset_request(
                source_type=source_type,
                source_ref=source_url,
                asset_role=asset_role,
                project_hint=project_hint,
                repository_full_name=repository_full_name,
                destination_path=destination_path,
                content_text=content_text,
                content_kind=content_kind,
            )
            payload_mode = "text"
        else:
            staged = external_asset_intake_service.stage_asset_request(
                source_type=source_type,
                source_ref=source_url,
                asset_role=asset_role,
                project_hint=project_hint,
                repository_full_name=repository_full_name,
                destination_path=destination_path,
                content_base64=base64.b64encode(raw_bytes).decode("utf-8"),
                content_kind=content_kind,
            )
            payload_mode = "binary"

        return {
            "ok": True,
            "mode": "external_fetch_runtime_result",
            "fetch_status": "fetched_and_staged",
            "source_url": source_url,
            "download_path": str(download_path),
            "content_type": content_type,
            "payload_mode": payload_mode,
            "staged_asset": staged["staged_asset"],
        }

    def get_package(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "mode": "external_fetch_runtime_package",
            "package": {
                "status": self.get_status(),
                "intake": external_asset_intake_service.get_package(),
                "package_status": "external_fetch_runtime_ready",
            },
        }


external_fetch_runtime_service = ExternalFetchRuntimeService()
