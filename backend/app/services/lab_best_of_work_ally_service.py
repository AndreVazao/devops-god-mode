from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List

from app.services.praison_research_adapter_service import praison_research_adapter_service
from app.services.ruflo_research_lab_service import ruflo_research_lab_service


class LabBestOfWorkAllyService:
    """Operationalize the best Ruflo/Praison research patterns natively in God Mode.

    Ruflo and Praison remain research labs/references. This service turns their
    strongest patterns into God Mode-native decision rules for Andre's daily work.
    """

    SERVICE_ID = "lab_best_of_work_ally"
    VERSION = "phase_183_v1"

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def status(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "service": self.SERVICE_ID,
            "version": self.VERSION,
            "generated_at": self._now(),
            "god_mode_is_orchestrator": True,
            "ruflo_is_lab_dependency": False,
            "praison_is_lab_dependency": False,
            "implementation_policy": "native_first_reference_only",
            "phase_workflow_policy": "only_current_phase_smoke_workflow_kept",
            "package_endpoint": "/api/lab-best-of-work-ally/package",
        }

    def best_patterns(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "patterns": [
                {
                    "id": "goal_first_work_planning",
                    "source": "ruflo",
                    "source_area": "goal planner / GOAP",
                    "native_target": "goal_planner + real_orchestration_pipeline",
                    "priority": "critical",
                    "why_for_andre": "Transforma um pedido curto no telemóvel em objetivo, plano, ações, validações e PR/build.",
                    "already_present": ["goal_planner", "real_orchestration_pipeline", "execution_modes_engine"],
                    "next_native_upgrade": "Goal-to-approved-work package com contexto, riscos e botões mobile.",
                },
                {
                    "id": "manager_worker_swarms",
                    "source": "ruflo+praison",
                    "source_area": "swarm coordination + hierarchical process",
                    "native_target": "agent_roles_registry + orchestration_playbooks",
                    "priority": "critical",
                    "why_for_andre": "O PC pensa como equipa: manager, investigador, programador, validador, documentador, release guard.",
                    "already_present": ["agent_roles_registry", "orchestration_playbooks", "provider_router"],
                    "next_native_upgrade": "Role assignment automático por tipo de trabalho e risco.",
                },
                {
                    "id": "playbook_as_business_process",
                    "source": "praison",
                    "source_area": "YAML agent playbooks / sequential workflow / conditional workflow",
                    "native_target": "playbook_templates_library + pipeline_persistence_executor",
                    "priority": "critical",
                    "why_for_andre": "Permite repetir processos reais: criar repo, corrigir app, publicar site, validar build, atualizar memória.",
                    "already_present": ["playbook_templates_library", "pipeline_persistence_executor"],
                    "next_native_upgrade": "Templates por negócio/projeto: God Mode, Barbudo Studio, ProVentil, VerbaForge.",
                },
                {
                    "id": "local_knowledge_before_code",
                    "source": "ruflo+praison",
                    "source_area": "memory/vector/RAG/custom knowledge",
                    "native_target": "local_knowledge_rag_decision + reusable_code_registry + andreos_memory",
                    "priority": "critical",
                    "why_for_andre": "Antes de criar código novo, procurar tree, módulos existentes, docs, memória e exemplos aproveitáveis.",
                    "already_present": ["local_knowledge_rag_decision", "module_registry_snapshot", "project_tree_autorefresh"],
                    "next_native_upgrade": "Reuse-first obrigatório para qualquer fase nova.",
                },
                {
                    "id": "provider_router_with_outcome_learning",
                    "source": "ruflo+praison",
                    "source_area": "provider routing / model catalog / Ollama",
                    "native_target": "ai_provider_router + provider_outcome_learning + ollama_local_brain_adapter",
                    "priority": "high",
                    "why_for_andre": "Escolher a melhor IA por tipo de tarefa e aprender com sucesso/falha, usando local quando fizer sentido.",
                    "already_present": ["ai_provider_router", "provider_outcome_learning", "ollama_local_brain_adapter"],
                    "next_native_upgrade": "Score por tarefa: código, UI, build, docs, debug, estratégia, voz/drive mode.",
                },
                {
                    "id": "security_guard_every_handoff",
                    "source": "ruflo",
                    "source_area": "security guardrails / AIDefence",
                    "native_target": "ai_handoff_security_guard + local_encrypted_vault_contract",
                    "priority": "critical",
                    "why_for_andre": "O God Mode pode usar várias IAs sem mandar tokens, passwords, cookies ou segredos crus.",
                    "already_present": ["ai_handoff_security_guard", "local_encrypted_vault_contract", "memory_boundary"],
                    "next_native_upgrade": "Guard obrigatório antes de provider/browser/deploy handoff.",
                },
                {
                    "id": "operator_friendly_no_code_mode",
                    "source": "praison",
                    "source_area": "no-code/auto mode",
                    "native_target": "home_app_control_surface + mobile_approval_cockpit + driving_mode_voice_first",
                    "priority": "high",
                    "why_for_andre": "André trabalha na rua; precisa de botões, estados e aprovações simples no telemóvel.",
                    "already_present": ["home_app_control_surface", "mobile_approval_cockpit_v2", "driving_mode_voice_first"],
                    "next_native_upgrade": "Comandos rápidos: avançar fase, validar build, importar env, atualizar memória, abrir proof.",
                },
                {
                    "id": "sandboxed_code_interpreter_future",
                    "source": "praison",
                    "source_area": "code interpreter agents",
                    "native_target": "safe_local_execution_sandbox_future",
                    "priority": "future_gated",
                    "why_for_andre": "Muito poderoso para análise/correção, mas só entra com sandbox, rollback e aprovação.",
                    "already_present": ["low_risk_executor", "write_verify_rollback"],
                    "next_native_upgrade": "Sandbox local isolada, sem acesso a segredos por defeito.",
                },
                {
                    "id": "multi_machine_federation_future",
                    "source": "ruflo",
                    "source_area": "federation entre agentes/máquinas",
                    "native_target": "remote_brain_linkage + local_pc_runtime_orchestrator",
                    "priority": "future",
                    "why_for_andre": "Quando houver vários PCs/servidores, cada máquina pode ser worker do God Mode.",
                    "already_present": ["remote_brain_linkage", "local_pc_runtime_orchestrator"],
                    "next_native_upgrade": "Depois do PC principal estar provado em produção.",
                },
            ],
        }

    def work_ally_operating_rules(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "rules": [
                {
                    "id": "one_command_to_plan",
                    "rule": "Todo pedido do Oner vira primeiro goal package: objetivo, contexto, riscos, artefacts esperados e aprovação necessária.",
                },
                {
                    "id": "reuse_first",
                    "rule": "Antes de criar ficheiro/módulo novo, consultar tree oficial, module registry, AndreOS memory e reusable code registry.",
                },
                {
                    "id": "native_first_labs_reference_only",
                    "rule": "Ruflo/Praison inspiram padrões; God Mode implementa nativamente salvo decisão explícita.",
                },
                {
                    "id": "mobile_first_operator",
                    "rule": "Todos os fluxos críticos têm estado simples para telemóvel: pronto, atenção, bloqueado, aprovado, em execução, concluído.",
                },
                {
                    "id": "pc_brain_mobile_approval",
                    "rule": "PC executa trabalho pesado; telemóvel aprova segredos, merges, releases, deploys e ações destrutivas.",
                },
                {
                    "id": "secret_guard_always",
                    "rule": "Nenhum segredo cru entra em GitHub, AndreOS, Obsidian cloud, logs ou contexto de IA externa.",
                },
                {
                    "id": "phase_workflow_hygiene",
                    "rule": "Quando uma fase avança, apagar workflows smoke de fases antigas e manter só o workflow da fase corrente + workflows globais.",
                },
            ],
        }

    def command_to_work_plan(self, command: str = "Avança") -> Dict[str, Any]:
        command_clean = (command or "Avança").strip()[:1200]
        return {
            "ok": True,
            "mode": "lab_best_of_command_to_work_plan",
            "input_command": command_clean,
            "plan": [
                {"step": 1, "pattern": "goal_first_work_planning", "action": "Converter comando em objetivo e fase pequena validável."},
                {"step": 2, "pattern": "local_knowledge_before_code", "action": "Consultar tree/registry/memória para evitar duplicar módulos."},
                {"step": 3, "pattern": "manager_worker_swarms", "action": "Atribuir papéis: planner, coder, validator, documenter, release guard."},
                {"step": 4, "pattern": "playbook_as_business_process", "action": "Escolher template: patch, build, memory sync, install proof, vault/env."},
                {"step": 5, "pattern": "security_guard_every_handoff", "action": "Redigir segredos e bloquear ações de risco sem aprovação."},
                {"step": 6, "pattern": "provider_router_with_outcome_learning", "action": "Escolher provider/execução local mais adequado e registar resultado."},
                {"step": 7, "pattern": "mobile_first_operator", "action": "Mostrar card simples no cockpit para aprovar/acompanhar."},
                {"step": 8, "pattern": "phase_workflow_hygiene", "action": "Manter só workflow smoke da fase corrente após validação."},
            ],
            "risk_gates": ["secrets", "merge", "release", "deploy", "payments", "licenses", "destructive_actions"],
        }

    def workflow_hygiene_policy(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "policy": {
                "keep": [
                    ".github/workflows/phase183-lab-best-of-work-ally-smoke.yml",
                    ".github/workflows/universal-total-test.yml",
                    ".github/workflows/android-real-build-progressive.yml",
                    ".github/workflows/windows-exe-real-build.yml",
                    ".github/workflows/prune-old-artifacts-all-repos.yml",
                    ".github/workflows/project-tree-autorefresh.yml",
                ],
                "delete_previous_phase_smokes": True,
                "reason": "Evita acumular smokes rígidos de fases antigas e reduz ruído nos PRs.",
            },
        }

    def source_lab_snapshot(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "ruflo": {
                "repo": "AndreVazao/godmode-ruflo-lab",
                "summary": ruflo_research_lab_service.mapping(),
            },
            "praison": {
                "repo": "AndreVazao/godmode-praison-lab",
                "summary": praison_research_adapter_service.mapping(),
            },
        }

    def package(self) -> Dict[str, Any]:
        return {
            "status": self.status(),
            "best_patterns": self.best_patterns(),
            "work_ally_operating_rules": self.work_ally_operating_rules(),
            "default_command_plan": self.command_to_work_plan("Avança"),
            "workflow_hygiene_policy": self.workflow_hygiene_policy(),
            "source_lab_snapshot": self.source_lab_snapshot(),
        }


lab_best_of_work_ally_service = LabBestOfWorkAllyService()
