import json
import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from app.services.github_service import github_service


class ExternalAssetIntakeService:
    def __init__(self, storage_path: str = "data/external_asset_intake.json") -> None:
        self.storage_path = Path(storage_path)
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        self._ensure_store()

    def _ensure_store(self) -> None:
        if self.storage_path.exists():
            return
        self._write_store(
            {
                "sources": [
                    {
                        "source_id": "source_browser_web_services",
                        "source_type": "browser_web_service",
                        "display_name": "Browser Web Services",
                        "source_status": "ready_for_intake",
                    },
                    {
                        "source_id": "source_drive_like_storage",
                        "source_type": "drive_like_storage",
                        "display_name": "Drive Like Storage",
                        "source_status": "planned_ready",
                    },
                    {
                        "source_id": "source_github_asset_repo",
                        "source_type": "github_repository",
                        "display_name": "GitHub Asset Publishing",
                        "source_status": "ready_for_repo_publish",
                    },
                ],
                "staged_assets": [],
            }
        )

    def _read_store(self) -> Dict[str, Any]:
        self._ensure_store()
        return json.loads(self.storage_path.read_text(encoding="utf-8"))

    def _write_store(self, payload: Dict[str, Any]) -> None:
        self.storage_path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def get_sources(self) -> Dict[str, Any]:
        store = self._read_store()
        return {
            "ok": True,
            "mode": "external_asset_sources",
            "sources": store.get("sources", []),
        }

    def stage_asset_request(
        self,
        source_type: str,
        source_ref: str,
        asset_role: str,
        project_hint: str | None = None,
        repository_full_name: str | None = None,
        destination_path: str | None = None,
    ) -> Dict[str, Any]:
        normalized_source_type = (source_type or "").strip()
        normalized_source_ref = (source_ref or "").strip()
        normalized_asset_role = (asset_role or "").strip()
        if not normalized_source_type:
            raise ValueError("empty_source_type")
        if not normalized_source_ref:
            raise ValueError("empty_source_ref")
        if not normalized_asset_role:
            raise ValueError("empty_asset_role")

        with self._lock:
            store = self._read_store()
            item = {
                "staged_asset_id": f"staged_asset_{uuid.uuid4().hex[:12]}",
                "source_type": normalized_source_type,
                "source_ref": normalized_source_ref,
                "asset_role": normalized_asset_role,
                "project_hint": project_hint,
                "repository_full_name": repository_full_name,
                "destination_path": destination_path,
                "staging_status": "staged_locally",
                "traceability_status": "source_recorded",
                "created_at": self._now(),
                "updated_at": self._now(),
            }
            store.setdefault("staged_assets", []).append(item)
            self._write_store(store)
        return {
            "ok": True,
            "mode": "external_asset_staged",
            "staged_asset": item,
        }

    def get_staged_assets(self, project_hint: str | None = None) -> Dict[str, Any]:
        store = self._read_store()
        assets = store.get("staged_assets", [])
        if project_hint:
            assets = [item for item in assets if item.get("project_hint") == project_hint]
        return {
            "ok": True,
            "mode": "external_asset_staged_assets",
            "count": len(assets),
            "staged_assets": assets,
        }

    def build_github_publish_plan(
        self,
        repository_full_name: str,
        project_hint: str | None = None,
    ) -> Dict[str, Any]:
        staged_assets = self.get_staged_assets(project_hint=project_hint)["staged_assets"]
        repo_assets = [
            item
            for item in staged_assets
            if item.get("repository_full_name") in {None, repository_full_name}
        ]
        plan_items: List[Dict[str, Any]] = []
        for item in repo_assets:
            plan_items.append(
                {
                    "publish_item_id": f"publish_item_{item['staged_asset_id']}",
                    "repository_full_name": repository_full_name,
                    "asset_role": item["asset_role"],
                    "source_ref": item["source_ref"],
                    "destination_path": item.get("destination_path")
                    or f"assets/{item['asset_role']}/{item['staged_asset_id']}",
                    "publish_status": "planned",
                }
            )
        return {
            "ok": True,
            "mode": "external_asset_github_publish_plan",
            "github_configured": github_service.is_configured(),
            "repository_full_name": repository_full_name,
            "project_hint": project_hint,
            "planned_items": plan_items,
            "planned_count": len(plan_items),
        }

    def get_package(self) -> Dict[str, Any]:
        staged_assets = self.get_staged_assets()["staged_assets"]
        return {
            "ok": True,
            "mode": "external_asset_intake_package",
            "package": {
                "sources": self.get_sources()["sources"],
                "staged_assets": staged_assets,
                "github_configured": github_service.is_configured(),
                "staged_count": len(staged_assets),
                "package_status": "external_asset_intake_ready",
            },
        }

    def get_status(self) -> Dict[str, Any]:
        package = self.get_package()["package"]
        return {
            "ok": True,
            "mode": "external_asset_intake_status",
            "sources_count": len(package["sources"]),
            "staged_count": package["staged_count"],
            "github_configured": package["github_configured"],
            "status": package["package_status"],
        }


external_asset_intake_service = ExternalAssetIntakeService()
