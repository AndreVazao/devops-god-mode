from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

from app.services.preview_packaging_service import preview_packaging_service
from app.services.workspace_publish_bridge_service import workspace_publish_bridge_service


class BundlePublishLinkService:
    def get_status(self) -> Dict[str, Any]:
        preview_status = preview_packaging_service.get_status()
        bridge_status = workspace_publish_bridge_service.get_status()
        return {
            "ok": True,
            "mode": "bundle_publish_link_status",
            "package_root": preview_status["package_root"],
            "bridge_status": bridge_status["status"],
            "status": "bundle_publish_link_ready",
        }

    def _collect_bundle_files(self, bundle_dir: Path, include_archive: bool) -> List[Path]:
        files: List[Path] = []
        index_file = bundle_dir / "index.html"
        manifest_file = bundle_dir / "bundle.manifest.json"
        assets_dir = bundle_dir / "assets"
        if index_file.exists():
            files.append(index_file)
        if manifest_file.exists():
            files.append(manifest_file)
        if assets_dir.exists():
            for child in sorted(assets_dir.iterdir()):
                if child.is_file():
                    files.append(child)
        if include_archive:
            archive_file = bundle_dir.parent / f"{bundle_dir.name}-archive.zip"
            archive_manifest = bundle_dir.parent / f"{bundle_dir.name}-archive.zip.manifest.json"
            if archive_file.exists():
                files.append(archive_file)
            if archive_manifest.exists():
                files.append(archive_manifest)
        return files

    def restage_preview_bundle(
        self,
        bundle_name: str,
        repository_full_name: str,
        destination_root: str,
        project_hint: str | None = None,
        include_archive: bool = True,
    ) -> Dict[str, Any]:
        bundle_dir = Path(preview_packaging_service.package_root) / bundle_name
        if not bundle_dir.exists():
            return {
                "ok": False,
                "mode": "bundle_publish_link_restage_result",
                "restage_status": "bundle_not_found",
                "bundle_name": bundle_name,
            }

        files = self._collect_bundle_files(bundle_dir=bundle_dir, include_archive=include_archive)
        if not files:
            return {
                "ok": False,
                "mode": "bundle_publish_link_restage_result",
                "restage_status": "bundle_files_not_found",
                "bundle_name": bundle_name,
            }

        results: List[Dict[str, Any]] = []
        for file_path in files:
            if file_path.parent.name == "assets":
                destination_path = f"{destination_root}/assets/{file_path.name}"
            else:
                destination_path = f"{destination_root}/{file_path.name}"
            result = workspace_publish_bridge_service.restage_workspace_file(
                workspace_file=str(file_path),
                asset_role="preview_bundle_asset",
                source_ref=f"preview-bundle://{bundle_name}/{file_path.name}",
                project_hint=project_hint,
                repository_full_name=repository_full_name,
                destination_path=destination_path,
            )
            results.append(result)

        return {
            "ok": True,
            "mode": "bundle_publish_link_restage_result",
            "restage_status": "bundle_restaged",
            "bundle_name": bundle_name,
            "restaged_count": len(results),
            "results": results,
        }

    async def dry_run_publish_preview_bundle(
        self,
        bundle_name: str,
        repository_full_name: str,
        destination_root: str,
        project_hint: str | None = None,
        branch: str | None = None,
        include_archive: bool = True,
    ) -> Dict[str, Any]:
        restaged = self.restage_preview_bundle(
            bundle_name=bundle_name,
            repository_full_name=repository_full_name,
            destination_root=destination_root,
            project_hint=project_hint,
            include_archive=include_archive,
        )
        if not restaged.get("ok"):
            return {
                "ok": False,
                "mode": "bundle_publish_link_publish_result",
                "publish_status": "bundle_restage_failed",
                "restage": restaged,
            }

        publish_result = await workspace_publish_bridge_service.publish_workspace_file(
            workspace_file=str((Path(preview_packaging_service.package_root) / bundle_name / "index.html")),
            asset_role="preview_bundle_index",
            source_ref=f"preview-bundle://{bundle_name}/index.html",
            repository_full_name=repository_full_name,
            destination_path=f"{destination_root}/index.html",
            project_hint=project_hint,
            branch=branch,
            content_kind="text",
            dry_run=True,
        )
        return {
            "ok": True,
            "mode": "bundle_publish_link_publish_result",
            "publish_status": "dry_run_ready",
            "restage": restaged,
            "publish_result": publish_result,
        }

    def get_package(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "mode": "bundle_publish_link_package",
            "package": {
                "status": self.get_status(),
                "preview_packaging": preview_packaging_service.get_package(),
                "workspace_publish_bridge": workspace_publish_bridge_service.get_package(),
                "package_status": "bundle_publish_link_ready",
            },
        }


bundle_publish_link_service = BundlePublishLinkService()
