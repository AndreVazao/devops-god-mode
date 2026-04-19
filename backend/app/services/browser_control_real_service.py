from typing import Any, Dict, List, Optional

from app.services.browser_conversation_intake_service import (
    browser_conversation_intake_service,
)


class BrowserControlRealService:
    def _actions_for_session(self, session: Dict[str, Any]) -> List[Dict[str, Any]]:
        control_id = f"control_{session['session_id']}"
        target_hint = session.get("conversation_title") or session["session_id"]
        return [
            {
                "action_id": f"{control_id}_open_chat",
                "control_id": control_id,
                "action_type": "open_chat",
                "target_hint": target_hint,
                "requires_confirmation": True,
                "action_status": "pending",
                "completion_note": "",
            },
            {
                "action_id": f"{control_id}_focus_thread",
                "control_id": control_id,
                "action_type": "focus_thread",
                "target_hint": "position_on_target_conversation",
                "requires_confirmation": False,
                "action_status": "pending",
                "completion_note": "",
            },
            {
                "action_id": f"{control_id}_scroll_capture",
                "control_id": control_id,
                "action_type": "scroll_capture",
                "target_hint": session.get("intake_goal") or "capture_code_and_context",
                "requires_confirmation": False,
                "action_status": "pending",
                "completion_note": "",
            },
        ]

    def _controls(self) -> List[Dict[str, Any]]:
        sessions = browser_conversation_intake_service.get_priority_queue()["sessions"]
        controls: List[Dict[str, Any]] = []
        for session in sessions:
            actions = self._actions_for_session(session)
            pending_actions = [action for action in actions if action["action_status"] != "completed"]
            controls.append(
                {
                    "control_id": f"control_{session['session_id']}",
                    "session_id": session["session_id"],
                    "control_mode": "assisted_browser_control",
                    "target_url": session["source_url"],
                    "target_conversation_id": session["conversation_title"],
                    "control_status": "queued" if session["capture_status"] == "queued" else "active",
                    "active_step_id": pending_actions[0]["action_id"] if pending_actions else None,
                    "pending_actions_count": len(pending_actions),
                    "last_action_summary": session.get("updated_at") or "",
                }
            )
        return controls

    def get_controls(self) -> Dict[str, Any]:
        controls = self._controls()
        return {"ok": True, "mode": "browser_control_sessions", "controls": controls}

    def get_actions(self, control_id: str) -> Dict[str, Any]:
        session_id = control_id.removeprefix("control_")
        session = browser_conversation_intake_service.get_session(session_id)
        if not session:
            raise ValueError("control_not_found")
        return {
            "ok": True,
            "mode": "browser_control_actions",
            "control_id": control_id,
            "actions": self._actions_for_session(session),
        }

    def get_next_action(self) -> Dict[str, Any]:
        controls = self._controls()
        next_control = next((control for control in controls if control["pending_actions_count"] > 0), None)
        if not next_control:
            return {"ok": True, "mode": "browser_control_next_action", "next_action": None}
        actions = self.get_actions(next_control["control_id"])["actions"]
        next_action = next((action for action in actions if action["action_status"] == "pending"), None)
        return {"ok": True, "mode": "browser_control_next_action", "next_action": next_action}

    def advance_action(self, control_id: str, action_id: str, completion_note: str = "") -> Dict[str, Any]:
        session_id = control_id.removeprefix("control_")
        session = browser_conversation_intake_service.get_session(session_id)
        if not session:
            raise ValueError("control_not_found")

        if action_id.endswith("_open_chat"):
            updated_session = browser_conversation_intake_service.append_capture(
                session_id=session_id,
                snippets=[],
                code_blocks=[],
                warnings=[],
                increment_scroll_steps=0,
                capture_status="capturing",
            )
        elif action_id.endswith("_focus_thread"):
            updated_session = browser_conversation_intake_service.append_capture(
                session_id=session_id,
                snippets=[{"type": "focus_marker", "note": completion_note or "thread focused"}],
                code_blocks=[],
                warnings=[],
                increment_scroll_steps=0,
                capture_status="capturing",
            )
        else:
            updated_session = browser_conversation_intake_service.append_capture(
                session_id=session_id,
                snippets=[{"type": "scroll_capture_marker", "note": completion_note or "scroll capture advanced"}],
                code_blocks=[],
                warnings=[],
                increment_scroll_steps=1,
                capture_status="capturing",
            )

        actions = self._actions_for_session(updated_session)
        for action in actions:
            if action["action_id"] == action_id:
                action["action_status"] = "completed"
                action["completion_note"] = completion_note or "completed"
                break

        return {
            "ok": True,
            "mode": "browser_control_action_advanced",
            "control_id": control_id,
            "action_id": action_id,
            "session": browser_conversation_intake_service.get_capture_progress(session_id)["progress"],
            "actions": actions,
        }


browser_control_real_service = BrowserControlRealService()
