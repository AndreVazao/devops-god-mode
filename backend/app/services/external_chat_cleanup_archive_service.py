from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import uuid4

from app.services.memory_context_router_service import memory_context_router_service
from app.services.operator_priority_service import operator_priority_service
from app.utils.atomic_json_store import AtomicJsonStore

DATA_DIR = Path("data")
CLEANUP_FILE = DATA_DIR / "external_chat_cleanup_archive.json"
CLEANUP_STORE = AtomicJsonStore(
    CLEANUP_FILE,
    default_factory=lambda: {
        "version": 1,
        "policy": "extract_memory_before_external_chat_cleanup",
        "inventories": [],
        "memory_extractions": [],
        "cleanup_plans": [],
        "archive_decisions": [],
    },
)


class ExternalChatCleanupArchiveService:
    """Plan cleanup/archive for external AI conversations.

    The service does not delete provider conversations by itself. It creates a
    safe cleanup plan after useful context has been extracted into AndreOS memory.
    Real delete/archive actions require an explicit approval gate and provider
    support in a later executor.
    """

    PROVIDERS = ["chatgpt", "deepseek", "claude", "gemini", "perplexity", "local_ai"]

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def policy(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "mode": "external_chat_cleanup_policy",
            "rules": [
                "Nunca limpar conversa antes de extrair contexto útil para a memória do projeto.",
                "Conversas temporárias de testes/correções podem ser propostas para limpeza quando não tiverem valor futuro.",
                "Conversas antigas de projeto podem ser arquivadas ou apagadas quando o projeto estiver concluído e validado.",
                "A limpeza real exige aprovação explícita ou estado de projeto concluído com política de limpeza ativa.",
                "Guardar sempre referência mínima: provider, título, projeto, motivo e resumo extraído.",
                "Não guardar dados sensíveis de acesso/autenticação em memória.",
            ],
            "cleanup_actions": ["keep", "extract_then_archive", "extract_then_delete", "needs_operator_review"],
            "default_action": "needs_operator_review",
        }

    def inventory(
        self,
        provider_id: str = "chatgpt",
        conversations: Optional[List[Dict[str, Any]]] = None,
        project_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        provider = provider_id if provider_id in self.PROVIDERS else provider_id.strip().lower() or "unknown"
        project = self._resolve_project(project_id)
        items = []
        for raw in conversations or []:
            item = self._normalize_conversation(raw, provider, project)
            items.append(item)
        inventory = {
            "inventory_id": f"chat-inventory-{uuid4().hex[:12]}",
            "created_at": self._now(),
            "provider_id": provider,
            "project_id": project,
            "conversation_count": len(items),
            "conversations": items,
            "source": "operator_or_external_reader_snapshot",
        }
        self._store("inventories", inventory)
        return {"ok": True, "mode": "external_chat_inventory", "inventory": inventory}

    def _normalize_conversation(self, raw: Dict[str, Any], provider: str, default_project: str) -> Dict[str, Any]:
        title = str(raw.get("title") or raw.get("name") or "Untitled conversation")[:300]
        summary = str(raw.get("summary") or raw.get("snippet") or raw.get("notes") or "")[:2000]
        project = str(raw.get("project_id") or default_project).strip().upper().replace("-", "_").replace(" ", "_")
        return {
            "conversation_id": str(raw.get("conversation_id") or raw.get("id") or f"external-{uuid4().hex[:10]}")[:200],
            "provider_id": provider,
            "title": title,
            "project_id": project,
            "summary": summary,
            "url": raw.get("url"),
            "conversation_index": raw.get("conversation_index"),
            "status_hint": raw.get("status_hint", "unknown"),
            "created_at_hint": raw.get("created_at"),
            "updated_at_hint": raw.get("updated_at"),
            "operator_marked_done": bool(raw.get("operator_marked_done", False)),
            "temporary": bool(raw.get("temporary", False)),
        }

    def extract_memory(
        self,
        conversation: Dict[str, Any],
        project_id: Optional[str] = None,
        extraction_summary: str = "",
        backlog_items: Optional[List[str]] = None,
        decisions: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        normalized = self._normalize_conversation(conversation, str(conversation.get("provider_id") or "unknown"), self._resolve_project(project_id))
        project = self._resolve_project(project_id or normalized.get("project_id"))
        context = memory_context_router_service.prepare_project_context(
            project_id=project,
            source="external_chat_cleanup_extraction",
            idea=(extraction_summary or normalized.get("summary") or normalized.get("title")),
            max_chars=10000,
        ).get("context_pack")
        extraction = {
            "extraction_id": f"chat-extraction-{uuid4().hex[:12]}",
            "created_at": self._now(),
            "project_id": project,
            "provider_id": normalized.get("provider_id"),
            "conversation_id": normalized.get("conversation_id"),
            "conversation_title": normalized.get("title"),
            "extraction_summary": extraction_summary or normalized.get("summary") or normalized.get("title"),
            "backlog_items": backlog_items or [],
            "decisions": decisions or [],
            "context_pack_id": (context or {}).get("context_pack_id"),
            "safe_to_cleanup_after_extraction": True,
        }
        self._store("memory_extractions", extraction)
        return {"ok": True, "mode": "external_chat_memory_extraction", "extraction": extraction}

    def cleanup_plan(
        self,
        provider_id: str = "chatgpt",
        project_id: Optional[str] = None,
        project_done: bool = False,
        conversations: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        inventory = self.inventory(provider_id=provider_id, conversations=conversations or [], project_id=project_id).get("inventory", {})
        extractions = CLEANUP_STORE.load().get("memory_extractions", [])
        extraction_keys = {(e.get("provider_id"), e.get("conversation_id")) for e in extractions}
        actions = []
        for convo in inventory.get("conversations", []):
            key = (convo.get("provider_id"), convo.get("conversation_id"))
            extracted = key in extraction_keys
            action = self._decide_action(convo, extracted=extracted, project_done=project_done)
            actions.append({
                "conversation_id": convo.get("conversation_id"),
                "provider_id": convo.get("provider_id"),
                "project_id": convo.get("project_id"),
                "title": convo.get("title"),
                "extracted_to_memory": extracted,
                "recommended_action": action["action"],
                "reason": action["reason"],
                "requires_operator_approval": action["requires_operator_approval"],
            })
        plan = {
            "cleanup_plan_id": f"chat-cleanup-plan-{uuid4().hex[:12]}",
            "created_at": self._now(),
            "provider_id": inventory.get("provider_id"),
            "project_id": inventory.get("project_id"),
            "project_done": project_done,
            "inventory_id": inventory.get("inventory_id"),
            "actions": actions,
            "delete_count": len([a for a in actions if a.get("recommended_action") == "extract_then_delete"]),
            "archive_count": len([a for a in actions if a.get("recommended_action") == "extract_then_archive"]),
            "review_count": len([a for a in actions if a.get("recommended_action") == "needs_operator_review"]),
            "keep_count": len([a for a in actions if a.get("recommended_action") == "keep"]),
            "execution_allowed_now": False,
            "why_not_execute": "provider delete/archive requires explicit approval and provider-specific executor",
            "operator_next": {"label": "Rever plano de limpeza", "endpoint": "/api/external-chat-cleanup/plan", "route": "/app/home"},
        }
        self._store("cleanup_plans", plan)
        return {"ok": True, "mode": "external_chat_cleanup_plan", "plan": plan}

    def _decide_action(self, convo: Dict[str, Any], extracted: bool, project_done: bool) -> Dict[str, Any]:
        if not extracted:
            return {"action": "needs_operator_review", "reason": "context_not_extracted_yet", "requires_operator_approval": True}
        if convo.get("temporary"):
            return {"action": "extract_then_delete", "reason": "temporary_work_conversation_already_extracted", "requires_operator_approval": True}
        if project_done or convo.get("operator_marked_done"):
            return {"action": "extract_then_archive", "reason": "project_done_or_operator_marked_done", "requires_operator_approval": True}
        title = (convo.get("title") or "").lower()
        if any(term in title for term in ["teste", "test", "draft", "rascunho", "erro rapido"]):
            return {"action": "extract_then_delete", "reason": "low_value_test_or_draft", "requires_operator_approval": True}
        return {"action": "keep", "reason": "active_or_potentially_useful_conversation", "requires_operator_approval": False}

    def approve_cleanup_plan(self, cleanup_plan_id: str, approval_phrase: str = "") -> Dict[str, Any]:
        if approval_phrase != "CLEANUP EXTERNAL CHATS":
            return {"ok": False, "mode": "external_chat_cleanup_approval", "error": "approval_phrase_required", "required_phrase": "CLEANUP EXTERNAL CHATS"}
        plans = CLEANUP_STORE.load().get("cleanup_plans", [])
        plan = next((p for p in plans if p.get("cleanup_plan_id") == cleanup_plan_id), None)
        if not plan:
            return {"ok": False, "mode": "external_chat_cleanup_approval", "error": "plan_not_found"}
        decision = {
            "decision_id": f"chat-cleanup-decision-{uuid4().hex[:12]}",
            "created_at": self._now(),
            "cleanup_plan_id": cleanup_plan_id,
            "approval_phrase": "CLEANUP EXTERNAL CHATS",
            "approved_actions": plan.get("actions", []),
            "provider_execution_pending": True,
            "note": "approval recorded; provider-specific executor can archive/delete later",
        }
        self._store("archive_decisions", decision)
        return {"ok": True, "mode": "external_chat_cleanup_approved", "decision": decision}

    def _resolve_project(self, project_id: Optional[str]) -> str:
        if project_id:
            return project_id.strip().upper().replace("-", "_").replace(" ", "_") or "GOD_MODE"
        status = operator_priority_service.get_status()
        return status.get("active_project") or "GOD_MODE"

    def _store(self, key: str, item: Dict[str, Any]) -> None:
        def mutate(state: Dict[str, Any]) -> Dict[str, Any]:
            state.setdefault(key, [])
            state[key].append(item)
            state[key] = state[key][-200:]
            return state
        CLEANUP_STORE.update(mutate)

    def latest(self) -> Dict[str, Any]:
        state = CLEANUP_STORE.load()
        return {
            "ok": True,
            "mode": "external_chat_cleanup_latest",
            "latest_inventory": (state.get("inventories") or [None])[-1],
            "latest_extraction": (state.get("memory_extractions") or [None])[-1],
            "latest_plan": (state.get("cleanup_plans") or [None])[-1],
            "latest_decision": (state.get("archive_decisions") or [None])[-1],
            "inventory_count": len(state.get("inventories") or []),
            "extraction_count": len(state.get("memory_extractions") or []),
            "plan_count": len(state.get("cleanup_plans") or []),
            "decision_count": len(state.get("archive_decisions") or []),
        }

    def panel(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "mode": "external_chat_cleanup_panel",
            "headline": "Limpeza segura de conversas externas",
            "policy": self.policy(),
            "latest": self.latest(),
            "safe_buttons": [
                {"id": "inventory", "label": "Inventariar conversas", "endpoint": "/api/external-chat-cleanup/inventory", "priority": "critical"},
                {"id": "extract", "label": "Extrair memória", "endpoint": "/api/external-chat-cleanup/extract-memory", "priority": "critical"},
                {"id": "plan", "label": "Plano de limpeza", "endpoint": "/api/external-chat-cleanup/plan", "priority": "critical"},
                {"id": "latest", "label": "Último estado", "endpoint": "/api/external-chat-cleanup/latest", "priority": "high"},
            ],
        }

    def get_status(self) -> Dict[str, Any]:
        latest = self.latest()
        return {
            "ok": True,
            "mode": "external_chat_cleanup_status",
            "inventory_count": latest.get("inventory_count", 0),
            "extraction_count": latest.get("extraction_count", 0),
            "plan_count": latest.get("plan_count", 0),
            "decision_count": latest.get("decision_count", 0),
            "execution_is_gated": True,
        }

    def get_package(self) -> Dict[str, Any]:
        return {"ok": True, "mode": "external_chat_cleanup_package", "package": {"status": self.get_status(), "panel": self.panel(), "latest": self.latest()}}


external_chat_cleanup_archive_service = ExternalChatCleanupArchiveService()
