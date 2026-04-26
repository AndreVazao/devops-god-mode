from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict
from uuid import uuid4

from app.services.chat_action_cards_service import chat_action_cards_service
from app.services.god_mode_home_service import god_mode_home_service
from app.services.operator_conversation_thread_service import operator_conversation_thread_service
from app.utils.atomic_json_store import AtomicJsonStore

DATA_DIR = Path("data")
INLINE_RENDERER_FILE = DATA_DIR / "chat_inline_card_renderer.json"
INLINE_RENDERER_STORE = AtomicJsonStore(
    INLINE_RENDERER_FILE,
    default_factory=lambda: {"sessions": [], "render_events": []},
)


class ChatInlineCardRendererService:
    """Renderer manifest and session helper for chat-first APK inline action cards."""

    def get_status(self) -> Dict[str, Any]:
        store = self._load_store()
        return {
            "ok": True,
            "mode": "chat_inline_card_renderer_status",
            "status": "chat_inline_card_renderer_ready",
            "store_file": str(INLINE_RENDERER_FILE),
            "atomic_store_enabled": True,
            "apk_chat_first": True,
            "inline_cards_enabled": True,
            "session_count": len(store.get("sessions", [])),
            "render_event_count": len(store.get("render_events", [])),
        }

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def _normalize_store(self, store: Dict[str, Any]) -> Dict[str, Any]:
        if not isinstance(store, dict):
            return {"sessions": [], "render_events": []}
        store.setdefault("sessions", [])
        store.setdefault("render_events", [])
        return store

    def _load_store(self) -> Dict[str, Any]:
        return self._normalize_store(INLINE_RENDERER_STORE.load())

    def build_manifest(self, tenant_id: str = "owner-andre") -> Dict[str, Any]:
        cards = chat_action_cards_service.build_dashboard(tenant_id=tenant_id)
        home = god_mode_home_service.build_dashboard(tenant_id=tenant_id)
        manifest = {
            "manifest_id": f"inline-renderer-{uuid4().hex[:12]}",
            "created_at": self._now(),
            "tenant_id": tenant_id,
            "frontend_routes": {
                "primary": "/app/operator-chat-sync-cards",
                "alias": "/app/chat-inline-cards",
                "legacy_sync_chat": "/app/operator-chat-sync",
                "cards_admin": "/app/chat-action-cards",
            },
            "api_routes": {
                "send_message_and_cards": "/api/chat-inline-card-renderer/send",
                "cards_from_home_chat": "/api/chat-action-cards/from-home-chat",
                "execute_card": "/api/chat-action-cards/execute",
                "dismiss_card": "/api/chat-action-cards/dismiss",
                "list_cards": "/api/chat-action-cards/cards",
            },
            "render_contract": {
                "message_mode": "continuous_chat_like_chatgpt",
                "card_marker_prefix": "[ACTION_CARD:",
                "render_inline": True,
                "primary_buttons": ["executar", "ignorar", "abrir chat antigo"],
                "no_secrets_rule": True,
                "mobile_first": True,
            },
            "current_card_summary": {
                "open_count": cards.get("open_count", 0),
                "high_priority_open_count": cards.get("high_priority_open_count", 0),
            },
            "home_next_action": home.get("next_action"),
        }
        return {"ok": True, "mode": "chat_inline_card_renderer_manifest", "manifest": manifest}

    def open_session(self, tenant_id: str = "owner-andre", title: str = "God Mode APK chat") -> Dict[str, Any]:
        opened = operator_conversation_thread_service.open_thread(
            tenant_id=tenant_id,
            conversation_title=title,
            channel_mode="apk_inline_action_card_chat",
        )
        if not opened.get("ok"):
            return opened
        session = {
            "session_id": f"inline-session-{uuid4().hex[:12]}",
            "created_at": self._now(),
            "tenant_id": tenant_id,
            "thread_id": opened["thread"]["thread_id"],
            "title": title,
            "status": "open",
        }

        def mutate(store: Dict[str, Any]) -> Dict[str, Any]:
            store = self._normalize_store(store)
            store["sessions"].append(session)
            store["sessions"] = store["sessions"][-200:]
            return store

        INLINE_RENDERER_STORE.update(mutate)
        return {"ok": True, "mode": "chat_inline_card_renderer_open_session", "session": session, "thread": opened["thread"]}

    def send_message(self, message: str, thread_id: str | None = None, tenant_id: str = "owner-andre", project_id: str = "GOD_MODE") -> Dict[str, Any]:
        if not thread_id:
            opened = self.open_session(tenant_id=tenant_id)
            if not opened.get("ok"):
                return opened
            thread_id = opened["session"]["thread_id"]
        result = chat_action_cards_service.create_cards_from_home_chat(
            message=message,
            thread_id=thread_id,
            tenant_id=tenant_id,
            project_id=project_id,
        )
        event = {
            "event_id": f"inline-render-{uuid4().hex[:12]}",
            "created_at": self._now(),
            "tenant_id": tenant_id,
            "thread_id": thread_id,
            "project_id": project_id,
            "ok": bool(result.get("ok")),
            "card_count": len(result.get("cards", [])),
        }

        def mutate(store: Dict[str, Any]) -> Dict[str, Any]:
            store = self._normalize_store(store)
            store["render_events"].append(event)
            store["render_events"] = store["render_events"][-500:]
            return store

        INLINE_RENDERER_STORE.update(mutate)
        thread = operator_conversation_thread_service.get_thread(thread_id)
        cards = chat_action_cards_service.list_cards(tenant_id=tenant_id, thread_id=thread_id, status="open", limit=50)
        return {
            "ok": True,
            "mode": "chat_inline_card_renderer_send",
            "event": event,
            "thread_id": thread_id,
            "chat_result": result,
            "thread": thread,
            "open_cards": cards.get("cards", []),
        }

    def build_dashboard(self, tenant_id: str = "owner-andre") -> Dict[str, Any]:
        store = self._load_store()
        cards = chat_action_cards_service.build_dashboard(tenant_id=tenant_id)
        manifest = self.build_manifest(tenant_id=tenant_id).get("manifest", {})
        return {
            "ok": True,
            "mode": "chat_inline_card_renderer_dashboard",
            "tenant_id": tenant_id,
            "status": self.get_status(),
            "manifest": manifest,
            "card_dashboard": cards,
            "recent_sessions": store.get("sessions", [])[-20:],
            "recent_render_events": store.get("render_events", [])[-30:],
        }

    def get_package(self) -> Dict[str, Any]:
        return {"ok": True, "mode": "chat_inline_card_renderer_package", "package": {"status": self.get_status(), "dashboard": self.build_dashboard()}}


chat_inline_card_renderer_service = ChatInlineCardRendererService()
