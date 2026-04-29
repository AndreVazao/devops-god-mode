from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import uuid4

from app.services.memory_context_router_service import memory_context_router_service
from app.services.operator_priority_service import operator_priority_service
from app.utils.atomic_json_store import AtomicJsonStore

DATA_DIR = Path("data")
COMPLETION_FILE = DATA_DIR / "provider_completion_router.json"
COMPLETION_STORE = AtomicJsonStore(
    COMPLETION_FILE,
    default_factory=lambda: {
        "version": 1,
        "policy": "deliver_working_program_with_safe_provider_continuation",
        "completion_plans": [],
        "provider_events": [],
    },
)


class ProviderCompletionRouterService:
    """Route work to completion across providers without losing the final objective.

    ChatGPT remains the main provider. If a provider hits a usage limit, lacks
    capability, loses context, fails quality, or cannot continue a permitted task,
    the router prepares a continuation plan. If the issue is a safety refusal, the
    router does not evade it; it decomposes the goal into an allowed safe path so
    the final program can still be delivered in a compliant way.
    """

    FAILURE_TYPES = [
        "usage_limit",
        "context_limit",
        "provider_unavailable",
        "quality_failure",
        "tooling_gap",
        "manual_login_required",
        "operator_approval_required",
        "safety_refusal",
        "unknown",
    ]

    PROVIDER_ORDER = [
        {"id": "chatgpt", "label": "ChatGPT", "rank": 1, "role": "primary", "language": "pt-PT"},
        {"id": "claude", "label": "Claude", "rank": 2, "role": "fallback_large_context", "language": "pt-PT"},
        {"id": "gemini", "label": "Gemini", "rank": 3, "role": "fallback_multimodal_or_research", "language": "pt-PT"},
        {"id": "perplexity", "label": "Perplexity", "rank": 4, "role": "fallback_research_sources", "language": "pt-PT"},
        {"id": "local_ai", "label": "Local AI", "rank": 5, "role": "fallback_private_or_offline", "language": "pt-PT"},
    ]

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def policy(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "mode": "provider_completion_policy",
            "primary_provider": "chatgpt",
            "default_language": "pt-PT",
            "final_objective_rule": "o programa tem de ficar pronto e funcional dentro de um caminho permitido",
            "routing_rules": [
                {
                    "id": "capacity_or_limit_fallback",
                    "label": "Se o provider principal bater limite, guardar retoma e continuar quando possível ou passar para fallback.",
                    "allowed": True,
                },
                {
                    "id": "quality_or_capability_fallback",
                    "label": "Se o provider não conseguir entregar qualidade suficiente, preparar handoff para outro provider.",
                    "allowed": True,
                },
                {
                    "id": "safety_refusal_safe_decomposition",
                    "label": "Se houver recusa de segurança, não contornar; decompor o objetivo em alternativa permitida que ainda entregue o programa funcional.",
                    "allowed": True,
                },
                {
                    "id": "operator_approval_gate",
                    "label": "Ações reais, externas ou estruturais exigem aprovação do operador antes de execução.",
                    "allowed": True,
                },
            ],
            "not_allowed": [
                "usar outro provider para contornar uma restrição de segurança válida",
                "guardar dados sensíveis na memória",
                "executar ações reais sem aprovação quando exigida",
            ],
        }

    def classify_event(
        self,
        provider_id: str = "chatgpt",
        project_id: Optional[str] = None,
        event_text: str = "",
        failure_type: str = "unknown",
        final_objective: str = "entregar programa pronto e funcional",
    ) -> Dict[str, Any]:
        clean_failure = failure_type if failure_type in self.FAILURE_TYPES else "unknown"
        project = self._resolve_project(project_id)
        event = {
            "event_id": f"provider-event-{uuid4().hex[:12]}",
            "created_at": self._now(),
            "provider_id": provider_id,
            "project_id": project,
            "failure_type": clean_failure,
            "event_text": event_text[:2000],
            "final_objective": final_objective,
            "classification": self._classification(clean_failure),
        }
        self._store_event(event)
        return {"ok": True, "mode": "provider_completion_event_classified", "event": event}

    def completion_plan(
        self,
        provider_id: str = "chatgpt",
        project_id: Optional[str] = None,
        event_text: str = "",
        failure_type: str = "unknown",
        final_objective: str = "entregar programa pronto e funcional",
    ) -> Dict[str, Any]:
        classified = self.classify_event(
            provider_id=provider_id,
            project_id=project_id,
            event_text=event_text,
            failure_type=failure_type,
            final_objective=final_objective,
        )
        event = classified.get("event") or {}
        project = event.get("project_id") or self._resolve_project(project_id)
        context_pack = memory_context_router_service.prepare_project_context(
            project_id=project,
            source=f"provider_completion_{event.get('failure_type')}",
            max_chars=10000,
        ).get("context_pack")
        next_provider = self._select_next_provider(provider_id, event.get("failure_type"))
        plan = {
            "plan_id": f"provider-completion-plan-{uuid4().hex[:12]}",
            "created_at": self._now(),
            "project_id": project,
            "source_event_id": event.get("event_id"),
            "failure_type": event.get("failure_type"),
            "current_provider": provider_id,
            "next_provider": next_provider,
            "final_objective": final_objective,
            "status": self._plan_status(event.get("failure_type")),
            "completion_strategy": self._strategy(event.get("failure_type")),
            "context_pack_id": (context_pack or {}).get("context_pack_id"),
            "resume_contract": (context_pack or {}).get("resume_contract"),
            "handoff_prompt": self._handoff_prompt(project, final_objective, event, context_pack, next_provider),
            "safe_decomposition": self._safe_decomposition(project, final_objective, event.get("failure_type")),
            "operator_next": self._operator_next(event.get("failure_type")),
        }
        self._store_plan(plan)
        return {"ok": True, "mode": "provider_completion_plan", "plan": plan}

    def _resolve_project(self, project_id: Optional[str]) -> str:
        if project_id:
            return project_id.strip().upper().replace("-", "_").replace(" ", "_") or "GOD_MODE"
        priorities = operator_priority_service.get_status()
        return priorities.get("active_project") or "GOD_MODE"

    def _classification(self, failure_type: str) -> Dict[str, Any]:
        if failure_type in {"usage_limit", "context_limit", "provider_unavailable"}:
            return {"kind": "capacity", "can_handoff": True, "needs_safe_decomposition": False}
        if failure_type in {"quality_failure", "tooling_gap"}:
            return {"kind": "capability", "can_handoff": True, "needs_safe_decomposition": False}
        if failure_type in {"manual_login_required", "operator_approval_required"}:
            return {"kind": "operator_gate", "can_handoff": False, "needs_operator": True}
        if failure_type == "safety_refusal":
            return {"kind": "safety", "can_handoff": False, "needs_safe_decomposition": True}
        return {"kind": "unknown", "can_handoff": True, "needs_safe_decomposition": True}

    def _select_next_provider(self, current_provider: str, failure_type: str) -> Dict[str, Any]:
        if failure_type == "safety_refusal":
            return {"id": current_provider, "label": current_provider, "reason": "safe_decomposition_on_same_or_any_provider_after_reframe"}
        if failure_type in {"manual_login_required", "operator_approval_required"}:
            return {"id": current_provider, "label": current_provider, "reason": "wait_for_operator_then_resume"}
        for provider in self.PROVIDER_ORDER:
            if provider["id"] != current_provider:
                return {**provider, "reason": f"fallback_after_{failure_type}"}
        return self.PROVIDER_ORDER[0]

    def _plan_status(self, failure_type: str) -> str:
        if failure_type in {"manual_login_required", "operator_approval_required"}:
            return "paused_waiting_operator"
        if failure_type == "safety_refusal":
            return "needs_safe_reframe_before_continuation"
        return "ready_for_provider_handoff"

    def _strategy(self, failure_type: str) -> List[Dict[str, Any]]:
        if failure_type == "safety_refusal":
            return [
                {"step": 1, "label": "Preservar objetivo final permitido", "type": "memory"},
                {"step": 2, "label": "Remover/alterar parte recusada", "type": "safe_reframe"},
                {"step": 3, "label": "Propor alternativa técnica permitida", "type": "architecture"},
                {"step": 4, "label": "Continuar implementação do programa funcional", "type": "delivery"},
            ]
        if failure_type in {"usage_limit", "context_limit", "provider_unavailable"}:
            return [
                {"step": 1, "label": "Guardar última sessão", "type": "memory"},
                {"step": 2, "label": "Gerar pacote compacto", "type": "context"},
                {"step": 3, "label": "Retomar no ChatGPT quando possível ou passar para fallback", "type": "handoff"},
                {"step": 4, "label": "Continuar até próximo gate", "type": "delivery"},
            ]
        return [
            {"step": 1, "label": "Guardar contexto", "type": "memory"},
            {"step": 2, "label": "Escolher provider mais adequado", "type": "routing"},
            {"step": 3, "label": "Pedir resultado completo e testável", "type": "delivery"},
            {"step": 4, "label": "Validar contra objetivo final", "type": "validation"},
        ]

    def _safe_decomposition(self, project: str, final_objective: str, failure_type: str) -> Dict[str, Any]:
        return {
            "project_id": project,
            "final_objective": final_objective,
            "rule": "manter objetivo final, substituir qualquer parte bloqueada por alternativa permitida",
            "required_output": [
                "arquitetura permitida",
                "scripts ou ficheiros funcionais dentro do permitido",
                "passos de instalação/teste",
                "gates de aprovação para ações reais",
                "registo em memória para retoma",
            ],
            "applies_strictly_when": failure_type == "safety_refusal",
        }

    def _handoff_prompt(
        self,
        project: str,
        final_objective: str,
        event: Dict[str, Any],
        context_pack: Optional[Dict[str, Any]],
        next_provider: Dict[str, Any],
    ) -> str:
        header = (context_pack or {}).get("provider_prompt_header") or memory_context_router_service.provider_prompt_header(project)
        return (
            f"{header}\n"
            f"Objetivo final: {final_objective}\n"
            f"Motivo da continuação: {event.get('failure_type')} no provider {event.get('provider_id')}.\n"
            "Tarefa: continuar até entregar programa funcional, testável e documentado.\n"
            "Se alguma parte não for permitida, propõe alternativa segura e continua a implementação permitida.\n"
            "Não percas contexto: usa o resumo compacto, a última sessão, o backlog e as decisões.\n"
            "Antes de ações reais como escrita, criação externa, build ou alteração estrutural, pedir aprovação.\n"
            f"Provider sugerido: {next_provider.get('label') or next_provider.get('id')}.\n"
        )

    def _operator_next(self, failure_type: str) -> Dict[str, Any]:
        if failure_type in {"manual_login_required", "operator_approval_required"}:
            return {"label": "Dar OK ou completar login manual", "endpoint": "/api/operator-pending-attention/panel", "route": "/app/home"}
        if failure_type == "safety_refusal":
            return {"label": "Continuar por alternativa permitida", "endpoint": "/api/provider-completion-router/plan", "route": "/app/home"}
        return {"label": "Preparar handoff para provider", "endpoint": "/api/provider-completion-router/plan", "route": "/app/home"}

    def _store_event(self, event: Dict[str, Any]) -> None:
        def mutate(state: Dict[str, Any]) -> Dict[str, Any]:
            state.setdefault("provider_events", [])
            state.setdefault("completion_plans", [])
            state["provider_events"].append(event)
            state["provider_events"] = state["provider_events"][-200:]
            return state

        COMPLETION_STORE.update(mutate)

    def _store_plan(self, plan: Dict[str, Any]) -> None:
        def mutate(state: Dict[str, Any]) -> Dict[str, Any]:
            state.setdefault("completion_plans", [])
            state.setdefault("provider_events", [])
            state["completion_plans"].append(plan)
            state["completion_plans"] = state["completion_plans"][-200:]
            return state

        COMPLETION_STORE.update(mutate)

    def latest(self) -> Dict[str, Any]:
        state = COMPLETION_STORE.load()
        events = state.get("provider_events") or []
        plans = state.get("completion_plans") or []
        return {
            "ok": True,
            "mode": "provider_completion_latest",
            "latest_event": events[-1] if events else None,
            "latest_plan": plans[-1] if plans else None,
            "event_count": len(events),
            "plan_count": len(plans),
        }

    def panel(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "mode": "provider_completion_panel",
            "headline": "Continuar até ao programa funcional",
            "policy": self.policy(),
            "providers": self.PROVIDER_ORDER,
            "failure_types": self.FAILURE_TYPES,
            "latest": self.latest(),
            "safe_buttons": [
                {"id": "policy", "label": "Política", "endpoint": "/api/provider-completion-router/policy", "priority": "high"},
                {"id": "latest", "label": "Último plano", "endpoint": "/api/provider-completion-router/latest", "priority": "high"},
                {"id": "plan", "label": "Gerar plano", "endpoint": "/api/provider-completion-router/plan", "priority": "critical"},
            ],
        }

    def get_status(self) -> Dict[str, Any]:
        latest = self.latest()
        return {
            "ok": True,
            "mode": "provider_completion_status",
            "primary_provider": "chatgpt",
            "default_language": "pt-PT",
            "event_count": latest.get("event_count", 0),
            "plan_count": latest.get("plan_count", 0),
            "latest_status": ((latest.get("latest_plan") or {}).get("status") or "ready"),
        }

    def get_package(self) -> Dict[str, Any]:
        return {"ok": True, "mode": "provider_completion_package", "package": {"status": self.get_status(), "panel": self.panel()}}


provider_completion_router_service = ProviderCompletionRouterService()
