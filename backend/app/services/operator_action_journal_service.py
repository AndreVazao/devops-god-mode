from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Dict, List


class OperatorActionJournalService:
    def __init__(self, store_path: str = "data/operator_action_journal.json") -> None:
        self.store_path = Path(store_path)
        self.store_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.store_path.exists():
            self.store_path.write_text(json.dumps({"entries": []}, ensure_ascii=False, indent=2), encoding="utf-8")

    def _read_store(self) -> Dict[str, Any]:
        return json.loads(self.store_path.read_text(encoding="utf-8"))

    def _write_store(self, payload: Dict[str, Any]) -> None:
        self.store_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    def get_status(self) -> Dict[str, Any]:
        store = self._read_store()
        return {
            "ok": True,
            "mode": "operator_action_journal_status",
            "store_path": str(self.store_path),
            "entry_count": len(store.get("entries", [])),
            "status": "operator_action_journal_ready",
        }

    def log_event(
        self,
        tenant_id: str,
        thread_id: str,
        event_type: str,
        summary: str,
        outcome: str = "recorded",
        details: Dict[str, Any] | None = None,
        origin: str = "operator_chat_sync_frontend",
    ) -> Dict[str, Any]:
        store = self._read_store()
        entries = store.get("entries", [])
        entry_id = f"journal-{len(entries) + 1:05d}"
        entry = {
            "entry_id": entry_id,
            "tenant_id": tenant_id,
            "thread_id": thread_id,
            "event_type": event_type,
            "summary": summary,
            "outcome": outcome,
            "details": details or {},
            "origin": origin,
            "created_at": datetime.now(UTC).isoformat(),
        }
        entries.append(entry)
        store["entries"] = entries
        self._write_store(store)
        return {
            "ok": True,
            "mode": "operator_action_journal_log_result",
            "log_status": "event_logged",
            "entry": entry,
        }

    def list_entries(
        self,
        tenant_id: str | None = None,
        thread_id: str | None = None,
        limit: int = 50,
    ) -> Dict[str, Any]:
        store = self._read_store()
        entries: List[Dict[str, Any]] = store.get("entries", [])
        if tenant_id:
            entries = [item for item in entries if item.get("tenant_id") == tenant_id]
        if thread_id:
            entries = [item for item in entries if item.get("thread_id") == thread_id]
        entries = list(reversed(entries))[:limit]
        return {
            "ok": True,
            "mode": "operator_action_journal_list_result",
            "entry_count": len(entries),
            "entries": entries,
        }

    def get_package(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "mode": "operator_action_journal_package",
            "package": {
                "status": self.get_status(),
                "package_status": "operator_action_journal_ready",
            },
        }


operator_action_journal_service = OperatorActionJournalService()
