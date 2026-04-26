from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List
from uuid import uuid4

from app.services.god_mode_home_service import god_mode_home_service
from app.services.memory_core_service import memory_core_service
from app.services.mobile_approval_cockpit_v2_service import mobile_approval_cockpit_v2_service
from app.services.money_command_center_service import money_command_center_service
from app.services.operator_conversation_thread_service import operator_conversation_thread_service
from app.utils.atomic_json_store import AtomicJsonStore

DATA_DIR = Path("data")
CHAT_ACTION_CARDS_FILE = DATA_DIR / "chat_action_cards.json"
CHAT_ACTION_CARDS_STORE = AtomicJsonStore(
    CHAT_ACTION_CARDS_FILE,
    default_factory=lambda: {"cards": [], "executions": []},
)

SAFE_CARD_ACTIONS = {
    "open_url",
    "one_tap_money",
    "one_tap_continue_god_mode",
    "one_tap_review_memory",
    "create_money_approval_card",
    "decide_mobile_approval",
    "acknowledge",
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


class ChatActionCardsService:
    """Action cards that can be rendered and clicked inline inside the APK chat."""

    def get_status(self) -> Dict[str, Any]:
        store = self._load_store()
        return {
            "ok": True,
            "mode": "chat_action_cards_status",
            "status": "chat_action_cards_ready",
            "store_file": str(CHAT_ACTION_CARDS_FILE),
            "atomic_store_enabled": True,
            "safe_actions": sorted(SAFE_CARD_ACTIONS),
            "card_count": len(store.get("cards", [])),
            "execution_count": len(store.get("executions", [])),
        }

    def _normalize_store(self, store: Dict[str, Any]) -> Dict[str, Any]:
        if not isinstance(store, dict):
            return {"cards": [], "executions": []}
        store.setdefault("cards", [])
        store.setdefault("executions", [])
        return store

    def _load_store(self) -> Dict[str, Any]:
        return self._normalize_store(CHAT_ACTION_CARDS_STORE.load())

    def _save_card(self, card: Dict[str, Any]) -> None:
        def mutate(store: Dict[str, Any]) -> Dict[str, Any]:
            store = self._normalize_store(store)
            store["cards"].append(card)
            store["cards"] = store["cards"][-1000:]
            return store

        CHAT_ACTION_CARDS_STORE.update(mutate)

    def _append_chat_card_message(self, thread_id: str, card: Dict[str, Any]) -> Dict[str, Any]:
        body = (
            f"[ACTION_CARD:{card['card_id']}] {card['title']}\n"
            f"{card.get('body', '')}\n"
            f"Ações: {', '.join(action['label'] for action in card.get('actions', []))}"
        )
        return operator_conversation_thread_service.append_message(
            thread_id=thread_id,
            role="assistant",
            content=body,
            operational_state="action_card",
            suggested_next_steps=[action["label"] for action in card.get("actions", [])],
        )

    def create_card(
        self,
        thread_id: str,
        title: str,
        body: str,
        actions: List[Dict[str, Any]],
        tenant_id: str = "owner-andre",
        project_id: str = "GOD_MODE",
        source: str = "chat",
        priority: str = "medium",
    ) -> Dict[str, Any]:
        valid_actions: List[Dict[str, Any]] = []
        for action in actions:
            action_type = action.get("action_type")
            if action_type in SAFE_CARD_ACTIONS:
                valid_actions.append({
                    "action_id": action.get("action_id") or f"card-action-{uuid4().hex[:8]}",
                    "label": action.get("label") or action_type,
                    "action_type": action_type,
                    "payload": action.get("payload", {}),
                    "requires_approval": bool(action.get("requires_approval", False)),
                })
        if not valid_actions:
            return {"ok": False, "error": "no_valid_actions", "allowed": sorted(SAFE_CARD_ACTIONS)}
        thread = operator_conversation_thread_service.get_thread(thread_id)
        if not thread.get("ok"):
            return {"ok": False, "error": "thread_not_found", "thread_id": thread_id}
        card = {
            "card_id": f"chat-card-{uuid4().hex[:12]}",
            "thread_id": thread_id,
            "tenant_id": tenant_id,
            "project_id": project_id,
            "title": title.strip() or "Ação sugerida",
            "body": body.strip(),
            "source": source,
            "priority": priority,
            "status": "open",
            "actions": valid_actions,
            "created_at": _now(),
            "updated_at": _now(),
        }
        self._save_card(card)
        append_result = self._append_chat_card_message(thread_id, card)
        memory_core_service.write_history("GOD_MODE", "Chat action card created", f"Card {card['card_id']} in thread {thread_id}: {card['title']}")
        return {"ok": True, "mode": "chat_action_card_create", "card": card, "chat_append": append_result}

    def create_cards_from_home_chat(
        self,
        message: str,
        thread_id: str | None = None,
        tenant_id: str = "owner-andre",
        project_id: str = "GOD_MODE",
    ) -> Dict[str, Any]:
        chat = god_mode_home_service.chat(message=message, thread_id=thread_id, tenant_id=tenant_id, project_id=project_id)
        if not chat.get("ok"):
            return chat
        actual_thread_id = chat["thread_id"]
        suggestions = chat.get("suggested_next_steps", [])
        cards: List[Dict[str, Any]] = []
        for suggestion in suggestions[:3]:
            card = self._card_for_suggestion(actual_thread_id, suggestion, tenant_id, project_id)
            if card.get("ok"):
                cards.append(card["card"])
        return {"ok": True, "mode": "chat_action_cards_from_home_chat", "chat": chat, "cards": cards, "thread_id": actual_thread_id}

    def _card_for_suggestion(self, thread_id: str, suggestion: str, tenant_id: str, project_id: str) -> Dict[str, Any]:
        lowered = suggestion.lower()
        if "dinheiro" in lowered:
            return self.create_card(
                thread_id=thread_id,
                tenant_id=tenant_id,
                project_id=project_id,
                title="Criar próximo passo para dinheiro",
                body="Cria um cartão de aprovação para o próximo sprint curto de receita.",
                priority="high",
                source="home_chat_suggestion",
                actions=[{"label": "Criar cartão", "action_type": "one_tap_money", "requires_approval": False}],
            )
        if "continuar" in lowered or "god mode" in lowered:
            return self.create_card(
                thread_id=thread_id,
                tenant_id=tenant_id,
                project_id="GOD_MODE",
                title="Continuar God Mode",
                body="Submete uma continuação guiada e segura para o God Mode.",
                priority="high",
                source="home_chat_suggestion",
                actions=[{"label": "Continuar", "action_type": "one_tap_continue_god_mode", "requires_approval": False}],
            )
        if "memória" in lowered or "memoria" in lowered:
            return self.create_card(
                thread_id=thread_id,
                tenant_id=tenant_id,
                project_id=project_id,
                title="Rever memória",
                body="Revê a memória AndreOS do projeto ativo e cria próximos passos.",
                source="home_chat_suggestion",
                actions=[{"label": "Rever memória", "action_type": "one_tap_review_memory", "payload": {"project_id": project_id}, "requires_approval": False}],
            )
        if "aprova" in lowered:
            return self.create_card(
                thread_id=thread_id,
                tenant_id=tenant_id,
                project_id=project_id,
                title="Abrir aprovações",
                body="Abre o cockpit de aprovações mobile.",
                source="home_chat_suggestion",
                actions=[{"label": "Abrir aprovações", "action_type": "open_url", "payload": {"url": "/app/mobile-approval-cockpit-v2"}}],
            )
        return self.create_card(
            thread_id=thread_id,
            tenant_id=tenant_id,
            project_id=project_id,
            title=suggestion,
            body="Ação sugerida pelo chat do God Mode.",
            source="home_chat_suggestion",
            actions=[{"label": "Abrir chat", "action_type": "open_url", "payload": {"url": "/app/operator-chat-sync"}}],
        )

    def list_cards(self, tenant_id: str = "owner-andre", thread_id: str | None = None, status: str | None = None, limit: int = 100) -> Dict[str, Any]:
        store = self._load_store()
        cards = [card for card in store.get("cards", []) if card.get("tenant_id") == tenant_id]
        if thread_id:
            cards = [card for card in cards if card.get("thread_id") == thread_id]
        if status:
            cards = [card for card in cards if card.get("status") == status]
        return {"ok": True, "mode": "chat_action_cards_list", "card_count": len(cards[-limit:]), "cards": cards[-limit:]}

    def execute_card_action(self, card_id: str, action_id: str, tenant_id: str = "owner-andre") -> Dict[str, Any]:
        store = self._load_store()
        card = next((item for item in store.get("cards", []) if item.get("card_id") == card_id and item.get("tenant_id") == tenant_id), None)
        if not card:
            return {"ok": False, "error": "card_not_found", "card_id": card_id}
        if card.get("status") in {"executed", "dismissed"}:
            return {"ok": False, "error": "card_closed", "status": card.get("status")}
        action = next((item for item in card.get("actions", []) if item.get("action_id") == action_id or item.get("label") == action_id), None)
        if not action:
            return {"ok": False, "error": "action_not_found", "action_id": action_id}
        result = self._execute_action(card, action)
        execution = {
            "execution_id": f"chat-card-exec-{uuid4().hex[:12]}",
            "created_at": _now(),
            "tenant_id": tenant_id,
            "card_id": card_id,
            "thread_id": card.get("thread_id"),
            "action_id": action.get("action_id"),
            "action_type": action.get("action_type"),
            "ok": bool(result.get("ok")),
            "result_mode": result.get("mode"),
        }

        def mutate(payload: Dict[str, Any]) -> Dict[str, Any]:
            payload = self._normalize_store(payload)
            for item in payload.get("cards", []):
                if item.get("card_id") == card_id and item.get("tenant_id") == tenant_id:
                    item["status"] = "executed" if result.get("ok") else "failed"
                    item["updated_at"] = _now()
                    item["last_execution"] = execution
                    break
            payload["executions"].append(execution)
            payload["executions"] = payload["executions"][-1000:]
            return payload

        CHAT_ACTION_CARDS_STORE.update(mutate)
        operator_conversation_thread_service.append_message(
            thread_id=card.get("thread_id"),
            role="assistant",
            content=f"Ação executada: {action.get('label')} — {'ok' if result.get('ok') else 'erro'}",
            operational_state="action_card_executed" if result.get("ok") else "action_card_failed",
            suggested_next_steps=["Continuar conversa", "Abrir Home"],
        )
        memory_core_service.write_history("GOD_MODE", "Chat action card executed", f"{card_id} -> {action.get('action_type')} | ok={result.get('ok')}")
        return {"ok": True, "mode": "chat_action_card_execute", "execution": execution, "result": result}

    def _execute_action(self, card: Dict[str, Any], action: Dict[str, Any]) -> Dict[str, Any]:
        action_type = action.get("action_type")
        payload = action.get("payload", {}) or {}
        tenant_id = card.get("tenant_id", "owner-andre")
        project_id = payload.get("project_id") or card.get("project_id", "GOD_MODE")
        if action_type == "open_url":
            return {"ok": True, "mode": "chat_action_open_url", "url": payload.get("url", "/app/operator-chat-sync")}
        if action_type == "one_tap_money":
            return god_mode_home_service.run_one_tap("one-tap-money", tenant_id=tenant_id, project_id=project_id)
        if action_type == "one_tap_continue_god_mode":
            return god_mode_home_service.run_one_tap("one-tap-continue-god-mode", tenant_id=tenant_id, project_id="GOD_MODE")
        if action_type == "one_tap_review_memory":
            return god_mode_home_service.run_one_tap("one-tap-review-memory", tenant_id=tenant_id, project_id=project_id)
        if action_type == "create_money_approval_card":
            return money_command_center_service.create_approval_card(max_projects=int(payload.get("max_projects", 2)), tenant_id=tenant_id)
        if action_type == "decide_mobile_approval":
            return mobile_approval_cockpit_v2_service.decide_card(card_id=payload.get("approval_card_id", ""), decision=payload.get("decision", "acknowledged"), operator_note=payload.get("operator_note", "Decidido via chat action card"), tenant_id=tenant_id)
        if action_type == "acknowledge":
            return {"ok": True, "mode": "chat_action_acknowledge"}
        return {"ok": False, "error": "unsupported_action_type", "action_type": action_type}

    def dismiss_card(self, card_id: str, tenant_id: str = "owner-andre") -> Dict[str, Any]:
        found = False

        def mutate(payload: Dict[str, Any]) -> Dict[str, Any]:
            nonlocal found
            payload = self._normalize_store(payload)
            for card in payload.get("cards", []):
                if card.get("card_id") == card_id and card.get("tenant_id") == tenant_id:
                    card["status"] = "dismissed"
                    card["updated_at"] = _now()
                    found = True
                    break
            return payload

        CHAT_ACTION_CARDS_STORE.update(mutate)
        return {"ok": found, "mode": "chat_action_card_dismiss", "card_id": card_id, "status": "dismissed" if found else "not_found"}

    def build_dashboard(self, tenant_id: str = "owner-andre") -> Dict[str, Any]:
        cards = self.list_cards(tenant_id=tenant_id, limit=300).get("cards", [])
        open_cards = [card for card in cards if card.get("status") == "open"]
        high = [card for card in open_cards if card.get("priority") in {"high", "critical"}]
        return {
            "ok": True,
            "mode": "chat_action_cards_dashboard",
            "tenant_id": tenant_id,
            "card_count": len(cards),
            "open_count": len(open_cards),
            "high_priority_open_count": len(high),
            "recent_cards": cards[-50:],
            "apk_contract": {
                "render_inline": True,
                "card_marker_prefix": "[ACTION_CARD:",
                "click_endpoint": "/api/chat-action-cards/execute",
                "dismiss_endpoint": "/api/chat-action-cards/dismiss",
            },
        }

    def get_package(self) -> Dict[str, Any]:
        return {"ok": True, "mode": "chat_action_cards_package", "package": {"status": self.get_status(), "dashboard": self.build_dashboard()}}


chat_action_cards_service = ChatActionCardsService()
