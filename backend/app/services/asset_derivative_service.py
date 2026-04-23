from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict


class AssetDerivativeService:
    def get_status(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "mode": "asset_derivative_status",
            "status": "asset_derivative_ready",
        }

    def create_svg_wrapper(
        self,
        workspace_file: str,
        output_name: str,
        title: str | None = None,
        background: str | None = None,
    ) -> Dict[str, Any]:
        source_path = Path(workspace_file)
        if not source_path.exists():
            return {
                "ok": False,
                "mode": "asset_derivative_svg_wrapper_result",
                "derivative_status": "workspace_file_not_found",
                "workspace_file": workspace_file,
            }

        source_text = source_path.read_text(encoding="utf-8")
        safe_title = title or output_name
        svg_body = (
            f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 512 512'>"
            f"<title>{safe_title}</title>"
        )
        if background:
            svg_body += f"<rect width='512' height='512' fill='{background}' rx='64' ry='64'/>"
        svg_body += (
            "<foreignObject x='32' y='32' width='448' height='448'>"
            "<div xmlns='http://www.w3.org/1999/xhtml' style='width:100%;height:100%;display:flex;align-items:center;justify-content:center;'>"
            f"<div style='width:100%;height:100%;'>{source_text}</div>"
            "</div>"
            "</foreignObject>"
            "</svg>"
        )

        output_path = source_path.parent / f"{output_name}.svg"
        output_path.write_text(svg_body, encoding="utf-8")

        manifest_path = output_path.with_suffix(".svg.derivative.json")
        manifest_path.write_text(
            json.dumps(
                {
                    "type": "svg_wrapper",
                    "source_file": str(source_path),
                    "output_file": str(output_path),
                    "title": safe_title,
                    "background": background,
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )

        return {
            "ok": True,
            "mode": "asset_derivative_svg_wrapper_result",
            "derivative_status": "svg_wrapper_created",
            "source_file": str(source_path),
            "output_file": str(output_path),
            "manifest_file": str(manifest_path),
        }

    def create_binary_metadata_sidecar(
        self,
        workspace_file: str,
        label: str,
    ) -> Dict[str, Any]:
        source_path = Path(workspace_file)
        if not source_path.exists():
            return {
                "ok": False,
                "mode": "asset_derivative_binary_sidecar_result",
                "derivative_status": "workspace_file_not_found",
                "workspace_file": workspace_file,
            }

        sidecar_path = source_path.with_suffix(source_path.suffix + ".asset.json")
        mime_type = None
        if source_path.suffix.lower() == ".png":
            mime_type = "image/png"
        elif source_path.suffix.lower() == ".jpg" or source_path.suffix.lower() == ".jpeg":
            mime_type = "image/jpeg"
        elif source_path.suffix.lower() == ".webp":
            mime_type = "image/webp"
        elif source_path.suffix.lower() == ".svg":
            mime_type = "image/svg+xml"

        payload = {
            "label": label,
            "source_file": str(source_path),
            "file_name": source_path.name,
            "file_extension": source_path.suffix.lower(),
            "file_size": source_path.stat().st_size,
            "mime_type": mime_type,
        }
        sidecar_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

        return {
            "ok": True,
            "mode": "asset_derivative_binary_sidecar_result",
            "derivative_status": "binary_sidecar_created",
            "source_file": str(source_path),
            "sidecar_file": str(sidecar_path),
        }

    def get_package(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "mode": "asset_derivative_package",
            "package": {
                "status": self.get_status(),
                "package_status": "asset_derivative_ready",
            },
        }


asset_derivative_service = AssetDerivativeService()
