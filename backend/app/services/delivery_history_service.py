from typing import Any, Dict, List

from app.services.delivery_acknowledgment_service import delivery_acknowledgment_service


class DeliveryHistoryService:
    def get_histories(self) -> Dict[str, Any]:
        acknowledgments = delivery_acknowledgment_service.get_acknowledgments()["acknowledgments"]
        histories: List[Dict[str, Any]] = []
        for acknowledgment in acknowledgments:
            histories.append(
                {
                    "delivery_history_id": f"delivery_history_{acknowledgment['recovery_project_id']}",
                    "recovery_project_id": acknowledgment["recovery_project_id"],
                    "total_history_items": acknowledgment["pending_ack_count"],
                    "latest_delivery_state": "download_pending",
                    "history_status": "history_available",
                }
            )
        return {"ok": True, "mode": "delivery_histories", "histories": histories}

    def get_history_records(self, recovery_project_id: str | None = None) -> Dict[str, Any]:
        events = delivery_acknowledgment_service.get_ack_events(recovery_project_id)["events"]
        records: List[Dict[str, Any]] = []
        for event in events:
            records.append(
                {
                    "delivery_history_record_id": f"delivery_history_record_{event['delivery_ack_event_id']}",
                    "recovery_project_id": event["recovery_project_id"],
                    "delivery_ack_event_id": event["delivery_ack_event_id"],
                    "record_type": event["event_type"],
                    "record_label": event["event_label"],
                    "record_status": "open" if event["event_status"] == "pending" else "closed",
                }
            )
        return {"ok": True, "mode": "delivery_history_records", "records": records}

    def get_history_package(self, recovery_project_id: str) -> Dict[str, Any]:
        history = next(
            item for item in self.get_histories()["histories"] if item["recovery_project_id"] == recovery_project_id
        )
        package = {
            "history": history,
            "records": self.get_history_records(recovery_project_id)["records"],
            "mobile_compact": True,
            "package_status": history["history_status"],
        }
        return {"ok": True, "mode": "delivery_history_package", "package": package}

    def get_next_history_action(self) -> Dict[str, Any]:
        histories = self.get_histories()["histories"]
        next_history = histories[0] if histories else None
        return {
            "ok": True,
            "mode": "next_delivery_history_action",
            "next_history_action": {
                "delivery_history_id": next_history["delivery_history_id"],
                "recovery_project_id": next_history["recovery_project_id"],
                "action": "surface_recent_delivery_history",
                "history_status": next_history["history_status"],
            }
            if next_history
            else None,
        }


delivery_history_service = DeliveryHistoryService()
