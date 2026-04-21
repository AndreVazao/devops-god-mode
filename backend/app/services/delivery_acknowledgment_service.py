from typing import Any, Dict, List

from app.services.final_delivery_service import final_delivery_service


class DeliveryAcknowledgmentService:
    def get_acknowledgments(self) -> Dict[str, Any]:
        deliveries = final_delivery_service.get_deliveries()["deliveries"]
        acknowledgments: List[Dict[str, Any]] = []
        for delivery in deliveries:
            acknowledgments.append(
                {
                    "delivery_acknowledgment_id": f"delivery_ack_{delivery['recovery_project_id']}",
                    "recovery_project_id": delivery["recovery_project_id"],
                    "acknowledged_output_count": 0,
                    "pending_ack_count": delivery["deliverable_count"],
                    "acknowledgment_status": "awaiting_user_acknowledgment",
                }
            )
        return {"ok": True, "mode": "delivery_acknowledgments", "acknowledgments": acknowledgments}

    def get_ack_events(self, recovery_project_id: str | None = None) -> Dict[str, Any]:
        actions = final_delivery_service.get_delivery_actions(recovery_project_id)["actions"]
        events: List[Dict[str, Any]] = []
        for action in actions:
            events.append(
                {
                    "delivery_ack_event_id": f"delivery_ack_event_{action['final_delivery_action_id']}",
                    "recovery_project_id": action["recovery_project_id"],
                    "final_delivery_action_id": action["final_delivery_action_id"],
                    "event_type": "download_pending",
                    "event_label": f"{action['action_label']} pendente",
                    "event_status": "pending",
                }
            )
        return {"ok": True, "mode": "delivery_ack_events", "events": events}

    def get_ack_package(self, recovery_project_id: str) -> Dict[str, Any]:
        acknowledgment = next(
            item for item in self.get_acknowledgments()["acknowledgments"] if item["recovery_project_id"] == recovery_project_id
        )
        package = {
            "acknowledgment": acknowledgment,
            "events": self.get_ack_events(recovery_project_id)["events"],
            "mobile_compact": True,
            "package_status": acknowledgment["acknowledgment_status"],
        }
        return {"ok": True, "mode": "delivery_ack_package", "package": package}

    def get_next_ack_action(self) -> Dict[str, Any]:
        acknowledgments = self.get_acknowledgments()["acknowledgments"]
        next_ack = acknowledgments[0] if acknowledgments else None
        return {
            "ok": True,
            "mode": "next_delivery_ack_action",
            "next_ack_action": {
                "delivery_acknowledgment_id": next_ack["delivery_acknowledgment_id"],
                "recovery_project_id": next_ack["recovery_project_id"],
                "action": "confirm_output_delivered_or_downloaded",
                "acknowledgment_status": next_ack["acknowledgment_status"],
            }
            if next_ack
            else None,
        }


delivery_acknowledgment_service = DeliveryAcknowledgmentService()
