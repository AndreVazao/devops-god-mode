import json
import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

from app.services.local_code_patch_service import local_code_patch_service


class PatchApplyPreviewService:
    def __init__(self, storage_path: str = "data/patch_apply_preview_store.json") -> None:
        self.storage_path = Path(storage_path)
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        self._ensure_store()

    def _ensure_store(self) -> None:
        if not self.storage_path.exists():
            self._write_store({"previews": []})

    def _read_store(self) -> Dict[str, Any]:
        if not self.storage_path.exists():
            return {"previews": []}
        return json.loads(self.storage_path.read_text(encoding="utf-8"))

    def _write_store(self, payload: Dict[str, Any]) -> None:
        self.storage_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def _build_before_preview(self, patch: Dict[str, Any]) -> str:
        return f"instruction: {patch.get('instruction', '')}"

    def _build_after_preview(self, patch: Dict[str, Any]) -> str:
        strategy = patch.get("patch_strategy", "unknown")
        target_path = patch.get("target_path", "unknown")
        return f"strategy={strategy} target={target_path}"

    def create_preview(self, patch_id: str, apply_mode: str = "simulate_only") -> Dict[str, Any]:
        patch = local_code_patch_service.get_patch(patch_id)
        if not patch:
            raise ValueError("patch_not_found")

        if patch.get("approval_required") and patch.get("status") != "ready_to_apply":
            raise PermissionError("patch_not_ready_to_preview")

        preview = {
            "preview_id": f"preview_{uuid.uuid4().hex[:12]}",
            "patch_id": patch_id,
            "apply_mode": apply_mode,
            "before_preview": self._build_before_preview(patch),
            "after_preview": self._build_after_preview(patch),
            "diff_summary": [
                f"strategy: {patch.get('patch_strategy', 'unknown')}",
                f"target: {patch.get('target_path', 'unknown')}",
                f"risk: {patch.get('risk_level', 'unknown')}",
            ],
            "validation_status": "pending",
            "apply_status": "preview_ready",
            "created_at": self._now(),
            "updated_at": self._now(),
        }

        with self._lock:
            store = self._read_store()
            store.setdefault("previews", []).append(preview)
            self._write_store(store)

        return preview

    def list_previews(self) -> Dict[str, Any]:
        with self._lock:
            store = self._read_store()
        previews = store.get("previews", [])
        return {"ok": True, "mode": "patch_apply_preview_queue", "count": len(previews), "previews": previews}

    def get_preview(self, preview_id: str) -> Optional[Dict[str, Any]]:
        with self._lock:
            store = self._read_store()
        for item in store.get("previews", []):
            if item.get("preview_id") == preview_id:
                return item
        return None

    def mark_simulated_apply(self, preview_id: str, validation_status: str = "pending") -> Dict[str, Any]:
        with self._lock:
            store = self._read_store()
            for item in store.get("previews", []):
                if item.get("preview_id") == preview_id:
                    item["apply_status"] = "applied_locally_pending_validation"
                    item["validation_status"] = validation_status
                    item["updated_at"] = self._now()
                    self._write_store(store)
                    return item
        raise ValueError("preview_not_found")

    def mark_validated(self, preview_id: str) -> Dict[str, Any]:
        with self._lock:
            store = self._read_store()
            for item in store.get("previews", []):
                if item.get("preview_id") == preview_id:
                    item["apply_status"] = "applied_and_validated"
                    item["validation_status"] = "passed"
                    item["updated_at"] = self._now()
                    self._write_store(store)
                    return item
        raise ValueError("preview_not_found")


patch_apply_preview_service = PatchApplyPreviewService()
