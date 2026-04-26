from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List
from uuid import uuid4

from app.services.chat_action_cards_service import chat_action_cards_service
from app.services.mobile_first_run_wizard_service import mobile_first_run_wizard_service
from app.services.mobile_approval_cockpit_v2_service import mobile_approval_cockpit_v2_service
from app.services.money_command_center_service import money_command_center_service
from app.services.operator_conversation_thread_service import operator_conversation_thread_service
from app.utils.atomic_json_store import AtomicJsonStore

DATA_DIR = Path("data")
CHAT_BOOT_FILE = DATA_DIR / "chat_boot_briefing.json"
CHAT_BOOT_STORE = AtomicJsonStore(
    CHAT_BOOT_FILE,
    default_factory=lambda: {"briefings": [], "boots": []},
)


class ChatBootBriefingService:
    """Create an automatic mobile chat briefing with inline action cards."""

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def _normalize_store(self, store: Dict[str, Any]) -> Dict[str, Any]:
        if not isinstance(store, dict):
            return {"briefings": [], "boots": []}
        store.setdefault("briefings", [])
        store.setdefault("boots", [])
        return store

    def _load_store(self) -> Dict[str, Any]:
        return self._normalize_store(CHAT_BOOT_STORE.load())

    def _safe(self, label: str, fn: Any) -> Dict[str, Any]:
        try:
            result = fn()
            return {"ok": bool(result.get("ok", True)), "label": label, "result": result}
        except Exception as exc:  # pragma: no cover - boot briefing should fail soft
            return {"ok": False, "label": label, "error": str(exc)}

    def get_status(self) -> Dict[str, Any]:
        store = self._load_store()
        return {
            "ok": True,
            "mode": "chat_boot_briefing_status",
            "status": "chat_boot_briefing_ready",
            "store_file": str(CHAT_BOOT_FILE),
            "atomic_store_enabled": True,
            "briefing_count": len(store.get("briefings", [])),
            "boot_count": len(store.get("boots", [])),
        }

    def build_briefing(self, tenant_id: str = "owner-andre", device_id: str = "android-apk") -> Dict[str, Any]:
        first_run = self._safe("first_run", lambda: mobile_first_run_wizard_service.run_check(tenant_id=tenant_id, device_id=device_id))
        money = self._safe("money", lambda: money_command_center_service.top_project())
        approvals = self._safe("approvals", lambda: mobile_approval_cockpit_v2_service.build_dashboard(tenant_id=tenant_id))

        first_check = first_run.get("result", {}).get("check", {}) if first_run.get("ok") else {}
        money_top = money.get("result", {}).get("top_project", {}) if money.get("ok") else {}
        approval_count = approvals.get("result", {}).get("pending_approval_count", 0) if approvals.get("ok") else 0
        status = first_check.get("status", "yellow")
        recommended_route = first_check.get("recommended_route", "/app/operator-chat-sync-cards")
        fallback_route = first_check.get("fallback_route", "/app/operator-chat-sync")
        lines = [
            f"Estado mobile: {status}.",
            f"Rota recomendada: {recommended_route}.",
            f"Aprovações pendentes: {approval_count}.",
        ]
        if money_top:
            lines.append(f"Melhor próximo projeto para dinheiro: {money_top.get('name')} — {money_top.get('first_sellable_feature')}.")
        else:
            lines.append("Ainda não consegui escolher projeto de dinheiro com confiança.")
        if status == "green":
            headline = "Tudo pronto. Podemos trabalhar no chat com cartões."
        elif status == "yellow":
            headline = "Quase tudo pronto. Podes avançar, mantendo fallback."
        else:
            headline = "Há falhas. Usa fallback ou home segura antes de avançar."
        briefing = {
            "briefing_id": f"chat-boot-briefing-{uuid4().hex[:12]}",
            "created_at": self._now(),
            "tenant_id": tenant_id,
            "device_id": device_id,
            "status": status,
            "headline": headline,
            "message": "\n".join([headline, "", *lines]),
            "recommended_route": recommended_route,
            "fallback_route": fallback_route,
            "safe_home_route": first_check.get("safe_home_route", "/app/home"),
            "money_project": money_top.get("project_id"),
            "money_project_name": money_top.get("name"),
            "pending_approvals": approval_count,
            "snapshots": {"first_run": first_run, "money": money, "approvals": approvals},
        }

        def mutate(store: Dict[str, Any]) -> Dict[str, Any]:
            store = self._normalize_store(store)
            store["briefings"].append(briefing)
            store["briefings"] = store["briefings"][-300:]
            return store

        CHAT_BOOT_STORE.update(mutate)
        return {"ok": True, "mode": "chat_boot_briefing_build", "briefing": briefing}

    def _open_or_create_thread(self, tenant_id: str, thread_id: str | None) -> Dict[str, Any]:
        if thread_id:
            existing = operator_conversation_thread_service.get_thread(thread_id)
            if existing.get("ok"):
                return existing
        return operator_conversation_thread_service.open_thread(
            tenant_id=tenant_id,
            conversation_title="God Mode boot briefing",
            channel_mode="apk_inline_action_card_chat",
        )

    def boot_chat(self, tenant_id: str = "owner-andre", device_id: str = "android-apk", thread_id: str | None = None) -> Dict[str, Any]:
        opened = self._open_or_create_thread(tenant_id=tenant_id, thread_id=thread_id)
        if not opened.get("ok"):
            return opened
        actual_thread_id = opened.get("thread", {}).get("thread_id") or thread_id
        briefing = self.build_briefing(tenant_id=tenant_id, device_id=device_id).get("briefing", {})
        append = operator_conversation_thread_service.append_message(
            thread_id=actual_thread_id,
            role="assistant",
            content=briefing.get("message", "God Mode pronto."),
            operational_state="boot_briefing",
            suggested_next_steps=["Entrar no God Mode", "Criar próximo passo para dinheiro", "Abrir aprovações"],
        )
        cards = self._create_cards(actual_thread_id, briefing, tenant_id)
        boot = {
            "boot_id": f"chat-boot-{uuid4().hex[:12]}",
            "created_at": self._now(),
            "tenant_id": tenant_id,
            "device_id": device_id,
            "thread_id": actual_thread_id,
            "briefing_id": briefing.get("briefing_id"),
            "card_count": len(cards),
            "status": briefing.get("status"),
        }

        def mutate(store: Dict[str, Any]) -> Dict[str, Any]:
            store = self._normalize_store(store)
            store["boots"].append(boot)
            store["boots"] = store["boots"][-300:]
            return store

        CHAT_BOOT_STORE.update(mutate)
        return {"ok": True, "mode": "chat_boot_briefing_boot", "boot": boot, "briefing": briefing, "append": append, "cards": cards, "thread": operator_conversation_thread_service.get_thread(actual_thread_id)}

    def _create_cards(self, thread_id: str, briefing: Dict[str, Any], tenant_id: str) -> List[Dict[str, Any]]:
        cards: List[Dict[str, Any]] = []
        card_specs = [
            {
                "title": "Entrar no God Mode",
                "body": f"Abrir rota recomendada: {briefing.get('recommended_route')}",
                "priority": "critical",
                "actions": [{"label": "Abrir", "action_type": "open_url", "payload": {"url": briefing.get("recommended_route", "/app/operator-chat-sync-cards")}}],
            },
            {
                "title": "Criar próximo passo para dinheiro",
                "body": "Cria um cartão de aprovação para o próximo sprint de receita.",
                "priority": "high",
                "actions": [{"label": "Criar", "action_type": "one_tap_money"}],
            },
            {
                "title": "Abrir aprovações",
                "body": f"Pendentes: {briefing.get('pending_approvals', 0)}.",
                "priority": "high" if int(briefing.get("pending_approvals", 0)) else "medium",
                "actions": [{"label": "Abrir aprovações", "action_type": "open_url", "payload": {"url": "/app/mobile-approval-cockpit-v2"}}],
            },
        ]
        for spec in card_specs:
            created = chat_action_cards_service.create_card(
                thread_id=thread_id,
                title=spec["title"],
                body=spec["body"],
                actions=spec["actions"],
                tenant_id=tenant_id,
                project_id="GOD_MODE",
                source="chat_boot_briefing",
                priority=spec["priority"],
            )
            if created.get("ok"):
                cards.append(created["card"])
        return cards

    def build_dashboard(self, tenant_id: str = "owner-andre", device_id: str = "android-apk") -> Dict[str, Any]:
        store = self._load_store()
        briefing = self.build_briefing(tenant_id=tenant_id, device_id=device_id).get("briefing", {})
        return {
            "ok": True,
            "mode": "chat_boot_briefing_dashboard",
            "tenant_id": tenant_id,
            "device_id": device_id,
            "status": self.get_status(),
            "briefing": briefing,
            "buttons": [
                {"id": "boot", "label": "Criar briefing no chat", "endpoint": "/api/chat-boot-briefing/boot", "priority": "critical"},
                {"id": "open", "label": "Abrir chat", "route": briefing.get("recommended_route", "/app/operator-chat-sync-cards"), "priority": "high"},
                {"id": "fallback", "label": "Fallback", "route": briefing.get("fallback_route", "/app/operator-chat-sync"), "priority": "medium"},
            ],
            "recent_briefings": store.get("briefings", [])[-20:],
            "recent_boots": store.get("boots", [])[-20:],
        }

    def get_package(self) -> Dict[str, Any]:
        return {"ok": True, "mode": "chat_boot_briefing_package", "package": {"status": self.get_status(), "dashboard": self.build_dashboard()}}


chat_boot_briefing_service = ChatBootBriefingService()
