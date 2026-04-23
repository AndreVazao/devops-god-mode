from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Dict, List


class OperatorInputRequestService:
    def __init__(self, store_path: str = "data/operator_input_requests.json") -> None:
        self.store_path = Path(store_path)
        self.store_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.store_path.exists():
            self.store_path.write_text(json.dumps({"requests": []}, ensure_ascii=False, indent=2), encoding="utf-8")

    def _read_store(self) -> Dict[str, Any]:
        return json.loads(self.store_path.read_text(encoding="utf-8"))

    def _write_store(self, payload: Dict[str, Any]) -> None:
        self.store_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    def get_status(self) -> Dict[str, Any]:
        store = self._read_store()
        return {
            "ok": True,
            "mode": "operator_input_request_status",
            "store_path": str(self.store_path),
            "request_count": len(store.get("requests", [])),
            "status": "operator_input_request_ready",
        }

    def create_request(
        self,
        tenant_id: str,
        thread_id: str,
        provider_name: str,
        request_kind: str,
        title: str,
        prompt_text: str,
        field_label: str,
        field_mode: str = "text",
        is_sensitive: bool = True,
    ) -> Dict[str, Any]:
        store = self._read_store()
        request_id = f"input-{len(store.get('requests', [])) + 1:05d}"
        request_payload = {
            "request_id": request_id,
            "tenant_id": tenant_id,
            "thread_id": thread_id,
            "provider_name": provider_name,
            "request_kind": request_kind,
            "title": title,
            "prompt_text": prompt_text,
            "field_label": field_label,
            "field_mode": field_mode,
            "is_sensitive": is_sensitive,
            "status": "waiting_operator_input",
            "created_at": datetime.now(UTC).isoformat(),
            "submitted_at": None,
            "submitted_value_masked": None,
        }
        requests = store.get("requests", [])
        requests.append(request_payload)
        store["requests"] = requests
        self._write_store(store)
        return {
            "ok": True,
            "mode": "operator_input_request_create_result",
            "create_status": "operator_input_requested",
            "request": request_payload,
        }

    def submit_request(self, request_id: str, submitted_value: str) -> Dict[str, Any]:
        store = self._read_store()
        requests: List[Dict[str, Any]] = store.get("requests", [])
        item = next((req for req in requests if req.get("request_id") == request_id), None)
        if item is None:
            return {
                "ok": False,
                "mode": "operator_input_request_submit_result",
                "submit_status": "request_not_found",
                "request_id": request_id,
            }
        item["status"] = "input_received"
        item["submitted_at"] = datetime.now(UTC).isoformat()
        item["submitted_value_masked"] = (submitted_value[:2] + "***" + submitted_value[-2:]) if len(submitted_value) >= 6 else "***"
        item["transcription_mode"] = "operator_to_backend_field_bridge"
        self._write_store(store)
        return {
            "ok": True,
            "mode": "operator_input_request_submit_result",
            "submit_status": "input_received",
            "request_id": request_id,
            "submitted_value_masked": item["submitted_value_masked"],
            "transcription_mode": item["transcription_mode"],
        }

    def list_requests(self, tenant_id: str | None = None, thread_id: str | None = None) -> Dict[str, Any]:
        store = self._read_store()
        requests = store.get("requests", [])
        if tenant_id:
            requests = [item for item in requests if item.get("tenant_id") == tenant_id]
        if thread_id:
            requests = [item for item in requests if item.get("thread_id") == thread_id]
        return {
            "ok": True,
            "mode": "operator_input_request_list_result",
            "request_count": len(requests),
            "requests": requests,
        }

    def get_package(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "mode": "operator_input_request_package",
            "package": {
                "status": self.get_status(),
                "package_status": "operator_input_request_ready",
            },
        }


operator_input_request_service = OperatorInputRequestService()
