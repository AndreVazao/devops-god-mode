from __future__ import annotations

import base64
import json
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

    def _finalize_filename(self, filename: str, content_type: str | None) -> str:
        if Path(filename).suffix:
            return filename
        guessed_extension = mimetypes.guess_extension((content_type or "").split(";")[0].strip())
        if guessed_extension:
            return f"{filename}{guessed_extension}"
        return filename

    def _infer_content_kind(self, filename: str, content_type: str | None) -> str:
        lowered = filename.lower()
        if lowered.endswith(".svg"):
            return "svg_text"
        if lowered.endswith((".json", ".txt", ".md", ".html", ".css", ".js", ".ts", ".xml")):
            return "text"
        if content_type and content_type.startswith("text/"):
            return "text"
        return "binary"

    def _build_request_headers(
        self,
        auth_mode: str | None = None,
        auth_value: str | None = None,
        extra_headers: Dict[str, str] | None = None,
        user_agent: str | None = None,
    ) -> Dict[str, str]:
        headers: Dict[str, str] = {}
        if user_agent:
            headers["User-Agent"] = user_agent
        if extra_headers:
            headers.update({str(k): str(v) for k, v in extra_headers.items()})
        normalized_mode = (auth_mode or "none").strip().lower()
        if normalized_mode == "bearer" and auth_value:
            headers["Authorization"] = f"Bearer {auth_value}"
        elif normalized_mode == "basic" and auth_value:
            headers["Authorization"] = f"Basic {auth_value}"
        elif normalized_mode == "header" and auth_value:
            try:
                header_name, header_value = auth_value.split(":", 1)
                headers[header_name.strip()] = header_value.strip()
            except ValueError:
                headers["Authorization"] = auth_value
        return headers

    def _write_fetch_manifest(
        self,
        download_path: Path,
        source_url: str,
        content_type: str | None,
        payload_mode: str,
        auth_mode: str,
        extra_headers: Dict[str, str] | None,
        bytes_downloaded: int,
        content_kind: str,
    ) -> str:
        manifest_path = download_path.with_suffix(download_path.suffix + ".fetch.json")
        manifest_payload = {
            "source_url": source_url,
            "download_path": str(download_path),
            "content_type": content_type,
            "content_kind": content_kind,
            "payload_mode": payload_mode,
            "bytes_downloaded": bytes_downloaded,
            "auth_mode": auth_mode,
            "extra_header_names": sorted(list((extra_headers or {}).keys())),
        }
        manifest_path.write_text(
            json.dumps(manifest_payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return str(manifest_path)

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
        auth_mode: str | None = None,
        auth_value: str | None = None,
        extra_headers: Dict[str, str] | None = None,
        user_agent: str | None = None,
    ) -> Dict[str, Any]:
        initial_filename = self._infer_filename(source_url)
        target_dir = self.download_root / (project_hint or "general")
        target_dir.mkdir(parents=True, exist_ok=True)
        headers = self._build_request_headers(
            auth_mode=auth_mode,
            auth_value=auth_value,
            extra_headers=extra_headers,
            user_agent=user_agent,
        )

        async with httpx.AsyncClient(follow_redirects=True, timeout=30.0) as client:
            response = await client.get(source_url, headers=headers or None)
            response.raise_for_status()
            raw_bytes = response.content
            content_type = response.headers.get("content-type")

        filename = self._finalize_filename(initial_filename, content_type)
        download_path = target_dir / filename
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

        fetch_manifest = self._write_fetch_manifest(
            download_path=download_path,
            source_url=source_url,
            content_type=content_type,
            payload_mode=payload_mode,
            auth_mode=(auth_mode or "none"),
            extra_headers=extra_headers,
            bytes_downloaded=len(raw_bytes),
            content_kind=content_kind,
        )

        return {
            "ok": True,
            "mode": "external_fetch_runtime_result",
            "fetch_status": "fetched_and_staged",
            "source_url": source_url,
            "download_path": str(download_path),
            "fetch_manifest": fetch_manifest,
            "content_type": content_type,
            "content_kind": content_kind,
            "payload_mode": payload_mode,
            "bytes_downloaded": len(raw_bytes),
            "staged_asset": staged["staged_asset"],
            "auth_mode": (auth_mode or "none"),
            "extra_header_count": len(extra_headers or {}),
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
