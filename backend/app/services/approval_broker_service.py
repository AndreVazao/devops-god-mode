import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from app.utils.atomic_json_store import AtomicJsonStore


class ApprovalBrokerService:
    def __init__(self, storage_path: str = "data/approval_broker_store.json") -> None:
        self.storage_path = Path(storage_path)
        self._store = AtomicJsonStore(self.storage_path, default_factory=lambda: {"requests": []})

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

        def mutator(state: Dict[str, Any]) -> Dict[str, Any]:
            state.setdefault("requests", []).append(payload)
            return state

        self._store.update(mutator)
        return payload

    def list_requests(self, status: Optional[str] = None) -> Dict[str, Any]:
        state = self._store.load()
        requests = state.get("requests", [])
        if status:
            requests = [item for item in requests if item.get("status") == status]
        return {
            "ok": True,
            "mode": "approval_queue",
            "count": len(requests),
            "requests": requests,
        }

    def get_request(self, request_id: str) -> Optional[Dict[str, Any]]:
        state = self._store.load()
        for item in state.get("requests", []):
            if item.get("request_id") == request_id:
                return item
        return None

    def respond(self, request_id: str, response: str, note: str = "") -> Dict[str, Any]:
        result_item = [None]

        def mutator(state: Dict[str, Any]) -> Dict[str, Any]:
            requests = state.get("requests", [])
            for item in requests:
                if item.get("request_id") == request_id:
                    if response not in item.get("allowed_responses", []):
                        raise ValueError("invalid_response")
                    item["response"] = response
                    item["status"] = "approved" if response == "OK" else "rejected" if response == "REJEITA" else "needs_changes"
                    item["note"] = note
                    item["updated_at"] = self._now()
                    result_item[0] = item
                    return state
            raise ValueError("request_not_found")

        self._store.update(mutator)
        return result_item[0]


approval_broker_service = ApprovalBrokerService()
