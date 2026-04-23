from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Dict, List


class OperatorPopupDeliveryService:
    def __init__(self, store_path: str = "data/operator_popup_deliveries.json") -> None:
        self.store_path = Path(store_path)
        self.store_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.store_path.exists():
            self.store_path.write_text(json.dumps({"deliveries": []}, ensure_ascii=False, indent=2), encoding="utf-8")

    def _read_store(self) -> Dict[str, Any]:
        return json.loads(self.store_path.read_text(encoding="utf-8"))

    def _write_store(self, payload: Dict[str, Any]) -> None:
        self.store_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    def get_status(self) -> Dict[str, Any]:
        store = self._read_store()
        return {
            "ok": True,
            "mode": "operator_popup_delivery_status",
            "store_path": str(self.store_path),
            "delivery_count": len(store.get("deliveries", [])),
            "status": "operator_popup_delivery_ready",
        }

    def create_delivery(
        self,
        tenant_id: str,
        thread_id: str,
        popup_kind: str,
        popup_ref_id: str,
        title: str,
        requires_operator_response: bool = True,
    ) -> Dict[str, Any]:
        store = self._read_store()
        delivery_id = f"popup-{len(store.get('deliveries', [])) + 1:05d}"
        delivery = {
            "delivery_id": delivery_id,
            "tenant_id": tenant_id,
            "thread_id": thread_id,
            "popup_kind": popup_kind,
            "popup_ref_id": popup_ref_id,
            "title": title,
            "requires_operator_response": requires_operator_response,
            "status": "pending_delivery",
            "created_at": datetime.now(UTC).isoformat(),
            "last_delivery_attempt_at": None,
            "delivery_attempt_count": 0,
            "last_reissue_at": None,
        }
        deliveries = store.get("deliveries", [])
        deliveries.append(delivery)
        store["deliveries"] = deliveries
        self._write_store(store)
        return {
            "ok": True,
            "mode": "operator_popup_delivery_create_result",
            "create_status": "popup_delivery_created",
            "delivery": delivery,
        }

    def mark_delivered(self, delivery_id: str) -> Dict[str, Any]:
        store = self._read_store()
        deliveries: List[Dict[str, Any]] = store.get("deliveries", [])
        delivery = next((item for item in deliveries if item.get("delivery_id") == delivery_id), None)
        if delivery is None:
            return {
                "ok": False,
                "mode": "operator_popup_delivery_mark_result",
                "mark_status": "delivery_not_found",
                "delivery_id": delivery_id,
            }
        delivery["status"] = "delivered_waiting_operator"
        delivery["last_delivery_attempt_at"] = datetime.now(UTC).isoformat()
        delivery["delivery_attempt_count"] = int(delivery.get("delivery_attempt_count", 0)) + 1
        self._write_store(store)
        return {
            "ok": True,
            "mode": "operator_popup_delivery_mark_result",
            "mark_status": "popup_delivered",
            "delivery_id": delivery_id,
            "delivery_attempt_count": delivery["delivery_attempt_count"],
        }

    def reissue_pending_delivery(self, delivery_id: str) -> Dict[str, Any]:
        store = self._read_store()
        deliveries: List[Dict[str, Any]] = store.get("deliveries", [])
        delivery = next((item for item in deliveries if item.get("delivery_id") == delivery_id), None)
        if delivery is None:
            return {
                "ok": False,
                "mode": "operator_popup_delivery_reissue_result",
                "reissue_status": "delivery_not_found",
                "delivery_id": delivery_id,
            }
        delivery["status"] = "reissue_required"
        delivery["last_reissue_at"] = datetime.now(UTC).isoformat()
        delivery["delivery_attempt_count"] = int(delivery.get("delivery_attempt_count", 0)) + 1
        self._write_store(store)
        return {
            "ok": True,
            "mode": "operator_popup_delivery_reissue_result",
            "reissue_status": "popup_reissue_required",
            "delivery_id": delivery_id,
            "delivery_attempt_count": delivery["delivery_attempt_count"],
        }

    def acknowledge_response(self, delivery_id: str) -> Dict[str, Any]:
        store = self._read_store()
        deliveries: List[Dict[str, Any]] = store.get("deliveries", [])
        delivery = next((item for item in deliveries if item.get("delivery_id") == delivery_id), None)
        if delivery is None:
            return {
                "ok": False,
                "mode": "operator_popup_delivery_ack_result",
                "ack_status": "delivery_not_found",
                "delivery_id": delivery_id,
            }
        delivery["status"] = "operator_response_acknowledged"
        self._write_store(store)
        return {
            "ok": True,
            "mode": "operator_popup_delivery_ack_result",
            "ack_status": "operator_response_acknowledged",
            "delivery_id": delivery_id,
        }

    def list_deliveries(self, tenant_id: str | None = None, thread_id: str | None = None) -> Dict[str, Any]:
        store = self._read_store()
        deliveries = store.get("deliveries", [])
        if tenant_id:
            deliveries = [item for item in deliveries if item.get("tenant_id") == tenant_id]
        if thread_id:
            deliveries = [item for item in deliveries if item.get("thread_id") == thread_id]
        return {
            "ok": True,
            "mode": "operator_popup_delivery_list_result",
            "delivery_count": len(deliveries),
            "deliveries": deliveries,
        }

    def get_package(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "mode": "operator_popup_delivery_package",
            "package": {
                "status": self.get_status(),
                "package_status": "operator_popup_delivery_ready",
            },
        }


operator_popup_delivery_service = OperatorPopupDeliveryService()
