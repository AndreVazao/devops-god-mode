from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from typing import Any


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


BASE_GATES = [
    "goal_planner",
    "agent_roles",
    "security_guard",
    "provider_router",
    "mcp_validation",
    "operator_approval_for_high_risk",
]


PLAYBOOK_TEMPLATES: dict[str, dict[str, Any]] = {
    "godmode_feature_safe": {
        "version": "godmode.playbook.v1",
        "name": "godmode-feature-safe",
        "title": "Nova feature segura no God Mode",
        "description": "Criar ou melhorar feature com planeamento, reusable code, segurança, PR e validação.",
        "project": "GOD_MODE",
        "repo": "AndreVazao/devops-god-mode",
        "mode": "sequential",
        "priority": "high",
        "sensitive": False,
        "needs_code": True,
        "needs_large_context": False,
        "needs_multimodal": False,
        "preferred_provider": "chatgpt",
        "operator_approved": False,
        "goals": [
            {
                "id": "feature_plan",
                "goal": "Implementar uma feature segura no God Mode com testes e documentação.",
                "context": "Usar Goal Planner, Agent Roles, Reusable Code Registry, Security Guard e build checks.",
                "constraints": ["não fazer merge sem checks", "não executar destrutivo", "atualizar docs"],
            }
        ],
        "gates": BASE_GATES,
        "tags": ["feature", "code_generation", "build_release"],
    },
    "bugfix_release": {
        "version": "godmode.playbook.v1",
        "name": "bugfix-release-flow",
        "title": "Bugfix + release validation",
        "description": "Corrigir bug, validar Universal/Android/Windows e preparar PR/release.",
        "project": "GOD_MODE",
        "repo": "AndreVazao/devops-god-mode",
        "mode": "sequential",
        "priority": "critical",
        "sensitive": False,
        "needs_code": True,
        "needs_large_context": False,
        "needs_multimodal": False,
        "preferred_provider": "chatgpt",
        "operator_approved": False,
        "goals": [
            {
                "id": "bugfix",
                "goal": "Corrigir bug, validar build e preparar PR seguro.",
                "context": "Erro vindo de workflow, PC, APK, EXE, endpoint ou UI.",
                "constraints": ["validar smoke test", "não fazer merge sem checks", "documentar correção"],
            }
        ],
        "gates": BASE_GATES,
        "tags": ["bugfix", "debugging", "build_release"],
    },
    "external_repo_research": {
        "version": "godmode.playbook.v1",
        "name": "external-repo-research",
        "title": "Research de repo externo",
        "description": "Analisar repo externo como Ruflo/Praison sem acoplar dependência central.",
        "project": "GOD_MODE",
        "repo": "AndreVazao/devops-god-mode",
        "mode": "workflow",
        "priority": "high",
        "sensitive": False,
        "needs_code": False,
        "needs_large_context": True,
        "needs_multimodal": False,
        "preferred_provider": "chatgpt",
        "operator_approved": False,
        "goals": [
            {
                "id": "research",
                "goal": "Estudar repo externo e criar mapeamento de padrões úteis para o God Mode.",
                "context": "Clonar apenas em laboratório privado quando fizer sentido. Preferir implementação nativa.",
                "constraints": ["respeitar licença", "não adicionar dependência central", "registar reusable patterns"],
            }
        ],
        "gates": BASE_GATES,
        "tags": ["research", "architecture", "ai_orchestration"],
    },
    "apk_exe_validation": {
        "version": "godmode.playbook.v1",
        "name": "apk-exe-validation",
        "title": "Validação APK/EXE",
        "description": "Validar APK, EXE, artifacts, smoke test e readiness antes do André instalar.",
        "project": "GOD_MODE",
        "repo": "AndreVazao/devops-god-mode",
        "mode": "sequential",
        "priority": "critical",
        "sensitive": False,
        "needs_code": False,
        "needs_large_context": False,
        "needs_multimodal": False,
        "preferred_provider": "chatgpt",
        "operator_approved": False,
        "goals": [
            {
                "id": "validate_artifacts",
                "goal": "Validar APK, EXE, smoke test e links de artifacts para instalação segura.",
                "context": "Usar workflows Android APK Build, Windows EXE Build, Boot smoke test desktop backend e Artifact validation.",
                "constraints": ["não pedir instalação antes de smoke test", "gerar relatório curto"],
            }
        ],
        "gates": BASE_GATES,
        "tags": ["build_release", "mobile", "desktop", "test"],
    },
    "memory_sync_runtime": {
        "version": "godmode.playbook.v1",
        "name": "memory-sync-runtime",
        "title": "Sync memória God Mode",
        "description": "Atualizar AndreOS GitHub memory e preparar nota Obsidian local madura.",
        "project": "GOD_MODE",
        "repo": "AndreVazao/andreos-memory",
        "mode": "sequential",
        "priority": "high",
        "sensitive": False,
        "needs_code": False,
        "needs_large_context": False,
        "needs_multimodal": False,
        "preferred_provider": "ollama",
        "operator_approved": False,
        "goals": [
            {
                "id": "sync_memory",
                "goal": "Atualizar memória técnica estável do God Mode no AndreOS e preparar notas Obsidian locais se aplicável.",
                "context": "GitHub memory guarda decisões técnicas, histórico, última sessão e backlog. Obsidian é oficina local/evolução.",
                "constraints": ["não guardar tokens", "não guardar passwords", "separar GitHub memory de Obsidian local"],
            }
        ],
        "gates": BASE_GATES,
        "tags": ["memory", "obsidian", "andreos"],
    },
    "provider_fallback_code": {
        "version": "godmode.playbook.v1",
        "name": "provider-fallback-code",
        "title": "Fallback de provider para código",
        "description": "Quando provider principal falha/recusa/não conclui, escolher fallback e manter trace seguro.",
        "project": "GOD_MODE",
        "repo": "AndreVazao/devops-god-mode",
        "mode": "prompt_chain",
        "priority": "high",
        "sensitive": False,
        "needs_code": True,
        "needs_large_context": False,
        "needs_multimodal": False,
        "preferred_provider": "deepseek",
        "operator_approved": False,
        "goals": [
            {
                "id": "fallback",
                "goal": "Usar Provider Router para escolher fallback quando o provider principal não concluir código.",
                "context": "ChatGPT default; DeepSeek fallback forte para código; Gemini/Grok cross-check; Ollama para sensível/local.",
                "constraints": ["passar pelo Security Guard", "criar AI Handoff Trace", "não enviar segredos"],
            }
        ],
        "gates": BASE_GATES,
        "tags": ["ai_orchestration", "code_generation", "fallback_when_primary_refuses"],
    },
    "approved_github_patch": {
        "version": "godmode.playbook.v1",
        "name": "approved-github-patch",
        "title": "Patch GitHub com aprovação",
        "description": "Preparar alteração de ficheiros, branch e PR apenas com aprovação explícita.",
        "project": "GOD_MODE",
        "repo": "AndreVazao/devops-god-mode",
        "mode": "workflow",
        "priority": "critical",
        "sensitive": False,
        "needs_code": True,
        "needs_large_context": False,
        "needs_multimodal": False,
        "preferred_provider": "chatgpt",
        "operator_approved": False,
        "goals": [
            {
                "id": "prepare_patch",
                "goal": "Preparar patch GitHub com branch, commits e PR, mas só executar alterações persistentes com aprovação.",
                "context": "Usar gates high-risk para alterações de repo. Não fazer merge automático.",
                "constraints": ["exigir aprovação", "validar checks", "não fazer merge automático"],
            }
        ],
        "gates": BASE_GATES,
        "tags": ["github", "feature", "security"],
    },
    "local_pc_diagnostics": {
        "version": "godmode.playbook.v1",
        "name": "local-pc-diagnostics",
        "title": "Diagnóstico local do PC",
        "description": "Verificar PC, backend, portas, health, ferramentas e estado local sem alterar nada perigoso.",
        "project": "GOD_MODE",
        "repo": "AndreVazao/devops-god-mode",
        "mode": "parallel_safe",
        "priority": "high",
        "sensitive": True,
        "needs_code": False,
        "needs_large_context": False,
        "needs_multimodal": False,
        "preferred_provider": "ollama",
        "operator_approved": False,
        "goals": [
            {
                "id": "diagnose_pc",
                "goal": "Diagnosticar estado local do PC, backend, health, firewall/portas e ferramentas instaladas.",
                "context": "Executar apenas checks locais seguros. Não desinstalar, não apagar, não alterar sistema sem confirmação.",
                "constraints": ["somente leitura", "não alterar Windows", "não enviar dados sensíveis a IA externa"],
            }
        ],
        "gates": BASE_GATES,
        "tags": ["desktop", "diagnostics", "security", "private_context"],
    },
}


class PlaybookTemplatesLibraryService:
    """Curated reusable playbook templates for God Mode."""

    def status(self) -> dict[str, Any]:
        return {
            "ok": True,
            "service": "playbook_templates_library",
            "created_at": _utc_now(),
            "template_count": len(PLAYBOOK_TEMPLATES),
            "version": "godmode.playbook.templates.v1",
        }

    def panel(self) -> dict[str, Any]:
        return {
            **self.status(),
            "headline": "Playbook Templates Library",
            "description": "Biblioteca de receitas reutilizáveis para o God Mode executar fluxos repetíveis sem depender de conversas longas.",
            "primary_actions": [
                {"label": "Listar templates", "endpoint": "/api/playbook-templates/templates", "method": "GET", "safe": True},
                {"label": "Obter template", "endpoint": "/api/playbook-templates/templates/{template_id}", "method": "GET", "safe": True},
                {"label": "Criar pipeline", "endpoint": "/api/playbook-templates/to-pipeline", "method": "POST", "safe": True},
            ],
            "rules": self.rules(),
        }

    def rules(self) -> list[str]:
        return [
            "Templates são receitas reutilizáveis, não execução destrutiva.",
            "Cada template gera playbook compatível com Orchestration Playbooks v1.",
            "operator_approved=false por defeito.",
            "Templates de GitHub/release/memória persistente continuam a exigir gates.",
            "Contexto sensível deve preferir Ollama/local e Security Guard.",
        ]

    def templates(self, tag: str | None = None, project: str | None = None) -> dict[str, Any]:
        items = {}
        for template_id, template in PLAYBOOK_TEMPLATES.items():
            if tag and tag not in template.get("tags", []):
                continue
            if project and template.get("project") != project:
                continue
            items[template_id] = self._summary(template_id, template)
        return {"ok": True, "count": len(items), "templates": items}

    def get_template(self, template_id: str, overrides: dict[str, Any] | None = None) -> dict[str, Any]:
        template = PLAYBOOK_TEMPLATES.get(template_id)
        if not template:
            return {"ok": False, "error_type": "template_not_found", "template_id": template_id, "available": list(PLAYBOOK_TEMPLATES.keys())}
        playbook = deepcopy(template)
        if overrides:
            playbook = self._apply_overrides(playbook, overrides)
        return {"ok": True, "template_id": template_id, "playbook": playbook}

    def to_pipeline(self, template_id: str, overrides: dict[str, Any] | None = None, goal_id: str | None = None, operator_approved: bool = False) -> dict[str, Any]:
        got = self.get_template(template_id=template_id, overrides=overrides)
        if not got.get("ok"):
            return got
        try:
            from app.services.orchestration_playbook_service import orchestration_playbook_service

            return orchestration_playbook_service.to_pipeline_request(
                playbook=got["playbook"],
                goal_id=goal_id,
                operator_approved=operator_approved,
            )
        except Exception as exc:
            return {"ok": False, "error_type": exc.__class__.__name__, "detail": str(exc)[:240], "template_id": template_id}

    def run_template(self, template_id: str, overrides: dict[str, Any] | None = None, goal_id: str | None = None, operator_approved: bool = False, simulate: bool = True) -> dict[str, Any]:
        got = self.get_template(template_id=template_id, overrides=overrides)
        if not got.get("ok"):
            return got
        try:
            from app.services.orchestration_playbook_service import orchestration_playbook_service

            return orchestration_playbook_service.run(
                playbook=got["playbook"],
                goal_id=goal_id,
                operator_approved=operator_approved,
                simulate=simulate,
            )
        except Exception as exc:
            return {"ok": False, "error_type": exc.__class__.__name__, "detail": str(exc)[:240], "template_id": template_id}

    def _apply_overrides(self, playbook: dict[str, Any], overrides: dict[str, Any]) -> dict[str, Any]:
        allowed_top_level = {
            "name",
            "description",
            "project",
            "repo",
            "mode",
            "priority",
            "sensitive",
            "needs_code",
            "needs_large_context",
            "needs_multimodal",
            "preferred_provider",
            "operator_approved",
            "gates",
            "tags",
        }
        for key, value in overrides.items():
            if key in allowed_top_level:
                playbook[key] = value
        if "goal" in overrides or "context" in overrides or "constraints" in overrides:
            goals = playbook.setdefault("goals", [{}])
            if not goals:
                goals.append({"id": "goal_main"})
            if "goal" in overrides:
                goals[0]["goal"] = overrides["goal"]
            if "context" in overrides:
                goals[0]["context"] = overrides["context"]
            if "constraints" in overrides:
                goals[0]["constraints"] = overrides["constraints"]
        return playbook

    def _summary(self, template_id: str, template: dict[str, Any]) -> dict[str, Any]:
        return {
            "template_id": template_id,
            "name": template.get("name"),
            "title": template.get("title"),
            "description": template.get("description"),
            "project": template.get("project"),
            "repo": template.get("repo"),
            "mode": template.get("mode"),
            "priority": template.get("priority"),
            "preferred_provider": template.get("preferred_provider"),
            "tags": template.get("tags", []),
        }

    def package(self) -> dict[str, Any]:
        return {"status": self.status(), "panel": self.panel(), "rules": self.rules(), "templates": self.templates(limit=None) if False else self.templates()}


playbook_templates_library_service = PlaybookTemplatesLibraryService()
