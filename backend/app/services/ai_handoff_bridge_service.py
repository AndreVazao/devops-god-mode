from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List
from uuid import uuid4

from app.services.learning_router_service import learning_router_service
from app.services.memory_core_service import memory_core_service
from app.services.mobile_approval_cockpit_v2_service import mobile_approval_cockpit_v2_service
from app.utils.atomic_json_store import AtomicJsonStore

DATA_DIR = Path("data")
AI_HANDOFF_FILE = DATA_DIR / "ai_handoff_bridge.json"
AI_HANDOFF_STORE = AtomicJsonStore(
    AI_HANDOFF_FILE,
    default_factory=lambda: {"handoffs": [], "provider_drafts": [], "resolved": []},
)

SUPPORTED_PROVIDERS = ["chatgpt", "gemini", "claude", "grok", "deepseek"]
PROVIDER_WEB_TARGETS = {
    "chatgpt": "https://chatgpt.com/",
    "gemini": "https://gemini.google.com/",
    "claude": "https://claude.ai/",
    "grok": "https://x.com/i/grok",
    "deepseek": "https://chat.deepseek.com/",
}


class AIHandoffBridgeService:
    """Approval-gated bridge for messages the Learning Router cannot understand.

    This service does not control a browser directly. It prepares provider-ready
    prompts, creates approval cards, stores handoff state and lets the operator
    paste back the external AI answer. The final resolution can then teach the
    Learning Router safely.
    """

    def get_status(self) -> Dict[str, Any]:
        store = self._load_store()
        return {
            "ok": True,
            "mode": "ai_handoff_bridge_status",
            "status": "ai_handoff_bridge_ready",
            "store_file": str(AI_HANDOFF_FILE),
            "atomic_store_enabled": True,
            "supported_providers": SUPPORTED_PROVIDERS,
            "handoff_count": len(store.get("handoffs", [])),
            "resolved_count": len(store.get("resolved", [])),
        }

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def _normalize_store(self, store: Dict[str, Any]) -> Dict[str, Any]:
        if not isinstance(store, dict):
            return {"handoffs": [], "provider_drafts": [], "resolved": []}
        store.setdefault("handoffs", [])
        store.setdefault("provider_drafts", [])
        store.setdefault("resolved", [])
        return store

    def _load_store(self) -> Dict[str, Any]:
        return self._normalize_store(AI_HANDOFF_STORE.load())

    def _provider(self, provider: str) -> str:
        normalized = (provider or "chatgpt").lower().strip()
        return normalized if normalized in SUPPORTED_PROVIDERS else "chatgpt"

    def _latest_unknown(self) -> Dict[str, Any] | None:
        unknowns = learning_router_service.list_unknowns(limit=1).get("unknowns", [])
        return unknowns[-1] if unknowns else None

    def _build_external_prompt(self, unknown: Dict[str, Any], provider: str) -> str:
        project = unknown.get("project", "GOD_MODE")
        memory_core_service.initialize()
        context = memory_core_service.compact_context(project, max_chars=4500)
        return (
            "És um assistente de interpretação para o God Mode.\n"
            "O utilizador falou de forma natural e o router local não conseguiu classificar com confiança.\n"
            "Objetivo: interpretar a intenção, escolher uma ação segura e devolver JSON simples.\n\n"
            f"Provider alvo: {provider}\n"
            f"Projeto provável: {project}\n"
            f"Mensagem original: {unknown.get('message', '')}\n\n"
            "Contexto AndreOS compacto:\n"
            f"{context.get('context', '')}\n\n"
            "Responde em JSON com estas chaves:\n"
            "intent: one of continue_project, deep_audit, build_check, memory_review, fix_plan, delivery_summary, unknown\n"
            "confidence: número 0..1\n"
            "project: nome do projeto\n"
            "reason: motivo curto\n"
            "recommended_command: comando em português para enviar ao Mission Control\n"
            "learn_phrase: frase curta que o God Mode deve aprender se o operador aprovar\n"
            "needs_operator_approval: true\n"
        )

    def create_handoff_from_latest_unknown(self, provider: str = "chatgpt", tenant_id: str = "owner-andre") -> Dict[str, Any]:
        unknown = self._latest_unknown()
        if not unknown:
            return {"ok": False, "error": "no_unknown_messages"}
        return self.create_handoff_from_unknown(unknown, provider=provider, tenant_id=tenant_id)

    def create_handoff_from_unknown(self, unknown: Dict[str, Any], provider: str = "chatgpt", tenant_id: str = "owner-andre") -> Dict[str, Any]:
        provider_name = self._provider(provider)
        handoff_id = f"handoff-{uuid4().hex[:12]}"
        created_at = self._now()
        prompt = self._build_external_prompt(unknown, provider_name)
        handoff = {
            "handoff_id": handoff_id,
            "tenant_id": tenant_id,
            "provider": provider_name,
            "provider_url": PROVIDER_WEB_TARGETS[provider_name],
            "created_at": created_at,
            "updated_at": created_at,
            "status": "pending_operator_copy_to_provider",
            "unknown": unknown,
            "external_prompt": prompt,
            "approval_card_id": None,
        }
        card = mobile_approval_cockpit_v2_service.create_card(
            title=f"Interpretar mensagem desconhecida no {provider_name}",
            body=f"Projeto: {unknown.get('project', 'GOD_MODE')}. Mensagem: {unknown.get('message', '')}. Aprova abrir/copiar para provider externo?",
            card_type="provider_login_request",
            project_id=str(unknown.get("project", "GOD_MODE")).lower().replace("_", "-"),
            tenant_id=tenant_id,
            priority="medium",
            requires_approval=True,
            actions=[
                {"action_id": "approve-ai-handoff", "label": "Aprovar handoff IA", "decision": "approved"},
                {"action_id": "reject-ai-handoff", "label": "Rejeitar", "decision": "rejected"},
            ],
            source_ref={"type": "ai_handoff", "handoff_id": handoff_id},
            metadata={"provider": provider_name, "provider_url": PROVIDER_WEB_TARGETS[provider_name]},
        )
        if card.get("ok"):
            handoff["approval_card_id"] = card["card"]["card_id"]

        def mutate(store: Dict[str, Any]) -> Dict[str, Any]:
            store = self._normalize_store(store)
            store["handoffs"].append(handoff)
            store["handoffs"] = store["handoffs"][-500:]
            return store

        AI_HANDOFF_STORE.update(mutate)
        memory_core_service.write_history(
            unknown.get("project", "GOD_MODE"),
            action="AI Handoff Bridge created provider prompt",
            result=f"Provider: {provider_name} | Handoff: {handoff_id}",
        )
        return {"ok": True, "mode": "ai_handoff_create", "handoff": handoff, "approval_card": card}

    def list_handoffs(self, limit: int = 50, status: str | None = None) -> Dict[str, Any]:
        store = self._load_store()
        handoffs = store.get("handoffs", [])
        if status:
            handoffs = [item for item in handoffs if item.get("status") == status]
        handoffs = handoffs[-max(min(limit, 200), 1):]
        return {"ok": True, "mode": "ai_handoff_list", "handoff_count": len(handoffs), "handoffs": handoffs}

    def get_handoff(self, handoff_id: str) -> Dict[str, Any]:
        store = self._load_store()
        handoff = next((item for item in store.get("handoffs", []) if item.get("handoff_id") == handoff_id), None)
        if not handoff:
            return {"ok": False, "error": "handoff_not_found", "handoff_id": handoff_id}
        return {"ok": True, "mode": "ai_handoff_get", "handoff": handoff}

    def resolve_handoff(
        self,
        handoff_id: str,
        provider_response: str,
        learn_phrase: str = "",
        intent: str = "unknown",
        tenant_id: str = "owner-andre",
    ) -> Dict[str, Any]:
        response = provider_response.strip()
        if not response:
            return {"ok": False, "error": "provider_response_empty"}
        store = self._load_store()
        handoff = next((item for item in store.get("handoffs", []) if item.get("handoff_id") == handoff_id), None)
        if not handoff:
            return {"ok": False, "error": "handoff_not_found", "handoff_id": handoff_id}
        project = handoff.get("unknown", {}).get("project", "GOD_MODE")
        resolved = {
            "resolution_id": f"resolution-{uuid4().hex[:12]}",
            "handoff_id": handoff_id,
            "tenant_id": tenant_id,
            "project": project,
            "provider": handoff.get("provider"),
            "provider_response": response,
            "learn_phrase": learn_phrase.strip(),
            "intent": intent,
            "created_at": self._now(),
        }
        learn_result: Dict[str, Any] | None = None
        if learn_phrase.strip() and intent != "unknown":
            learn_result = learning_router_service.learn_pattern(
                phrase=learn_phrase,
                intent=intent,
                project=project,
                tenant_id=tenant_id,
            )
        memory_history = memory_core_service.write_history(
            project,
            action="AI Handoff Bridge resolved provider response",
            result=f"Handoff: {handoff_id} | Intent: {intent} | Learned: {bool(learn_result and learn_result.get('ok'))}",
        )

        def mutate(payload: Dict[str, Any]) -> Dict[str, Any]:
            payload = self._normalize_store(payload)
            for item in payload.get("handoffs", []):
                if item.get("handoff_id") == handoff_id:
                    item["status"] = "resolved"
                    item["updated_at"] = self._now()
                    item["resolution_id"] = resolved["resolution_id"]
                    break
            payload["resolved"].append(resolved)
            payload["resolved"] = payload["resolved"][-500:]
            return payload

        AI_HANDOFF_STORE.update(mutate)
        return {"ok": True, "mode": "ai_handoff_resolve", "resolution": resolved, "learn_result": learn_result, "memory_history": memory_history}

    def build_dashboard(self) -> Dict[str, Any]:
        store = self._load_store()
        pending = [item for item in store.get("handoffs", []) if item.get("status") != "resolved"]
        return {
            "ok": True,
            "mode": "ai_handoff_dashboard",
            "handoff_count": len(store.get("handoffs", [])),
            "pending_count": len(pending),
            "resolved_count": len(store.get("resolved", [])),
            "supported_providers": SUPPORTED_PROVIDERS,
            "recent_handoffs": store.get("handoffs", [])[-30:],
            "recent_resolved": store.get("resolved", [])[-20:],
        }

    def get_package(self) -> Dict[str, Any]:
        return {"ok": True, "mode": "ai_handoff_package", "package": {"status": self.get_status(), "dashboard": self.build_dashboard()}}


ai_handoff_bridge_service = AIHandoffBridgeService()
