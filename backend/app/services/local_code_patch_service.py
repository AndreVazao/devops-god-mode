import json
import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from app.services.approval_broker_service import approval_broker_service


class LocalCodePatchService:
    def __init__(self, storage_path: str = "data/local_code_patch_store.json") -> None:
        self.storage_path = Path(storage_path)
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        self._ensure_store()

    def _ensure_store(self) -> None:
        if not self.storage_path.exists():
            self._write_store({"patches": []})

    def _read_store(self) -> Dict[str, Any]:
        if not self.storage_path.exists():
            return {"patches": []}
        return json.loads(self.storage_path.read_text(encoding="utf-8"))

    def _write_store(self, payload: Dict[str, Any]) -> None:
        self.storage_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def _risk_to_approval(self, risk_level: str) -> bool:
        return risk_level.lower() in {"medium", "high", "critical"}

    def create_patch(
        self,
        repo_full_name: str,
        target_path: str,
        instruction: str,
        patch_strategy: str,
        risk_level: str,
        proposed_changes: Optional[List[Dict[str, Any]]] = None,
        validation_plan: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        approval_required = self._risk_to_approval(risk_level)
        approval_request_id = None
        status = "ready_to_apply"

        if approval_required:
            approval = approval_broker_service.create_request(
                source="local_code_patch_engine",
                action_type="apply_local_patch",
                risk_level=risk_level,
                summary=f"Patch local pronto para {target_path}",
                details={
                    "repo_full_name": repo_full_name,
                    "target_path": target_path,
                    "instruction": instruction,
                    "patch_strategy": patch_strategy,
                },
                requires_manual_confirmation=True,
                suggested_response="ALTERA",
                allowed_responses=["OK", "ALTERA", "REJEITA"],
            )
            approval_request_id = approval["request_id"]
            status = "waiting_for_approval"

        payload = {
            "patch_id": f"patch_{uuid.uuid4().hex[:12]}",
            "repo_full_name": repo_full_name,
            "target_path": target_path,
            "instruction": instruction,
            "patch_strategy": patch_strategy,
            "risk_level": risk_level,
            "approval_required": approval_required,
            "status": status,
            "approval_request_id": approval_request_id,
            "proposed_changes": proposed_changes or [],
            "validation_plan": validation_plan or [],
            "created_at": self._now(),
            "updated_at": self._now(),
        }

        with self._lock:
            store = self._read_store()
            store.setdefault("patches", []).append(payload)
            self._write_store(store)

        return payload

    def list_patches(self) -> Dict[str, Any]:
        with self._lock:
            store = self._read_store()
        patches = store.get("patches", [])
        return {"ok": True, "mode": "local_code_patch_queue", "count": len(patches), "patches": patches}

    def get_patch(self, patch_id: str) -> Optional[Dict[str, Any]]:
        with self._lock:
            store = self._read_store()
        for item in store.get("patches", []):
            if item.get("patch_id") == patch_id:
                return item
        return None

    def sync_with_approval(self, patch_id: str) -> Dict[str, Any]:
        with self._lock:
            store = self._read_store()
            for item in store.get("patches", []):
                if item.get("patch_id") == patch_id:
                    if not item.get("approval_required"):
                        item["status"] = "ready_to_apply"
                        item["updated_at"] = self._now()
                        self._write_store(store)
                        return item

                    approval = approval_broker_service.get_request(item.get("approval_request_id"))
                    if not approval:
                        item["status"] = "approval_missing"
                    else:
                        approval_status = approval.get("status")
                        if approval_status == "approved":
                            item["status"] = "ready_to_apply"
                        elif approval_status == "rejected":
                            item["status"] = "rejected"
                        elif approval_status == "needs_changes":
                            item["status"] = "needs_changes"
                        else:
                            item["status"] = "waiting_for_approval"
                    item["updated_at"] = self._now()
                    self._write_store(store)
                    return item

        raise ValueError("patch_not_found")


local_code_patch_service = LocalCodePatchService()
