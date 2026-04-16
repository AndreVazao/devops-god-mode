import json
import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from app.services.approval_broker_service import approval_broker_service


class ConversationRepoReconstructionService:
    def __init__(self, storage_path: str = "data/conversation_repo_reconstruction_store.json") -> None:
        self.storage_path = Path(storage_path)
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        self._ensure_store()

    def _ensure_store(self) -> None:
        if not self.storage_path.exists():
            self._write_store({"reconstructions": []})

    def _read_store(self) -> Dict[str, Any]:
        if not self.storage_path.exists():
            return {"reconstructions": []}
        return json.loads(self.storage_path.read_text(encoding="utf-8"))

    def _write_store(self, payload: Dict[str, Any]) -> None:
        self.storage_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def create_proposal(
        self,
        source_type: str,
        source_label: str,
        messages_scanned: int,
        code_blocks_found: int,
        proposed_repo_name: str,
        proposed_tree: List[str],
        risks: Optional[List[str]] = None,
        notes: Optional[str] = None,
    ) -> Dict[str, Any]:
        reconstruction_id = f"recon_{uuid.uuid4().hex[:12]}"
        approval = approval_broker_service.create_request(
            source="conversation_repo_reconstruction",
            action_type="reconstruction_repo_proposal",
            risk_level="medium",
            summary=f"Reconstrução pronta para {proposed_repo_name}",
            details={
                "source_type": source_type,
                "source_label": source_label,
                "messages_scanned": messages_scanned,
                "code_blocks_found": code_blocks_found,
                "proposed_repo_name": proposed_repo_name,
                "proposed_tree": proposed_tree,
                "notes": notes or "",
            },
            requires_manual_confirmation=True,
            suggested_response="ALTERA",
            allowed_responses=["OK", "ALTERA", "REJEITA"],
        )
        payload = {
            "reconstruction_id": reconstruction_id,
            "source_type": source_type,
            "source_label": source_label,
            "status": "proposal_ready",
            "messages_scanned": messages_scanned,
            "code_blocks_found": code_blocks_found,
            "proposed_repo": {
                "name": proposed_repo_name,
                "tree": proposed_tree,
            },
            "risks": risks or [],
            "approval_required": True,
            "approval_request_id": approval["request_id"],
            "notes": notes or "",
            "created_at": self._now(),
            "updated_at": self._now(),
        }
        with self._lock:
            store = self._read_store()
            store.setdefault("reconstructions", []).append(payload)
            self._write_store(store)
        return payload

    def list_reconstructions(self) -> Dict[str, Any]:
        with self._lock:
            store = self._read_store()
        reconstructions = store.get("reconstructions", [])
        return {"ok": True, "mode": "conversation_repo_reconstruction_queue", "count": len(reconstructions), "reconstructions": reconstructions}

    def get_reconstruction(self, reconstruction_id: str) -> Optional[Dict[str, Any]]:
        with self._lock:
            store = self._read_store()
        for item in store.get("reconstructions", []):
            if item.get("reconstruction_id") == reconstruction_id:
                return item
        return None

    def sync_with_approval(self, reconstruction_id: str) -> Dict[str, Any]:
        with self._lock:
            store = self._read_store()
            for item in store.get("reconstructions", []):
                if item.get("reconstruction_id") == reconstruction_id:
                    approval = approval_broker_service.get_request(item["approval_request_id"])
                    if not approval:
                        item["status"] = "approval_missing"
                    else:
                        approval_status = approval.get("status")
                        if approval_status == "approved":
                            item["status"] = "approved_to_build_repo"
                        elif approval_status == "rejected":
                            item["status"] = "rejected"
                        elif approval_status == "needs_changes":
                            item["status"] = "needs_changes"
                        else:
                            item["status"] = "proposal_ready"
                    item["updated_at"] = self._now()
                    self._write_store(store)
                    return item
        raise ValueError("reconstruction_not_found")


conversation_repo_reconstruction_service = ConversationRepoReconstructionService()
