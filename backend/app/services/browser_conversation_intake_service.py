import json
import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from app.services.conversation_organization_service import conversation_organization_service


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
        self.storage_path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def _navigation_steps_for(self, session_id: str, alias_hint: str) -> List[Dict[str, Any]]:
        return [
            {
                "step_id": f"{session_id}_open_chat",
                "session_id": session_id,
                "action_type": "open_chat",
                "target_hint": alias_hint,
                "step_status": "pending",
                "completion_note": "",
            },
            {
                "step_id": f"{session_id}_scroll_up_history",
                "session_id": session_id,
                "action_type": "scroll_up",
                "target_hint": "capture_older_messages_and_code_blocks",
                "step_status": "pending",
                "completion_note": "",
            },
            {
                "step_id": f"{session_id}_mark_code_regions",
                "session_id": session_id,
                "action_type": "capture_code",
                "target_hint": "extract_code_blocks_and_structured_snippets",
                "step_status": "pending",
                "completion_note": "",
            },
        ]

    def create_session(
        self,
        source_type: str,
        source_url: str,
        conversation_title: str,
        warnings: Optional[List[str]] = None,
        project_hint: Optional[str] = None,
        intake_goal: str = "capture_code_and_context",
        alias_hint: Optional[str] = None,
    ) -> Dict[str, Any]:
        session_id = f"intake_{uuid.uuid4().hex[:12]}"
        payload = {
            "session_id": session_id,
            "source_type": source_type,
            "source_url": source_url,
            "conversation_title": conversation_title,
            "project_hint": project_hint,
            "intake_goal": intake_goal,
            "capture_status": "queued",
            "scroll_steps": 0,
            "snippets": [],
            "code_blocks": [],
            "warnings": warnings or [],
            "navigation_steps": self._navigation_steps_for(
                session_id, alias_hint or conversation_title
            ),
            "created_at": self._now(),
            "updated_at": self._now(),
        }
        with self._lock:
            store = self._read_store()
            store.setdefault("sessions", []).append(payload)
            self._write_store(store)
        return payload

    def _session_summary(self, item: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "session_id": item["session_id"],
            "source_type": item["source_type"],
            "source_url": item["source_url"],
            "conversation_title": item["conversation_title"],
            "project_hint": item.get("project_hint"),
            "intake_goal": item.get("intake_goal"),
            "capture_status": item.get("capture_status"),
            "scroll_steps": int(item.get("scroll_steps", 0)),
            "snippets_count": len(item.get("snippets", [])),
            "code_blocks_count": len(item.get("code_blocks", [])),
            "warnings": item.get("warnings", []),
            "updated_at": item.get("updated_at"),
        }

    def list_sessions(self) -> Dict[str, Any]:
        with self._lock:
            store = self._read_store()
        sessions = [self._session_summary(item) for item in store.get("sessions", [])]
        return {
            "ok": True,
            "mode": "browser_conversation_intake_queue",
            "count": len(sessions),
            "sessions": sessions,
        }

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
                    item["scroll_steps"] = int(item.get("scroll_steps", 0)) + max(
                        increment_scroll_steps, 0
                    )
                    item.setdefault("snippets", []).extend(snippets or [])
                    item.setdefault("code_blocks", []).extend(code_blocks or [])
                    item.setdefault("warnings", []).extend(warnings or [])
                    item["capture_status"] = capture_status
                    for step in item.get("navigation_steps", []):
                        if step["action_type"] == "open_chat":
                            step["step_status"] = "completed"
                            step["completion_note"] = "chat opened for intake"
                        elif step["action_type"] == "scroll_up" and item["scroll_steps"] > 0:
                            step["step_status"] = "completed"
                            step["completion_note"] = f"scroll_steps={item['scroll_steps']}"
                        elif step["action_type"] == "capture_code" and item.get("code_blocks"):
                            step["step_status"] = "completed"
                            step["completion_note"] = (
                                f"code_blocks={len(item.get('code_blocks', []))}"
                            )
                    item["updated_at"] = self._now()
                    self._write_store(store)
                    return item
        raise ValueError("session_not_found")

    def get_navigation_plan(self, session_id: str) -> Dict[str, Any]:
        session = self.get_session(session_id)
        if not session:
            raise ValueError("session_not_found")
        return {
            "ok": True,
            "mode": "browser_intake_navigation_plan",
            "session_id": session_id,
            "navigation_steps": session.get("navigation_steps", []),
        }

    def get_capture_progress(self, session_id: str) -> Dict[str, Any]:
        session = self.get_session(session_id)
        if not session:
            raise ValueError("session_not_found")
        summary = self._session_summary(session)
        return {
            "ok": True,
            "mode": "browser_intake_capture_progress",
            "session_id": session_id,
            "progress": summary,
        }

    def seed_from_conversation_focus(self) -> Dict[str, Any]:
        next_focus = conversation_organization_service.get_next_focus()["next_focus"]
        if not next_focus or not next_focus.get("conversation_id"):
            return {
                "ok": True,
                "mode": "browser_intake_seeded_session",
                "seeded": False,
                "reason": "no_focus_available",
            }

        session = self.create_session(
            source_type="browser_ai_conversation",
            source_url=f"https://chatgpt.com/c/{next_focus['conversation_id']}",
            conversation_title=next_focus["conversation_id"],
            project_hint=next_focus.get("project_key"),
            intake_goal=next_focus.get("recommended_action") or "capture_code_and_context",
            alias_hint=next_focus["conversation_id"],
            warnings=[next_focus.get("focus_reason")] if next_focus.get("focus_reason") else [],
        )
        return {
            "ok": True,
            "mode": "browser_intake_seeded_session",
            "seeded": True,
            "session": self._session_summary(session),
        }

    def get_priority_queue(self) -> Dict[str, Any]:
        with self._lock:
            store = self._read_store()
        sessions = [self._session_summary(item) for item in store.get("sessions", [])]
        ordered = sorted(
            sessions,
            key=lambda item: (
                item["capture_status"] not in {"queued", "capturing"},
                item["scroll_steps"],
                -item["code_blocks_count"],
            ),
        )
        return {
            "ok": True,
            "mode": "browser_intake_priority_queue",
            "count": len(ordered),
            "sessions": ordered,
        }

    def get_next_session(self) -> Dict[str, Any]:
        sessions = self.get_priority_queue()["sessions"]
        return {
            "ok": True,
            "mode": "browser_intake_next_session",
            "next_session": sessions[0] if sessions else None,
        }


browser_conversation_intake_service = BrowserConversationIntakeService()
