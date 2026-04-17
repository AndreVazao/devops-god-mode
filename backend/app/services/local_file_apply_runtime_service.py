import json
import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

from app.services.local_code_patch_service import local_code_patch_service
from app.services.patch_apply_preview_service import patch_apply_preview_service


class LocalFileApplyRuntimeService:
    def __init__(self, storage_path: str = "data/local_file_apply_runtime_store.json") -> None:
        self.storage_path = Path(storage_path)
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        self._ensure_store()

    def _ensure_store(self) -> None:
        if not self.storage_path.exists():
            self._write_store({"apply_runs": []})

    def _read_store(self) -> Dict[str, Any]:
        if not self.storage_path.exists():
            return {"apply_runs": []}
        return json.loads(self.storage_path.read_text(encoding="utf-8"))

    def _write_store(self, payload: Dict[str, Any]) -> None:
        self.storage_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def create_apply_run(
        self,
        patch_id: str,
        preview_id: str,
        local_repo_path: str,
        local_target_file: str,
        execution_mode: str,
    ) -> Dict[str, Any]:
        patch = local_code_patch_service.get_patch(patch_id)
        if not patch:
            raise ValueError("patch_not_found")

        preview = patch_apply_preview_service.get_preview(preview_id)
        if not preview:
            raise ValueError("preview_not_found")

        if preview.get("patch_id") != patch_id:
            raise ValueError("preview_patch_mismatch")

        if patch.get("approval_required") and patch.get("status") != "ready_to_apply":
            raise PermissionError("patch_not_ready_to_apply")

        if preview.get("apply_status") not in {"preview_ready", "applied_locally_pending_validation", "applied_and_validated"}:
            raise PermissionError("preview_not_ready")

        backup_file_path = str(Path(local_repo_path) / ".godmode_backups" / f"{Path(local_target_file).name}.bak")

        payload = {
            "apply_run_id": f"apply_{uuid.uuid4().hex[:12]}",
            "patch_id": patch_id,
            "preview_id": preview_id,
            "local_repo_path": local_repo_path,
            "local_target_file": local_target_file,
            "backup_file_path": backup_file_path,
            "execution_mode": execution_mode,
            "apply_result": "backup_created_and_preview_written",
            "validation_result": "pending",
            "final_status": "applied_locally_pending_validation",
            "created_at": self._now(),
            "updated_at": self._now(),
        }

        with self._lock:
            store = self._read_store()
            store.setdefault("apply_runs", []).append(payload)
            self._write_store(store)

        return payload

    def list_apply_runs(self) -> Dict[str, Any]:
        with self._lock:
            store = self._read_store()
        apply_runs = store.get("apply_runs", [])
        return {"ok": True, "mode": "local_file_apply_runtime_queue", "count": len(apply_runs), "apply_runs": apply_runs}

    def get_apply_run(self, apply_run_id: str) -> Optional[Dict[str, Any]]:
        with self._lock:
            store = self._read_store()
        for item in store.get("apply_runs", []):
            if item.get("apply_run_id") == apply_run_id:
                return item
        return None

    def mark_validated(self, apply_run_id: str, validation_result: str = "passed") -> Dict[str, Any]:
        with self._lock:
            store = self._read_store()
            for item in store.get("apply_runs", []):
                if item.get("apply_run_id") == apply_run_id:
                    item["validation_result"] = validation_result
                    item["final_status"] = "applied_and_validated" if validation_result == "passed" else "validation_failed"
                    item["updated_at"] = self._now()
                    self._write_store(store)
                    return item
        raise ValueError("apply_run_not_found")


local_file_apply_runtime_service = LocalFileApplyRuntimeService()
