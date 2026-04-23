from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any, Dict, List


class PreviewPackagingService:
    def __init__(self, package_root: str = "data/preview_packages") -> None:
        self.package_root = Path(package_root)
        self.package_root.mkdir(parents=True, exist_ok=True)

    def get_status(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "mode": "preview_packaging_status",
            "package_root": str(self.package_root),
            "status": "preview_packaging_ready",
        }

    def _relative_preview_block(self, relative_path: str) -> str:
        lowered = relative_path.lower()
        if lowered.endswith(".svg"):
            return f"<img src='{relative_path}' alt='{relative_path}' style='max-width:320px;max-height:320px;border:1px solid #333;border-radius:12px;background:#111;padding:8px;'/>"
        if lowered.endswith((".png", ".jpg", ".jpeg", ".webp", ".gif")):
            return f"<img src='{relative_path}' alt='{relative_path}' style='max-width:320px;max-height:320px;border:1px solid #333;border-radius:12px;background:#111;padding:8px;'/>"
        if lowered.endswith((".json", ".txt", ".md", ".html", ".css", ".js", ".ts", ".xml")):
            return f"<iframe src='{relative_path}' style='width:100%;height:280px;border:1px solid #333;border-radius:12px;background:#111;'></iframe>"
        return f"<a href='{relative_path}'>Abrir ficheiro</a>"

    def create_preview_bundle(
        self,
        bundle_name: str,
        workspace_files: List[str],
        title: str | None = None,
    ) -> Dict[str, Any]:
        if not workspace_files:
            return {
                "ok": False,
                "mode": "preview_packaging_bundle_result",
                "bundle_status": "no_workspace_files",
            }

        bundle_dir = self.package_root / bundle_name
        assets_dir = bundle_dir / "assets"
        assets_dir.mkdir(parents=True, exist_ok=True)
        copied_assets: List[Dict[str, Any]] = []
        preview_sections: List[str] = []

        for original in workspace_files:
            source_path = Path(original)
            if not source_path.exists():
                return {
                    "ok": False,
                    "mode": "preview_packaging_bundle_result",
                    "bundle_status": "workspace_file_not_found",
                    "workspace_file": original,
                }
            target_path = assets_dir / source_path.name
            shutil.copyfile(source_path, target_path)
            rel = f"assets/{target_path.name}"
            copied_assets.append(
                {
                    "source_file": str(source_path),
                    "packaged_file": str(target_path),
                    "relative_path": rel,
                    "file_size": target_path.stat().st_size,
                }
            )
            preview_sections.append(
                "<section style='margin-bottom:24px;padding:16px;border:1px solid #2a2a2a;border-radius:16px;background:#161616;'>"
                f"<h2 style='margin-top:0;color:#fff;font-family:Arial,sans-serif'>{target_path.name}</h2>"
                f"<p style='color:#aaa;font-family:Arial,sans-serif'>Origem: {source_path}</p>"
                f"{self._relative_preview_block(rel)}"
                "</section>"
            )

        page_title = title or bundle_name
        index_path = bundle_dir / "index.html"
        index_html = (
            "<!DOCTYPE html><html lang='pt'><head><meta charset='utf-8'/>"
            f"<title>{page_title}</title>"
            "<meta name='viewport' content='width=device-width, initial-scale=1'/>"
            "</head><body style='background:#0b0b0b;color:#eaeaea;padding:24px;font-family:Arial,sans-serif;'>"
            f"<h1 style='margin-top:0'>{page_title}</h1>"
            "<p style='color:#9aa0a6'>Preview local do pacote derivado.</p>"
            f"{''.join(preview_sections)}"
            "</body></html>"
        )
        index_path.write_text(index_html, encoding="utf-8")

        manifest_path = bundle_dir / "bundle.manifest.json"
        manifest_path.write_text(
            json.dumps(
                {
                    "bundle_name": bundle_name,
                    "title": page_title,
                    "index_file": str(index_path),
                    "assets": copied_assets,
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )

        return {
            "ok": True,
            "mode": "preview_packaging_bundle_result",
            "bundle_status": "preview_bundle_created",
            "bundle_name": bundle_name,
            "bundle_dir": str(bundle_dir),
            "index_file": str(index_path),
            "manifest_file": str(manifest_path),
            "asset_count": len(copied_assets),
            "assets": copied_assets,
        }

    def create_bundle_archive(self, bundle_name: str) -> Dict[str, Any]:
        bundle_dir = self.package_root / bundle_name
        if not bundle_dir.exists():
            return {
                "ok": False,
                "mode": "preview_packaging_archive_result",
                "archive_status": "bundle_not_found",
                "bundle_name": bundle_name,
            }

        archive_base = self.package_root / f"{bundle_name}-archive"
        archive_file = shutil.make_archive(str(archive_base), "zip", root_dir=bundle_dir)
        archive_path = Path(archive_file)
        archive_manifest = archive_path.with_suffix(".zip.manifest.json")
        archive_manifest.write_text(
            json.dumps(
                {
                    "bundle_name": bundle_name,
                    "bundle_dir": str(bundle_dir),
                    "archive_file": str(archive_path),
                    "archive_size": archive_path.stat().st_size,
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )

        return {
            "ok": True,
            "mode": "preview_packaging_archive_result",
            "archive_status": "preview_archive_created",
            "bundle_name": bundle_name,
            "bundle_dir": str(bundle_dir),
            "archive_file": str(archive_path),
            "archive_manifest": str(archive_manifest),
            "archive_size": archive_path.stat().st_size,
        }

    def get_package(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "mode": "preview_packaging_package",
            "package": {
                "status": self.get_status(),
                "package_status": "preview_packaging_ready",
            },
        }


preview_packaging_service = PreviewPackagingService()
