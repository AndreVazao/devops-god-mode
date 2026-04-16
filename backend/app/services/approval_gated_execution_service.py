import json
import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

from app.services.approval_broker_service import approval_broker_service


class ApprovalGatedExecutionService:
    def __init__(self, storage_path: str = "data/approval_gated_execution_store.json") -> None:
        self.storage_path = Path(storage_path)
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        self._ensure_store()

    def _ensure_store(self) -> None:
        if not self.storage_path.exists():
            self._write_store({"executions": []})

    def _read_store(self) -> Dict[str, Any]:
        if not self.storage_path.exists():
            return {"executions": []}
        return json.loads(self.storage_path.read_text(encoding="utf-8"))

    def _write_store(self, payload: Dict[str, Any]) -> None:
        self.storage_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def create_sensitive_execution(
        self,
        action_type: str,
        risk_level: str,
        summary: str,
        repo_full_name: Optional[str] = None,
        target_path: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        approval = approval_broker_service.create_request(
            source="approval_gated_execution",
            action_type=action_type,
            risk_level=risk_level,
            summary=summary,
            details=details or {},
            requires_manual_confirmation=True,
            suggested_response="ALTERA",
            allowed_responses=["OK", "ALTERA", "REJEITA"],
        )
        execution = {
            "execution_id": f"exec_{uuid.uuid4().hex[:12]}",
            "action_type": action_type,
            "risk_level": risk_level,
            "status": "waiting_for_approval",
            "summary": summary,
            "approval_request_id": approval["request_id"],
            "repo_full_name": repo_full_name,
            "target_path": target_path,
            "details": details or {},
            "result": None,
            "created_at": self._now(),
            "updated_at": self._now(),
        }
        with self._lock:
            store = self._read_store()
            store.setdefault("executions", []).append(execution)
            self._write_store(store)
        return execution

    def list_executions(self, status: Optional[str] = None) -> Dict[str, Any]:
        with self._lock:
            store = self._read_store()
        executions = store.get("executions", [])
        if status:
            executions = [item for item in executions if item.get("status") == status]
        return {"ok": True, "mode": "approval_gated_execution_queue", "count": len(executions), "executions": executions}

    def get_execution(self, execution_id: str) -> Optional[Dict[str, Any]]:
        with self._lock:
            store = self._read_store()
        for item in store.get("executions", []):
            if item.get("execution_id") == execution_id:
                return item
        return None

    def sync_with_approval(self, execution_id: str) -> Dict[str, Any]:
        with self._lock:
            store = self._read_store()
            for item in store.get("executions", []):
                if item.get("execution_id") == execution_id:
                    approval = approval_broker_service.get_request(item["approval_request_id"])
                    if not approval:
                        item["status"] = "approval_missing"
                    else:
                        approval_status = approval.get("status")
                        if approval_status == "approved":
                            item["status"] = "approved_to_continue"
                            item["result"] = "ready_to_continue"
                        elif approval_status == "rejected":
                            item["status"] = "rejected"
                            item["result"] = "blocked_by_user"
                        elif approval_status == "needs_changes":
                            item["status"] = "needs_changes"
                            item["result"] = "changes_requested"
                        else:
                            item["status"] = "waiting_for_approval"
                    item["updated_at"] = self._now()
                    self._write_store(store)
                    return item
        raise ValueError("execution_not_found")


approval_gated_execution_service = ApprovalGatedExecutionService()
