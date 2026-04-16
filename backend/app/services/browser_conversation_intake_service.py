import json
import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


class BrowserConversationIntakeService:
    def __init__(self, storage_path: str = "data/browser_conversation_intake_store.json") -> None:
        self.storage_path = Path(storage_path)
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        self._ensure_store()

    def _ensure_store(self) -> None:
        if not self.storage_path.exists():
            self._write_store({"sessions": []})

    def _read_store(self) -> Dict[str, Any]:
        if not self.storage_path.exists():
            return {"sessions": []}
        return json.loads(self.storage_path.read_text(encoding="utf-8"))

    def _write_store(self, payload: Dict[str, Any]) -> None:
        self.storage_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def create_session(
        self,
        source_type: str,
        source_url: str,
        conversation_title: str,
        warnings: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        payload = {
            "session_id": f"intake_{uuid.uuid4().hex[:12]}",
            "source_type": source_type,
            "source_url": source_url,
            "conversation_title": conversation_title,
            "capture_status": "created",
            "scroll_steps": 0,
            "snippets": [],
            "code_blocks": [],
            "warnings": warnings or [],
            "created_at": self._now(),
            "updated_at": self._now(),
        }
        with self._lock:
            store = self._read_store()
            store.setdefault("sessions", []).append(payload)
            self._write_store(store)
        return payload

    def list_sessions(self) -> Dict[str, Any]:
        with self._lock:
            store = self._read_store()
        sessions = store.get("sessions", [])
        return {"ok": True, "mode": "browser_conversation_intake_queue", "count": len(sessions), "sessions": sessions}

    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        with self._lock:
            store = self._read_store()
        for item in store.get("sessions", []):
            if item.get("session_id") == session_id:
                return item
        return None

    def append_capture(
        self,
        session_id: str,
        snippets: Optional[List[Dict[str, Any]]] = None,
        code_blocks: Optional[List[Dict[str, Any]]] = None,
        warnings: Optional[List[str]] = None,
        increment_scroll_steps: int = 1,
        capture_status: str = "capturing",
    ) -> Dict[str, Any]:
        with self._lock:
            store = self._read_store()
            for item in store.get("sessions", []):
                if item.get("session_id") == session_id:
                    item["scroll_steps"] = int(item.get("scroll_steps", 0)) + max(increment_scroll_steps, 0)
                    item.setdefault("snippets", []).extend(snippets or [])
                    item.setdefault("code_blocks", []).extend(code_blocks or [])
                    item.setdefault("warnings", []).extend(warnings or [])
                    item["capture_status"] = capture_status
                    item["updated_at"] = self._now()
                    self._write_store(store)
                    return item
        raise ValueError("session_not_found")


browser_conversation_intake_service = BrowserConversationIntakeService()
