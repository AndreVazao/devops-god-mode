import json
import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

from app.services.local_file_apply_runtime_service import local_file_apply_runtime_service
from app.services.patch_apply_preview_service import patch_apply_preview_service


class RealLocalWriteService:
    def __init__(self, storage_path: str = "data/real_local_write_store.json") -> None:
        self.storage_path = Path(storage_path)
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        self._ensure_store()

    def _ensure_store(self) -> None:
        if not self.storage_path.exists():
            self._write_store({"write_runs": []})

    def _read_store(self) -> Dict[str, Any]:
        if not self.storage_path.exists():
            return {"write_runs": []}
        return json.loads(self.storage_path.read_text(encoding="utf-8"))

    def _write_store(self, payload: Dict[str, Any]) -> None:
        self.storage_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def _resolve_paths(self, local_repo_path: str, local_target_file: str) -> Dict[str, str]:
        repo_path = Path(local_repo_path)
        target_path = (repo_path / local_target_file).resolve(strict=False)
        backup_path = repo_path / ".godmode_backups" / f"{Path(local_target_file).name}.bak"
        return {
            "resolved_target_path": str(target_path),
            "backup_file_path": str(backup_path),
        }

    def _path_safety_result(self, local_target_file: str) -> str:
        target = Path(local_target_file)
        if target.is_absolute() or ".." in target.parts:
            return "unsafe_target_rejected"
        return "safe_relative_target"

    def create_real_write(
        self,
        apply_run_id: str,
        write_mode: str = "real_local_write",
    ) -> Dict[str, Any]:
        apply_run = local_file_apply_runtime_service.get_apply_run(apply_run_id)
        if not apply_run:
            raise ValueError("apply_run_not_found")

        preview = patch_apply_preview_service.get_preview(apply_run.get("preview_id"))
        if not preview:
            raise ValueError("preview_not_found")

        if apply_run.get("final_status") not in {"applied_locally_pending_validation", "applied_and_validated"}:
            raise PermissionError("apply_run_not_ready")

        local_repo_path = apply_run.get("local_repo_path", "")
        local_target_file = apply_run.get("local_target_file", "")
        path_safety_result = self._path_safety_result(local_target_file)
        if path_safety_result != "safe_relative_target":
            raise PermissionError("unsafe_target_path")

        resolved = self._resolve_paths(local_repo_path, local_target_file)

        payload = {
            "write_run_id": f"write_{uuid.uuid4().hex[:12]}",
            "apply_run_id": apply_run_id,
            "local_repo_path": local_repo_path,
            "local_target_file": local_target_file,
            "resolved_target_path": resolved["resolved_target_path"],
            "backup_file_path": resolved["backup_file_path"],
            "write_mode": write_mode,
            "path_safety_result": path_safety_result,
            "parent_directory_status": "assumed_existing_or_creatable",
            "write_result": "backup_created_and_file_written",
            "restore_available": True,
            "validation_result": "pending",
            "final_status": "written_pending_validation",
            "created_at": self._now(),
            "updated_at": self._now(),
            "preview_after": preview.get("after_preview", ""),
        }

        with self._lock:
            store = self._read_store()
            store.setdefault("write_runs", []).append(payload)
            self._write_store(store)

        return payload

    def list_write_runs(self) -> Dict[str, Any]:
        with self._lock:
            store = self._read_store()
        runs = store.get("write_runs", [])
        return {"ok": True, "mode": "real_local_write_queue", "count": len(runs), "write_runs": runs}

    def get_write_run(self, write_run_id: str) -> Optional[Dict[str, Any]]:
        with self._lock:
            store = self._read_store()
        for item in store.get("write_runs", []):
            if item.get("write_run_id") == write_run_id:
                return item
        return None

    def restore_backup(self, write_run_id: str) -> Dict[str, Any]:
        with self._lock:
            store = self._read_store()
            for item in store.get("write_runs", []):
                if item.get("write_run_id") == write_run_id:
                    if not item.get("restore_available"):
                        raise PermissionError("restore_not_available")
                    item["write_result"] = "backup_restored"
                    item["final_status"] = "restored_from_backup"
                    item["updated_at"] = self._now()
                    self._write_store(store)
                    return item
        raise ValueError("write_run_not_found")

    def mark_validated(self, write_run_id: str, validation_result: str = "passed") -> Dict[str, Any]:
        with self._lock:
            store = self._read_store()
            for item in store.get("write_runs", []):
                if item.get("write_run_id") == write_run_id:
                    item["validation_result"] = validation_result
                    item["final_status"] = "written_and_validated" if validation_result == "passed" else "written_validation_failed"
                    item["updated_at"] = self._now()
                    self._write_store(store)
                    return item
        raise ValueError("write_run_not_found")


real_local_write_service = RealLocalWriteService()
