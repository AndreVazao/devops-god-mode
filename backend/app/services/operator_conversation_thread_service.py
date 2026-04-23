from __future__ import annotations

import json
from datetime import datetime, UTC
from pathlib import Path
from typing import Any, Dict, List


class OperatorConversationThreadService:
    def __init__(self, store_path: str = "data/operator_conversation_threads.json") -> None:
        self.store_path = Path(store_path)
        self.store_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.store_path.exists():
            self.store_path.write_text(json.dumps({"threads": []}, ensure_ascii=False, indent=2), encoding="utf-8")

    def _read_store(self) -> Dict[str, Any]:
        return json.loads(self.store_path.read_text(encoding="utf-8"))

    def _write_store(self, payload: Dict[str, Any]) -> None:
        self.store_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    def get_status(self) -> Dict[str, Any]:
        store = self._read_store()
        return {
            "ok": True,
            "mode": "operator_conversation_thread_status",
            "store_path": str(self.store_path),
            "thread_count": len(store.get("threads", [])),
            "status": "operator_conversation_thread_ready",
        }

    def open_thread(self, tenant_id: str, conversation_title: str, channel_mode: str = "mobile_chat") -> Dict[str, Any]:
        store = self._read_store()
        thread_id = f"thread-{len(store.get('threads', [])) + 1:05d}"
        thread = {
            "thread_id": thread_id,
            "tenant_id": tenant_id,
            "conversation_title": conversation_title,
            "channel_mode": channel_mode,
            "messages": [],
            "latest_summary": "",
            "suggested_next_steps": [],
        }
        threads = store.get("threads", [])
        threads.append(thread)
        store["threads"] = threads
        self._write_store(store)
        return {
            "ok": True,
            "mode": "operator_conversation_thread_open_result",
            "open_status": "thread_opened",
            "thread": thread,
        }

    def append_message(
        self,
        thread_id: str,
        role: str,
        content: str,
        operational_state: str = "active",
        suggested_next_steps: List[str] | None = None,
    ) -> Dict[str, Any]:
        store = self._read_store()
        threads = store.get("threads", [])
        thread = next((item for item in threads if item.get("thread_id") == thread_id), None)
        if thread is None:
            return {
                "ok": False,
                "mode": "operator_conversation_thread_append_result",
                "append_status": "thread_not_found",
                "thread_id": thread_id,
            }
        message = {
            "role": role,
            "content": content,
            "operational_state": operational_state,
            "created_at": datetime.now(UTC).isoformat(),
        }
        thread.setdefault("messages", []).append(message)
        thread["latest_summary"] = content[:280]
        thread["suggested_next_steps"] = suggested_next_steps or []
        self._write_store(store)
        return {
            "ok": True,
            "mode": "operator_conversation_thread_append_result",
            "append_status": "message_appended",
            "thread_id": thread_id,
            "message_count": len(thread.get("messages", [])),
            "latest_summary": thread.get("latest_summary"),
            "suggested_next_steps": thread.get("suggested_next_steps", []),
        }

    def get_thread(self, thread_id: str) -> Dict[str, Any]:
        store = self._read_store()
        thread = next((item for item in store.get("threads", []) if item.get("thread_id") == thread_id), None)
        if thread is None:
            return {
                "ok": False,
                "mode": "operator_conversation_thread_get_result",
                "get_status": "thread_not_found",
                "thread_id": thread_id,
            }
        return {
            "ok": True,
            "mode": "operator_conversation_thread_get_result",
            "get_status": "thread_found",
            "thread": thread,
        }

    def list_threads(self, tenant_id: str | None = None) -> Dict[str, Any]:
        store = self._read_store()
        threads = store.get("threads", [])
        if tenant_id:
            threads = [item for item in threads if item.get("tenant_id") == tenant_id]
        return {
            "ok": True,
            "mode": "operator_conversation_thread_list_result",
            "thread_count": len(threads),
            "threads": threads,
        }

    def get_package(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "mode": "operator_conversation_thread_package",
            "package": {
                "status": self.get_status(),
                "package_status": "operator_conversation_thread_ready",
            },
        }


operator_conversation_thread_service = OperatorConversationThreadService()
