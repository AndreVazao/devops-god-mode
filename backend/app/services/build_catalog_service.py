from typing import Any, Dict, List

from app.services.build_artifact_harvest_service import build_artifact_harvest_service


class BuildCatalogService:
    def get_catalogs(self) -> Dict[str, Any]:
        harvests = build_artifact_harvest_service.get_harvests()["harvests"]
        catalogs: List[Dict[str, Any]] = []
        for harvest in harvests:
            items = build_artifact_harvest_service.get_artifact_items(harvest["recovery_project_id"])["items"]
            primary_item = next(
                (item for item in items if item["artifact_name"].lower().endswith(".apk")),
                items[0] if items else None,
            )
            catalogs.append(
                {
                    "build_catalog_id": f"build_catalog_{harvest['recovery_project_id']}",
                    "recovery_project_id": harvest["recovery_project_id"],
                    "output_count": len(items),
                    "primary_output_name": primary_item["normalized_output_name"] if primary_item else "",
                    "catalog_status": "ready_for_delivery",
                }
            )
        return {"ok": True, "mode": "build_catalogs", "catalogs": catalogs}

    def get_output_entries(self, recovery_project_id: str | None = None) -> Dict[str, Any]:
        items = build_artifact_harvest_service.get_artifact_items(recovery_project_id)["items"]
        entries: List[Dict[str, Any]] = []
        for item in items:
            output_type = item["artifact_name"].split(".")[-1].lower() if "." in item["artifact_name"] else "file"
            entries.append(
                {
                    "build_output_entry_id": f"build_output_{item['build_artifact_item_id']}",
                    "recovery_project_id": item["recovery_project_id"],
                    "output_type": output_type,
                    "display_name": item["normalized_output_name"],
                    "source_artifact_name": item["artifact_name"],
                    "delivery_status": "download_ready",
                }
            )
        return {"ok": True, "mode": "build_output_entries", "entries": entries}

    def get_catalog_package(self, recovery_project_id: str) -> Dict[str, Any]:
        catalog = next(
            item for item in self.get_catalogs()["catalogs"] if item["recovery_project_id"] == recovery_project_id
        )
        package = {
            "catalog": catalog,
            "entries": self.get_output_entries(recovery_project_id)["entries"],
            "mobile_compact": True,
            "package_status": catalog["catalog_status"],
        }
        return {"ok": True, "mode": "build_catalog_package", "package": package}

    def get_next_catalog_action(self) -> Dict[str, Any]:
        catalogs = self.get_catalogs()["catalogs"]
        next_catalog = catalogs[0] if catalogs else None
        return {
            "ok": True,
            "mode": "next_build_catalog_action",
            "next_catalog_action": {
                "build_catalog_id": next_catalog["build_catalog_id"],
                "recovery_project_id": next_catalog["recovery_project_id"],
                "action": "surface_primary_output_and_offer_download",
                "catalog_status": next_catalog["catalog_status"],
            }
            if next_catalog
            else None,
        }


build_catalog_service = BuildCatalogService()
