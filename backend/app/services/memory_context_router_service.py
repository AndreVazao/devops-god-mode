from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import uuid4

from app.services.memory_core_service import memory_core_service
from app.services.new_project_start_intake_service import new_project_start_intake_service
from app.services.operator_priority_service import operator_priority_service
from app.utils.atomic_json_store import AtomicJsonStore

DATA_DIR = Path("data")
ROUTER_FILE = DATA_DIR / "memory_context_router.json"
ROUTER_STORE = AtomicJsonStore(
    ROUTER_FILE,
    default_factory=lambda: {
        "version": 1,
        "policy": "obsidian_first_context_and_portuguese_primary_ai_provider",
        "context_packs": [],
        "handoffs": [],
    },
)


class MemoryContextRouterService:
    """Obsidian-first context router for existing and new projects.

    The router keeps every project anchored in AndreOS/Obsidian memory and
    prepares compact provider-ready context packs so conversations can pause,
    resume, roll over, or move to another provider without losing state.
    """

    PRIMARY_PROVIDER = {
        "id": "chatgpt",
        "label": "ChatGPT",
        "default_share": 0.80,
        "default_language": "pt-PT",
        "role": "primary_daily_provider",
    }

    FALLBACK_PROVIDERS = [
        {"id": "claude", "label": "Claude", "role": "fallback_reasoning_or_large_context"},
        {"id": "gemini", "label": "Gemini", "role": "fallback_research_or_multimodal"},
        {"id": "perplexity", "label": "Perplexity", "role": "fallback_research_with_sources"},
        {"id": "local_ai", "label": "Local AI", "role": "fallback_private_or_offline"},
    ]

    CONTEXT_FILES = [
        "MEMORIA_MESTRE.md",
        "ARQUITETURA.md",
        "DECISOES.md",
        "BACKLOG.md",
        "ROADMAP.md",
        "ULTIMA_SESSAO.md",
        "HISTORICO.md",
        "ERROS.md",
        "PROMPTS.md",
    ]

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def provider_policy(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "mode": "memory_context_provider_policy",
            "default_language": "pt-PT",
            "primary_provider": self.PRIMARY_PROVIDER,
            "fallback_providers": self.FALLBACK_PROVIDERS,
            "routing_rules": [
                {
                    "id": "primary_first",
                    "label": "Usar ChatGPT como provider principal na maioria do trabalho diário.",
                    "default": True,
                },
                {
                    "id": "pause_and_resume_on_limits",
                    "label": "Quando houver limite, pausa, grava contexto compacto e retoma mais tarde ou noutro provider.",
                    "default": True,
                },
                {
                    "id": "fallback_for_capacity_or_capability",
                    "label": "Usar providers alternativos quando o principal estiver limitado, indisponível ou não for o melhor para a tarefa.",
                    "default": True,
                },
                {
                    "id": "do_not_route_to_evade_safety",
                    "label": "Não usar outro provider para contornar bloqueios de segurança; apenas tarefas permitidas continuam noutro provider.",
                    "default": True,
                },
                {
                    "id": "portuguese_operator_context",
                    "label": "Manter instruções, resumos e handoffs em português por padrão.",
                    "default": True,
                },
            ],
        }

    def obsidian_policy(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "mode": "memory_context_obsidian_policy",
            "vault": "AndreOS",
            "project_root": "memory/vault/AndreOS/02_PROJETOS",
            "required_files": self.CONTEXT_FILES,
            "rules": [
                "Cada projeto existente ou novo deve ter pasta própria em AndreOS.",
                "A memória mestre guarda conceito, objetivo e estado geral.",
                "A arquitetura guarda decisões técnicas e módulos.",
                "O backlog guarda o que falta fazer.",
                "A última sessão guarda o ponto de retoma para qualquer provider.",
                "Histórico, erros e decisões impedem repetição de trabalho.",
                "Nunca guardar tokens, passwords, cookies, bearer, authorization, API keys ou secrets.",
            ],
        }

    def prepare_project_context(
        self,
        project_id: str,
        source: str = "existing_or_new_project",
        idea: Optional[str] = None,
        max_chars: int = 8000,
    ) -> Dict[str, Any]:
        normalized = project_id.strip().upper().replace("-", "_").replace(" ", "_") or "GOD_MODE"
        memory_core_service.create_project(normalized)
        if idea:
            memory_core_service.write_history(
                normalized,
                "Contexto inicial do projeto",
                idea,
            )
            memory_core_service.update_last_session(
                normalized,
                summary=f"Projeto preparado para trabalho contínuo. Origem: {source}.",
                next_steps="Confirmar prioridades, preparar plano seguro e só depois executar ações com gates.",
            )
        compact = memory_core_service.compact_context(normalized, max_chars=max_chars)
        links = [memory_core_service.obsidian_link(normalized, file_name=file_name) for file_name in self.CONTEXT_FILES]
        context_pack = {
            "context_pack_id": f"context-pack-{uuid4().hex[:12]}",
            "created_at": self._now(),
            "project_id": normalized,
            "source": source,
            "default_language": "pt-PT",
            "primary_provider": self.PRIMARY_PROVIDER,
            "fallback_providers": self.FALLBACK_PROVIDERS,
            "compact_context": compact,
            "obsidian_links": links,
            "resume_contract": self.resume_contract(normalized),
            "provider_prompt_header": self.provider_prompt_header(normalized),
            "secret_policy": "do_not_store_or_forward_secrets",
        }
        self._store_pack(context_pack)
        return {"ok": True, "mode": "memory_context_project_prepared", "context_pack": context_pack}

    def prepare_latest_new_project(self) -> Dict[str, Any]:
        latest = new_project_start_intake_service.latest()
        proposal = latest.get("latest_proposal") or {}
        if not proposal:
            return {"ok": False, "mode": "memory_context_latest_new_project", "error": "no_new_project_proposal"}
        idea = proposal.get("idea") or proposal.get("name") or "Projeto novo"
        project_id = proposal.get("project_id") or proposal.get("name") or "NEW_PROJECT"
        return self.prepare_project_context(
            project_id=project_id,
            source="new_project_start_intake",
            idea=idea,
            max_chars=8000,
        )

    def prepare_priority_projects(self, limit: int = 12) -> Dict[str, Any]:
        priorities = operator_priority_service.get_priorities()
        state = priorities.get("state") or {}
        projects = [item for item in state.get("projects", []) if item.get("enabled", True)]
        if not projects:
            projects = [{"project_id": "GOD_MODE", "label": "GOD_MODE"}]
        prepared = []
        for project in projects[: max(1, min(limit, 30))]:
            project_id = project.get("project_id") or project.get("label") or "GOD_MODE"
            prepared.append(self.prepare_project_context(project_id=project_id, source="operator_priority_project").get("context_pack"))
        return {
            "ok": True,
            "mode": "memory_context_priority_projects_prepared",
            "count": len(prepared),
            "context_packs": prepared,
        }

    def resume_contract(self, project_id: str) -> Dict[str, Any]:
        return {
            "project_id": project_id,
            "when_to_pause": [
                "provider conversation limit",
                "provider unavailable",
                "manual login required",
                "operator approval required",
                "network loss",
                "context too large for current provider",
            ],
            "before_pause_write": [
                "ULTIMA_SESSAO.md",
                "BACKLOG.md",
                "HISTORICO.md",
            ],
            "resume_steps": [
                "abrir contexto compacto do projeto",
                "confirmar última sessão",
                "confirmar próxima ação",
                "continuar no provider principal quando possível",
                "usar fallback apenas se for necessário e permitido",
            ],
            "do_not_store": ["tokens", "passwords", "cookies", "authorization headers", "bearer keys", "api keys", "secrets"],
        }

    def provider_prompt_header(self, project_id: str) -> str:
        return (
            f"Projeto: {project_id}\n"
            "Idioma padrão: português de Portugal.\n"
            "Objetivo: continuar sem perder contexto usando a memória AndreOS/Obsidian.\n"
            "Usa apenas o contexto compacto fornecido e pergunta por aprovação antes de escrita real, criação de repo, build, envio externo ou mudança estrutural.\n"
            "Não guardar nem pedir tokens, passwords, cookies, authorization, bearer, API keys ou secrets.\n"
            "Se houver limite de conversa, gera resumo de retoma e atualiza a última sessão.\n"
        )

    def handoff_plan(self, project_id: str, from_provider: str = "chatgpt", reason: str = "limit_or_capacity") -> Dict[str, Any]:
        prepared = self.prepare_project_context(project_id=project_id, source=f"handoff_from_{from_provider}")
        pack = prepared.get("context_pack") or {}
        handoff = {
            "handoff_id": f"provider-handoff-{uuid4().hex[:12]}",
            "created_at": self._now(),
            "project_id": pack.get("project_id") or project_id,
            "from_provider": from_provider,
            "preferred_next_provider": "chatgpt" if reason not in {"limit_or_capacity", "unavailable"} else "best_available_fallback",
            "reason": reason,
            "allowed": True,
            "not_allowed_for": ["contornar bloqueios de segurança", "expor secrets", "ações sem aprovação"],
            "context_pack_id": pack.get("context_pack_id"),
            "resume_contract": pack.get("resume_contract"),
            "prompt_header": pack.get("provider_prompt_header"),
        }
        self._store_handoff(handoff)
        return {"ok": True, "mode": "memory_context_handoff_plan", "handoff": handoff}

    def _store_pack(self, pack: Dict[str, Any]) -> None:
        def mutate(state: Dict[str, Any]) -> Dict[str, Any]:
            state.setdefault("version", 1)
            state.setdefault("policy", "obsidian_first_context_and_portuguese_primary_ai_provider")
            state.setdefault("context_packs", [])
            state.setdefault("handoffs", [])
            state["context_packs"].append(pack)
            state["context_packs"] = state["context_packs"][-200:]
            return state

        ROUTER_STORE.update(mutate)

    def _store_handoff(self, handoff: Dict[str, Any]) -> None:
        def mutate(state: Dict[str, Any]) -> Dict[str, Any]:
            state.setdefault("handoffs", [])
            state["handoffs"].append(handoff)
            state["handoffs"] = state["handoffs"][-200:]
            return state

        ROUTER_STORE.update(mutate)

    def latest(self) -> Dict[str, Any]:
        state = ROUTER_STORE.load()
        packs = state.get("context_packs") or []
        handoffs = state.get("handoffs") or []
        return {
            "ok": True,
            "mode": "memory_context_router_latest",
            "latest_context_pack": packs[-1] if packs else None,
            "latest_handoff": handoffs[-1] if handoffs else None,
            "context_pack_count": len(packs),
            "handoff_count": len(handoffs),
        }

    def panel(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "mode": "memory_context_router_panel",
            "headline": "Memória Obsidian + provider principal",
            "provider_policy": self.provider_policy(),
            "obsidian_policy": self.obsidian_policy(),
            "latest": self.latest(),
            "safe_buttons": [
                {"id": "prepare_priority_projects", "label": "Preparar memórias", "endpoint": "/api/memory-context-router/prepare-priority-projects", "priority": "critical"},
                {"id": "prepare_latest_new_project", "label": "Preparar projeto novo", "endpoint": "/api/memory-context-router/prepare-latest-new-project", "priority": "critical"},
                {"id": "provider_policy", "label": "Política providers", "endpoint": "/api/memory-context-router/provider-policy", "priority": "high"},
                {"id": "latest", "label": "Último contexto", "endpoint": "/api/memory-context-router/latest", "priority": "high"},
            ],
        }

    def get_status(self) -> Dict[str, Any]:
        latest = self.latest()
        return {
            "ok": True,
            "mode": "memory_context_router_status",
            "primary_provider": self.PRIMARY_PROVIDER,
            "default_language": "pt-PT",
            "obsidian_ready": memory_core_service.get_status().get("ok", False),
            "context_pack_count": latest.get("context_pack_count", 0),
            "handoff_count": latest.get("handoff_count", 0),
        }

    def get_package(self) -> Dict[str, Any]:
        return {"ok": True, "mode": "memory_context_router_package", "package": {"status": self.get_status(), "panel": self.panel()}}


memory_context_router_service = MemoryContextRouterService()
