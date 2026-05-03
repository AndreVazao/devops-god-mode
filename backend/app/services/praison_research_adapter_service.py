from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class PraisonResearchAdapterService:
    """Tracks Praison as a research source for native God Mode improvements."""

    def status(self) -> dict[str, Any]:
        return {
            "ok": True,
            "service": "praison_research_adapter",
            "created_at": _utc_now(),
            "upstream_repo": "PraisonLabs/Praison",
            "upstream_url": "https://github.com/PraisonLabs/Praison",
            "upstream_license": "MIT",
            "recommended_lab_repo": "AndreVazao/godmode-praison-lab",
            "lab_repo_status": "not_created_yet",
            "role": "external_research_source",
            "dependency_policy": "do_not_add_as_core_dependency_without_dedicated_lab_and_tests",
        }

    def panel(self) -> dict[str, Any]:
        return {
            **self.status(),
            "headline": "Praison Research Adapter",
            "description": "Regista Praison como fonte de pesquisa para workflows multi-agent, YAML playbooks, RAG/memória, Ollama e processos agentic.",
            "primary_actions": [
                {"label": "Ver mapeamento", "endpoint": "/api/praison-research/mapping", "method": "GET", "safe": True},
                {"label": "Plano de extração", "endpoint": "/api/praison-research/extraction-plan", "method": "GET", "safe": True},
                {"label": "Política", "endpoint": "/api/praison-research/policy", "method": "GET", "safe": True},
            ],
            "rules": self.rules(),
        }

    def rules(self) -> list[str]:
        return [
            "Praison é fonte de pesquisa, não dependência central do God Mode.",
            "Não copiar código para o God Mode sem laboratório, licença MIT e análise.",
            "Aproveitar padrões: YAML playbooks, workflows, routing, memória/RAG, agents, tools e Ollama.",
            "Preferir implementação nativa no God Mode quando o padrão for simples.",
            "Criar repo privado godmode-praison-lab se for clonar o upstream completo.",
            "Registrar qualquer padrão útil no Reusable Code Registry antes de implementação.",
        ]

    def policy(self) -> dict[str, Any]:
        return {
            "ok": True,
            "decision": "worth_tracking_but_not_core_dependency_yet",
            "clone_recommendation": "yes_as_private_lab_repo_only",
            "recommended_repo": "AndreVazao/godmode-praison-lab",
            "why_not_core_dependency_now": [
                "God Mode já tem arquitetura nativa própria.",
                "Adicionar framework multi-agent completo pode aumentar dependências e complexidade.",
                "O valor principal para já é aprender padrões e adaptar seletivamente.",
                "O PC atual pode ser fraco para stacks pesadas com múltiplos agentes e RAG.",
            ],
            "safe_usage": [
                "usar como laboratório de pesquisa",
                "extrair YAML playbook patterns",
                "comparar workflows multi-agent com Real Orchestration Pipeline",
                "mapear integração Ollama/local",
                "avaliar RAG/memória antes de integrar",
            ],
        }

    def mapping(self) -> dict[str, Any]:
        return {
            "ok": True,
            "mapping": [
                {
                    "praison_area": "YAML agent playbooks",
                    "god_mode_target": "orchestration_playbook_format",
                    "priority": "critical",
                    "implementation": "native_yaml_schema",
                    "reason": "Permite André criar/editar workflows sem mexer em código.",
                },
                {
                    "praison_area": "Sequential / hierarchical / workflow / parallel processes",
                    "god_mode_target": "real_orchestration_pipeline_v2",
                    "priority": "critical",
                    "implementation": "native_execution_modes",
                    "reason": "Completa a pipeline real com modos de execução claros.",
                },
                {
                    "praison_area": "Agents with short and long term memory",
                    "god_mode_target": "andreos_obsidian_memory_retrieval",
                    "priority": "high",
                    "implementation": "hybrid",
                    "reason": "Apoia memória persistente local/GitHub/Obsidian.",
                },
                {
                    "praison_area": "RAG agents / custom knowledge",
                    "god_mode_target": "project_knowledge_retrieval",
                    "priority": "high",
                    "implementation": "adapter_or_native_index",
                    "reason": "Útil para repos, PDFs, docs, conversas antigas e reusable code.",
                },
                {
                    "praison_area": "100+ LLM support",
                    "god_mode_target": "ai_provider_router_expansion",
                    "priority": "medium",
                    "implementation": "provider_catalog_extension",
                    "reason": "Expande Provider Router sem acoplamento direto.",
                },
                {
                    "praison_area": "Ollama integration",
                    "god_mode_target": "ollama_local_brain_adapter",
                    "priority": "high",
                    "implementation": "native_local_provider_rules",
                    "reason": "Apoia uso privado/local no PC.",
                },
                {
                    "praison_area": "Code interpreter agents",
                    "god_mode_target": "safe_local_execution_sandbox_future",
                    "priority": "future_high_risk",
                    "implementation": "gated_sandbox_only",
                    "reason": "Poderoso, mas exige sandbox e permissões fortes.",
                },
                {
                    "praison_area": "No-code/auto mode",
                    "god_mode_target": "operator_friendly_autopilot_commands",
                    "priority": "medium",
                    "implementation": "ui_and_command_shortcuts",
                    "reason": "Facilita uso enquanto o André está no telemóvel/condução.",
                },
            ],
        }

    def extraction_plan(self) -> dict[str, Any]:
        return {
            "ok": True,
            "plan": [
                {
                    "phase": "163A",
                    "name": "Track Praison research source",
                    "status": "implemented",
                    "outputs": ["research adapter", "mapping", "policy", "extraction plan"],
                },
                {
                    "phase": "163B",
                    "name": "Optional Praison Lab Repo",
                    "status": "waiting_for_repo",
                    "outputs": ["godmode-praison-lab", "sync workflow", "upstream mirror branch"],
                },
                {
                    "phase": "164",
                    "name": "Orchestration Playbooks v1",
                    "status": "recommended_next",
                    "outputs": ["YAML/JSON playbook schema", "playbook validator", "playbook-to-pipeline converter"],
                },
                {
                    "phase": "165",
                    "name": "Pipeline Execution Modes",
                    "status": "next_candidate",
                    "outputs": ["sequential", "hierarchical", "parallel", "evaluator_optimizer", "prompt_chain"],
                },
                {
                    "phase": "166",
                    "name": "RAG/Knowledge Retrieval Decision",
                    "status": "future_candidate",
                    "outputs": ["local index policy", "Obsidian/GitHub memory retrieval", "PDF/repo retrieval rules"],
                },
            ],
        }

    def package(self) -> dict[str, Any]:
        return {
            "status": self.status(),
            "panel": self.panel(),
            "rules": self.rules(),
            "policy": self.policy(),
            "mapping": self.mapping(),
            "extraction_plan": self.extraction_plan(),
        }


praison_research_adapter_service = PraisonResearchAdapterService()
