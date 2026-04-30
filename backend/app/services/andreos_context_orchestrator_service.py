from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from app.services.andreos_memory_repo_connector_service import (
    andreos_memory_repo_connector_service,
)


PROJECT_ALIASES = {
    "godmode": "GOD_MODE",
    "god_mode": "GOD_MODE",
    "god mode": "GOD_MODE",
    "proventil": "PROVENTIL",
    "verbaforge": "VERBAFORGE",
    "baribudos": "VERBAFORGE",
    "lords": "BOT_LORDS_MOBILE",
    "lords mobile": "BOT_LORDS_MOBILE",
    "bot lords": "BOT_LORDS_MOBILE",
    "ecu": "ECU_REPRO",
    "repro": "ECU_REPRO",
    "build center": "BUILD_CONTROL_CENTER",
    "build control": "BUILD_CONTROL_CENTER",
    "persona": "PERSONA_FORGE",
    "persona forge": "PERSONA_FORGE",
    "vox": "VOX",
    "bot factory": "BOT_FACTORY",
}


class AndreOSContextOrchestratorService:
    def status(self) -> dict[str, Any]:
        return {
            "ok": True,
            "service": "andreos_context_orchestrator",
            "role": "God Mode é o orquestrador principal do contexto AndreOS",
            "sources": [
                "PC/backend local",
                "Obsidian vault local",
                "AndreVazao/andreos-memory",
                "project registry",
                "AI chats/providers",
                "browser/provider execution hub",
            ],
            "external_memory_repo": "AndreVazao/andreos-memory",
            "safe_mode": True,
        }

    def panel(self) -> dict[str, Any]:
        return {
            **self.status(),
            "headline": "AndreOS Context Orchestrator",
            "description": "Camada central para o God Mode nunca perder contexto entre Obsidian, repo de memória e chats de IA.",
            "primary_actions": [
                {
                    "label": "Estado da memória AndreOS",
                    "endpoint": "/api/andreos-context-orchestrator/readiness",
                    "method": "GET",
                    "safe": True,
                },
                {
                    "label": "Contexto GOD_MODE",
                    "endpoint": "/api/andreos-context-orchestrator/context/GOD_MODE",
                    "method": "GET",
                    "safe": True,
                },
                {
                    "label": "Prompt para ChatGPT",
                    "endpoint": "/api/andreos-context-orchestrator/provider-brief/GOD_MODE?provider=chatgpt",
                    "method": "GET",
                    "safe": True,
                },
                {
                    "label": "Plano de sincronização",
                    "endpoint": "/api/andreos-context-orchestrator/sync-plan/GOD_MODE",
                    "method": "GET",
                    "safe": True,
                },
            ],
            "rules": [
                "O God Mode é a fonte operacional principal.",
                "O Obsidian/repo AndreOS são memória persistente e auditável.",
                "Os chats de IA são canais de trabalho e aconselhamento, não fonte única de verdade.",
                "Antes de pedir ajuda a uma IA, o God Mode prepara contexto compacto do projeto.",
                "Depois de uma resposta útil, o God Mode deve reconciliar e guardar decisão/resumo.",
            ],
        }

    def topology(self) -> dict[str, Any]:
        return {
            "ok": True,
            "orchestrator": "God Mode",
            "nodes": [
                {
                    "id": "god_mode_backend",
                    "label": "PC/backend God Mode",
                    "type": "executor",
                    "responsibility": "orquestra tarefas, jobs, approvals, browser/providers e repos",
                },
                {
                    "id": "obsidian_local",
                    "label": "Obsidian local",
                    "type": "human_readable_memory",
                    "responsibility": "memória navegável, editável e legível por humanos",
                },
                {
                    "id": "andreos_memory_repo",
                    "label": "AndreVazao/andreos-memory",
                    "type": "external_memory_repo",
                    "responsibility": "memória portátil, privada, versionada e partilhável com IA",
                },
                {
                    "id": "ai_chats",
                    "label": "Chats/providers de IA",
                    "type": "work_channel",
                    "responsibility": "gerar soluções, rever código, continuar conversas e obter aconselhamento",
                },
                {
                    "id": "project_repos",
                    "label": "Repos dos projetos",
                    "type": "source_of_code",
                    "responsibility": "código real, PRs, artifacts e histórico técnico",
                },
            ],
            "flows": [
                "operator_request -> God Mode -> context_pack -> provider_or_local_execution",
                "provider_response -> reconciliation -> decision_summary -> AndreOS memory",
                "project_change -> PR/build -> result_summary -> AndreOS memory",
                "Obsidian edit -> repo sync/audit -> God Mode context refresh",
            ],
        }

    def normalize_project_id(self, project_id: str | None) -> str:
        if not project_id:
            return "GOD_MODE"
        raw = project_id.strip()
        key = raw.lower().replace("-", "_").strip()
        return PROJECT_ALIASES.get(key, raw.upper().replace("-", "_"))

    async def readiness(self) -> dict[str, Any]:
        memory_status = andreos_memory_repo_connector_service.status()
        try:
            audit = await andreos_memory_repo_connector_service.audit()
        except Exception as exc:
            audit = {
                "ok": False,
                "partial": True,
                "error_type": "memory_audit_failed",
                "technical_error": exc.__class__.__name__,
            }
        blockers: list[str] = []
        warnings: list[str] = []
        if not memory_status.get("github_backend_configured"):
            warnings.append("backend_github_not_configured_locally")
        if not audit.get("ok"):
            warnings.append("memory_repo_has_missing_paths_or_is_unreachable")
        return {
            "ok": len(blockers) == 0,
            "ready_for_context_handoff": len(blockers) == 0,
            "memory_repo_status": memory_status,
            "audit_summary": {
                "ok": audit.get("ok"),
                "partial": audit.get("partial"),
                "missing_global_paths": audit.get("missing_global_paths", []),
                "missing_project_paths": audit.get("missing_project_paths", []),
                "next_action": audit.get("next_action"),
                "error_type": audit.get("error_type"),
            },
            "blockers": blockers,
            "warnings": warnings,
            "next_action": "use_context_pack_before_provider" if not blockers else "fix_blockers_first",
        }

    async def context_pack(self, project_id: str = "GOD_MODE", max_chars: int = 6000) -> dict[str, Any]:
        normalized = self.normalize_project_id(project_id)
        project = await andreos_memory_repo_connector_service.read_project(normalized)
        files = project.get("files", []) if isinstance(project, dict) else []
        selected: list[dict[str, Any]] = []
        remaining = max(max_chars, 1200)
        priority_order = [
            "MEMORIA_MESTRE.md",
            "ULTIMA_SESSAO.md",
            "DECISOES.md",
            "ARQUITETURA.md",
            "BACKLOG.md",
            "ERROS.md",
            "PROMPTS.md",
            "HISTORICO.md",
        ]
        sorted_files = sorted(
            files,
            key=lambda item: priority_order.index(item.get("path", "").split("/")[-1])
            if item.get("path", "").split("/")[-1] in priority_order
            else 99,
        )
        for item in sorted_files:
            preview = item.get("preview") or ""
            if not preview:
                continue
            take = preview[:remaining]
            selected.append(
                {
                    "path": item.get("path"),
                    "size": item.get("size"),
                    "excerpt": take,
                }
            )
            remaining -= len(take)
            if remaining <= 0:
                break
        compact_context = self._build_compact_context(normalized, selected, project)
        return {
            "ok": True,
            "project_id": normalized,
            "source": "AndreVazao/andreos-memory",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "project_status": {
                "ok": project.get("ok"),
                "partial": project.get("partial"),
                "missing_paths": project.get("missing_paths", []),
            },
            "selected_files": selected,
            "compact_context": compact_context,
            "handoff_prompt": self.provider_brief_text(normalized, compact_context, "chatgpt"),
        }

    def _build_compact_context(
        self,
        project_id: str,
        selected_files: list[dict[str, Any]],
        project_payload: dict[str, Any],
    ) -> str:
        lines = [
            f"# AndreOS Context Pack — {project_id}",
            "",
            "## Regra de orquestração",
            "O God Mode é o orquestrador. A memória AndreOS é a referência persistente. Os providers de IA ajudam, mas a decisão final volta ao God Mode.",
            "",
        ]
        missing = project_payload.get("missing_paths", [])
        if missing:
            lines.extend([
                "## Atenção",
                "Existem ficheiros de memória em falta ou ainda não auditados:",
                *[f"- {path}" for path in missing[:20]],
                "",
            ])
        for item in selected_files:
            lines.append(f"## {item.get('path')}")
            lines.append(item.get("excerpt", "").strip())
            lines.append("")
        return "\n".join(lines).strip()

    def provider_brief_text(self, project_id: str, compact_context: str, provider: str) -> str:
        provider_name = provider.strip() or "provider"
        return (
            f"Provider: {provider_name}\n"
            "Objetivo: continuar o trabalho sem perder contexto.\n\n"
            "Regras:\n"
            "- Responder em Português de Portugal.\n"
            "- Não pedir dados sensíveis.\n"
            "- Não inventar estado do projeto.\n"
            "- Se faltar informação, devolver perguntas objetivas ou plano de verificação.\n"
            "- Entregar código/decisão de forma reutilizável pelo God Mode.\n\n"
            f"Projeto: {project_id}\n\n"
            f"{compact_context}"
        )

    async def provider_brief(self, project_id: str = "GOD_MODE", provider: str = "chatgpt") -> dict[str, Any]:
        pack = await self.context_pack(project_id=project_id)
        normalized = pack["project_id"]
        prompt = self.provider_brief_text(normalized, pack["compact_context"], provider)
        return {
            "ok": True,
            "project_id": normalized,
            "provider": provider,
            "prompt": prompt,
            "source_pack_status": pack.get("project_status"),
            "use_case": "paste_or_send_to_ai_chat_before_continuing_work",
        }

    def sync_plan(self, project_id: str = "GOD_MODE") -> dict[str, Any]:
        normalized = self.normalize_project_id(project_id)
        return {
            "ok": True,
            "project_id": normalized,
            "mode": "planned_context_sync",
            "steps": [
                {
                    "id": "audit_external_memory_repo",
                    "label": "Auditar repo AndreOS externo",
                    "endpoint": "/api/andreos-memory-repo/audit",
                    "safe": True,
                },
                {
                    "id": "build_context_pack",
                    "label": "Gerar contexto compacto do projeto",
                    "endpoint": f"/api/andreos-context-orchestrator/context/{normalized}",
                    "safe": True,
                },
                {
                    "id": "handoff_to_provider",
                    "label": "Preparar prompt para ChatGPT/outro provider",
                    "endpoint": f"/api/andreos-context-orchestrator/provider-brief/{normalized}",
                    "safe": True,
                },
                {
                    "id": "reconcile_provider_answer",
                    "label": "Reconciliar resposta do provider com o plano do God Mode",
                    "target_module": "browser_response_reconciliation",
                    "safe": True,
                },
                {
                    "id": "record_memory_delta",
                    "label": "Preparar resumo/decisão para guardar na memória AndreOS",
                    "target_module": "future_memory_write_gate",
                    "safe": True,
                    "requires_approval": True,
                },
            ],
            "write_policy": "Nesta fase, o plano prepara sync. Escrita real fica atrás de gate explícito.",
        }

    def intake_policy(self) -> dict[str, Any]:
        return {
            "ok": True,
            "policy": {
                "before_provider_call": [
                    "identificar projeto",
                    "gerar context_pack AndreOS",
                    "preparar provider_brief em PT-PT",
                    "marcar job/checkpoint se for trabalho longo",
                ],
                "after_provider_response": [
                    "extrair decisão útil",
                    "validar contra repo/código real",
                    "criar patch/PR se aplicável",
                    "preparar resumo para AndreOS",
                    "não guardar dados sensíveis",
                ],
                "when_context_is_missing": [
                    "consultar repo AndreOS externo",
                    "consultar memória local/Obsidian",
                    "consultar conversas antigas se necessário",
                    "pedir OK ao operador quando houver ambiguidade crítica",
                ],
            },
        }

    async def package(self, project_id: str = "GOD_MODE") -> dict[str, Any]:
        return {
            "status": self.status(),
            "panel": self.panel(),
            "topology": self.topology(),
            "readiness": await self.readiness(),
            "context_pack": await self.context_pack(project_id),
            "sync_plan": self.sync_plan(project_id),
            "intake_policy": self.intake_policy(),
        }


andreos_context_orchestrator_service = AndreOSContextOrchestratorService()
