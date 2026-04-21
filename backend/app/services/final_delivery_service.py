from typing import Any, Dict, List

from app.services.build_catalog_service import build_catalog_service


class FinalDeliveryService:
    def get_deliveries(self) -> Dict[str, Any]:
        catalogs = build_catalog_service.get_catalogs()["catalogs"]
        deliveries: List[Dict[str, Any]] = []
        for catalog in catalogs:
            deliveries.append(
                {
                    "final_delivery_id": f"final_delivery_{catalog['recovery_project_id']}",
                    "recovery_project_id": catalog["recovery_project_id"],
                    "deliverable_count": catalog["output_count"],
                    "primary_deliverable_name": catalog["primary_output_name"],
                    "delivery_status": "ready_for_user_delivery",
                }
            )
        return {"ok": True, "mode": "final_deliveries", "deliveries": deliveries}

    def get_delivery_actions(self, recovery_project_id: str | None = None) -> Dict[str, Any]:
        entries = build_catalog_service.get_output_entries(recovery_project_id)["entries"]
        actions: List[Dict[str, Any]] = []
        for entry in entries:
            primary = entry["output_type"] == "apk"
            actions.append(
                {
                    "final_delivery_action_id": f"final_delivery_action_{entry['build_output_entry_id']}",
                    "recovery_project_id": entry["recovery_project_id"],
                    "build_output_entry_id": entry["build_output_entry_id"],
                    "action_type": "download_primary_output" if primary else "download_secondary_output",
                    "action_label": f"Descarregar {entry['display_name']}",
                    "action_status": "ready",
                }
            )
        return {"ok": True, "mode": "final_delivery_actions", "actions": actions}

    def get_delivery_package(self, recovery_project_id: str) -> Dict[str, Any]:
        delivery = next(
            item for item in self.get_deliveries()["deliveries"] if item["recovery_project_id"] == recovery_project_id
        )
        package = {
            "delivery": delivery,
            "actions": self.get_delivery_actions(recovery_project_id)["actions"],
            "mobile_compact": True,
            "package_status": delivery["delivery_status"],
        }
        return {"ok": True, "mode": "final_delivery_package", "package": package}

    def get_next_delivery_action(self) -> Dict[str, Any]:
        deliveries = self.get_deliveries()["deliveries"]
        next_delivery = deliveries[0] if deliveries else None
        return {
            "ok": True,
            "mode": "next_final_delivery_action",
            "next_delivery_action": {
                "final_delivery_id": next_delivery["final_delivery_id"],
                "recovery_project_id": next_delivery["recovery_project_id"],
                "action": "surface_primary_download_action_to_user",
                "delivery_status": next_delivery["delivery_status"],
            }
            if next_delivery
            else None,
        }


final_delivery_service = FinalDeliveryService()
