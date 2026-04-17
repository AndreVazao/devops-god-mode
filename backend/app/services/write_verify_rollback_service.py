import json
import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from app.services.real_local_write_service import real_local_write_service


class WriteVerifyRollbackService:
    def __init__(self, storage_path: str = "data/write_verify_rollback_store.json") -> None:
        self.storage_path = Path(storage_path)
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        self._ensure_store()

    def _ensure_store(self) -> None:
        if not self.storage_path.exists():
            self._write_store({"verify_runs": []})

    def _read_store(self) -> Dict[str, Any]:
        if not self.storage_path.exists():
            return {"verify_runs": []}
        return json.loads(self.storage_path.read_text(encoding="utf-8"))

    def _write_store(self, payload: Dict[str, Any]) -> None:
        self.storage_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def create_verify_run(
        self,
        write_run_id: str,
        verification_mode: str = "post_write_local_checks",
        verification_checks: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        write_run = real_local_write_service.get_write_run(write_run_id)
        if not write_run:
            raise ValueError("write_run_not_found")

        payload = {
            "verify_run_id": f"verify_{uuid.uuid4().hex[:12]}",
            "write_run_id": write_run_id,
            "verification_mode": verification_mode,
            "verification_checks": verification_checks or [
                "target_file_exists",
                "backup_exists",
                "content_non_empty",
            ],
            "verification_result": "pending",
            "rollback_triggered": False,
            "final_status": "verification_pending",
            "created_at": self._now(),
            "updated_at": self._now(),
        }

        with self._lock:
            store = self._read_store()
            store.setdefault("verify_runs", []).append(payload)
            self._write_store(store)

        return payload

    def list_verify_runs(self) -> Dict[str, Any]:
        with self._lock:
            store = self._read_store()
        runs = store.get("verify_runs", [])
        return {"ok": True, "mode": "write_verify_rollback_queue", "count": len(runs), "verify_runs": runs}

    def get_verify_run(self, verify_run_id: str) -> Optional[Dict[str, Any]]:
        with self._lock:
            store = self._read_store()
        for item in store.get("verify_runs", []):
            if item.get("verify_run_id") == verify_run_id:
                return item
        return None

    def mark_verification_passed(self, verify_run_id: str) -> Dict[str, Any]:
        with self._lock:
            store = self._read_store()
            for item in store.get("verify_runs", []):
                if item.get("verify_run_id") == verify_run_id:
                    item["verification_result"] = "passed"
                    item["final_status"] = "verified_ok"
                    item["updated_at"] = self._now()
                    self._write_store(store)
                    return item
        raise ValueError("verify_run_not_found")

    def mark_verification_failed(self, verify_run_id: str) -> Dict[str, Any]:
        with self._lock:
            store = self._read_store()
            for item in store.get("verify_runs", []):
                if item.get("verify_run_id") == verify_run_id:
                    item["verification_result"] = "failed"
                    item["final_status"] = "verification_failed"
                    item["updated_at"] = self._now()
                    self._write_store(store)
                    return item
        raise ValueError("verify_run_not_found")

    def execute_rollback(self, verify_run_id: str) -> Dict[str, Any]:
        with self._lock:
            store = self._read_store()
            for item in store.get("verify_runs", []):
                if item.get("verify_run_id") == verify_run_id:
                    write_run = real_local_write_service.get_write_run(item.get("write_run_id"))
                    if not write_run:
                        raise ValueError("write_run_not_found")
                    if write_run.get("final_status") == "restored_from_backup":
                        raise PermissionError("rollback_already_executed")
                    if not write_run.get("restore_available"):
                        raise PermissionError("rollback_not_available")
                    real_local_write_service.restore_backup(item.get("write_run_id"))
                    item["rollback_triggered"] = True
                    item["final_status"] = "rolled_back_after_failed_verification"
                    item["updated_at"] = self._now()
                    self._write_store(store)
                    return item
        raise ValueError("verify_run_not_found")


write_verify_rollback_service = WriteVerifyRollbackService()
