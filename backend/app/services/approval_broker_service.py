import json
import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


class ApprovalBrokerService:
    def __init__(self, storage_path: str = "data/approval_broker_store.json") -> None:
        self.storage_path = Path(storage_path)
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        self._ensure_store()

    def _ensure_store(self) -> None:
        if not self.storage_path.exists():
            self._write_store({"requests": []})

    def _read_store(self) -> Dict[str, Any]:
        if not self.storage_path.exists():
            return {"requests": []}
        return json.loads(self.storage_path.read_text(encoding="utf-8"))

    def _write_store(self, payload: Dict[str, Any]) -> None:
        self.storage_path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def create_request(
        self,
        source: str,
        action_type: str,
        risk_level: str,
        summary: str,
        details: Optional[Dict[str, Any]] = None,
        requires_manual_confirmation: bool = True,
        suggested_response: str = "ALTERA",
        allowed_responses: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        request_id = f"apr_{uuid.uuid4().hex[:12]}"
        payload = {
            "request_id": request_id,
            "source": source,
            "action_type": action_type,
            "risk_level": risk_level,
            "summary": summary,
            "details": details or {},
            "requires_manual_confirmation": requires_manual_confirmation,
            "suggested_response": suggested_response,
            "allowed_responses": allowed_responses or ["OK", "ALTERA", "REJEITA"],
            "status": "pending",
            "response": None,
            "created_at": self._now(),
            "updated_at": self._now(),
        }
        with self._lock:
            store = self._read_store()
            store.setdefault("requests", []).append(payload)
            self._write_store(store)
        return payload

    def list_requests(self, status: Optional[str] = None) -> Dict[str, Any]:
        with self._lock:
            store = self._read_store()
        requests = store.get("requests", [])
        if status:
            requests = [item for item in requests if item.get("status") == status]
        return {
            "ok": True,
            "mode": "approval_queue",
            "count": len(requests),
            "requests": requests,
        }

    def get_request(self, request_id: str) -> Optional[Dict[str, Any]]:
        with self._lock:
            store = self._read_store()
        for item in store.get("requests", []):
            if item.get("request_id") == request_id:
                return item
        return None

    def respond(self, request_id: str, response: str, note: str = "") -> Dict[str, Any]:
        with self._lock:
            store = self._read_store()
            requests = store.get("requests", [])
            for item in requests:
                if item.get("request_id") == request_id:
                    if response not in item.get("allowed_responses", []):
                        raise ValueError("invalid_response")
                    item["response"] = response
                    item["status"] = "approved" if response == "OK" else "rejected" if response == "REJEITA" else "needs_changes"
                    item["note"] = note
                    item["updated_at"] = self._now()
                    self._write_store(store)
                    return item
        raise ValueError("request_not_found")


approval_broker_service = ApprovalBrokerService()
