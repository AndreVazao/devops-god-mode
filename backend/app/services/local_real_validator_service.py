import json
import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

from app.services.real_local_write_service import real_local_write_service


class LocalRealValidatorService:
    def __init__(self, storage_path: str = "data/local_real_validator_store.json") -> None:
        self.storage_path = Path(storage_path)
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        self._ensure_store()

    def _ensure_store(self) -> None:
        if not self.storage_path.exists():
            self._write_store({"validator_runs": []})

    def _read_store(self) -> Dict[str, Any]:
        if not self.storage_path.exists():
            return {"validator_runs": []}
        return json.loads(self.storage_path.read_text(encoding="utf-8"))

    def _write_store(self, payload: Dict[str, Any]) -> None:
        self.storage_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def create_validator_run(
        self,
        write_run_id: str,
        validator_mode: str = "post_write_real_checks",
        checks: Optional[list[str]] = None,
    ) -> Dict[str, Any]:
        write_run = real_local_write_service.get_write_run(write_run_id)
        if not write_run:
            raise ValueError("write_run_not_found")

        payload = {
            "validator_run_id": f"validator_{uuid.uuid4().hex[:12]}",
            "write_run_id": write_run_id,
            "validator_mode": validator_mode,
            "checks": checks or [
                "target_exists",
                "backup_exists",
                "content_non_empty",
                "preview_excerpt_match",
            ],
            "expected_preview_excerpt": (write_run.get("preview_after") or "")[:120],
            "observed_file_excerpt": "",
            "checks_result": {},
            "final_status": "validators_pending",
            "created_at": self._now(),
            "updated_at": self._now(),
        }

        with self._lock:
            store = self._read_store()
            store.setdefault("validator_runs", []).append(payload)
            self._write_store(store)

        return payload

    def list_validator_runs(self) -> Dict[str, Any]:
        with self._lock:
            store = self._read_store()
        runs = store.get("validator_runs", [])
        return {"ok": True, "mode": "local_real_validator_queue", "count": len(runs), "validator_runs": runs}

    def get_validator_run(self, validator_run_id: str) -> Optional[Dict[str, Any]]:
        with self._lock:
            store = self._read_store()
        for item in store.get("validator_runs", []):
            if item.get("validator_run_id") == validator_run_id:
                return item
        return None

    def record_observation(
        self,
        validator_run_id: str,
        observed_file_excerpt: str,
        checks_result: Dict[str, str],
    ) -> Dict[str, Any]:
        with self._lock:
            store = self._read_store()
            for item in store.get("validator_runs", []):
                if item.get("validator_run_id") == validator_run_id:
                    item["observed_file_excerpt"] = observed_file_excerpt[:120]
                    item["checks_result"] = checks_result
                    item["updated_at"] = self._now()
                    self._write_store(store)
                    return item
        raise ValueError("validator_run_not_found")

    def finalize_validator_run(self, validator_run_id: str) -> Dict[str, Any]:
        with self._lock:
            store = self._read_store()
            for item in store.get("validator_runs", []):
                if item.get("validator_run_id") == validator_run_id:
                    checks_result = item.get("checks_result", {})
                    if checks_result and all(value == "passed" for value in checks_result.values()):
                        item["final_status"] = "validators_passed"
                    else:
                        item["final_status"] = "validators_failed"
                    item["updated_at"] = self._now()
                    self._write_store(store)
                    return item
        raise ValueError("validator_run_not_found")


local_real_validator_service = LocalRealValidatorService()
