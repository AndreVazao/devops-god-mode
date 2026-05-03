from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


PLAYBOOK_MODES = ["sequential", "hierarchical", "workflow", "prompt_chain", "evaluator_optimizer", "parallel_safe"]

DEFAULT_PLAYBOOK = {
    "version": "godmode.playbook.v1",
    "name": "godmode-safe-feature-flow",
    "description": "Playbook base para transformar um pedido em pipeline real segura.",
    "project": "GOD_MODE",
    "repo": "AndreVazao/devops-god-mode",
    "mode": "sequential",
    "priority": "normal",
    "sensitive": False,
    "needs_code": True,
    "needs_large_context": False,
    "needs_multimodal": False,
    "preferred_provider": "chatgpt",
    "operator_approved": False,
    "goals": [
        {
            "id": "goal_main",
            "goal": "Descrever aqui o objetivo principal.",
            "context": "Contexto técnico e operacional.",
            "constraints": ["não executar destrutivo sem aprovação", "validar build/testes"],
        }
    ],
    "gates": [
        "goal_planner",
        "agent_roles",
        "security_guard",
        "provider_router",
        "mcp_validation",
        "operator_approval_for_high_risk",
    ],
}


class OrchestrationPlaybookService:
    """Playbook layer inspired by Praison/Ruflo, native to God Mode."""

    def status(self) -> dict[str, Any]:
        return {
            "ok": True,
            "service": "orchestration_playbooks",
            "created_at": _utc_now(),
            "version": "godmode.playbook.v1",
            "supported_modes": PLAYBOOK_MODES,
            "inspired_by": ["Praison YAML agent playbooks", "Ruflo goal planning/orchestration"],
            "dependency_policy": "native_no_runtime_dependency_on_praison_or_ruflo",
        }

    def panel(self) -> dict[str, Any]:
        return {
            **self.status(),
            "headline": "Orchestration Playbooks v1",
            "description": "Converte playbooks JSON/YAML-like em Real Orchestration Pipeline com gates seguros.",
            "primary_actions": [
                {"label": "Template", "endpoint": "/api/orchestration-playbooks/template", "method": "GET", "safe": True},
                {"label": "Validar playbook", "endpoint": "/api/orchestration-playbooks/validate", "method": "POST", "safe": True},
                {"label": "Converter para pipeline", "endpoint": "/api/orchestration-playbooks/to-pipeline", "method": "POST", "safe": True},
                {"label": "Executar seguro", "endpoint": "/api/orchestration-playbooks/run", "method": "POST", "safe": True},
            ],
            "rules": self.rules(),
        }

    def rules(self) -> list[str]:
        return [
            "Playbooks configuram pipelines; não executam ações destrutivas sozinhos.",
            "Todo playbook deve ter version, name, mode e pelo menos um goal.",
            "Modos suportados v1: sequential, hierarchical, workflow, prompt_chain, evaluator_optimizer, parallel_safe.",
            "parallel_safe só cria planos paralelizáveis; execução paralela real fica para fase futura.",
            "high/critical gates exigem aprovação do Oner.",
            "Contexto sensível passa sempre pelo Security Guard.",
            "Playbook deve gerar pipeline_id e safe_action_queue.",
        ]

    def template(self, kind: str = "safe_feature") -> dict[str, Any]:
        if kind == "research_extraction":
            playbook = {
                **DEFAULT_PLAYBOOK,
                "name": "research-extraction-flow",
                "description": "Estudar repo/lab externo e extrair padrões úteis sem acoplar dependência.",
                "needs_code": False,
                "preferred_provider": "chatgpt",
                "goals": [
                    {
                        "id": "research",
                        "goal": "Estudar referência externa e criar plano de extração nativa para o God Mode.",
                        "context": "Usar labs Ruflo/Praison como referência; não copiar sem licença/atribuição.",
                        "constraints": ["não adicionar dependência central", "registar reusable patterns"],
                    }
                ],
            }
        elif kind == "bugfix_release":
            playbook = {
                **DEFAULT_PLAYBOOK,
                "name": "bugfix-release-flow",
                "priority": "critical",
                "mode": "sequential",
                "goals": [
                    {
                        "id": "bugfix",
                        "goal": "Corrigir bug, validar build e preparar release/artifact.",
                        "context": "Erro vindo de workflow, PC, APK ou EXE.",
                        "constraints": ["validar smoke test", "não fazer merge sem checks"],
                    }
                ],
            }
        else:
            playbook = DEFAULT_PLAYBOOK
        return {"ok": True, "kind": kind, "playbook": playbook}

    def validate(self, playbook: dict[str, Any]) -> dict[str, Any]:
        errors: list[dict[str, Any]] = []
        warnings: list[dict[str, Any]] = []
        if not isinstance(playbook, dict):
            return {"ok": False, "valid": False, "errors": [{"field": "playbook", "message": "playbook must be object"}], "warnings": []}
        required = ["version", "name", "mode", "goals"]
        for field in required:
            if field not in playbook:
                errors.append({"field": field, "message": "required"})
        mode = playbook.get("mode")
        if mode and mode not in PLAYBOOK_MODES:
            errors.append({"field": "mode", "message": f"unsupported mode {mode}", "supported": PLAYBOOK_MODES})
        goals = playbook.get("goals")
        if not isinstance(goals, list) or not goals:
            errors.append({"field": "goals", "message": "must be non-empty array"})
        else:
            for index, goal in enumerate(goals):
                if not isinstance(goal, dict):
                    errors.append({"field": f"goals[{index}]", "message": "must be object"})
                    continue
                if not goal.get("goal"):
                    errors.append({"field": f"goals[{index}].goal", "message": "required"})
                if not goal.get("id"):
                    warnings.append({"field": f"goals[{index}].id", "message": "missing id; one will be generated"})
        if playbook.get("operator_approved") is True:
            warnings.append({"field": "operator_approved", "message": "approval flag supplied in playbook; runtime caller should still control real approval"})
        if playbook.get("sensitive") is True and "security_guard" not in playbook.get("gates", []):
            warnings.append({"field": "gates", "message": "sensitive=true should include security_guard gate"})
        return {
            "ok": True,
            "valid": len(errors) == 0,
            "error_count": len(errors),
            "warning_count": len(warnings),
            "errors": errors,
            "warnings": warnings,
        }

    def to_pipeline_request(self, playbook: dict[str, Any], goal_id: str | None = None, operator_approved: bool = False) -> dict[str, Any]:
        validation = self.validate(playbook)
        if not validation.get("valid"):
            return {"ok": False, "error_type": "invalid_playbook", "validation": validation}
        selected_goal = self._select_goal(playbook, goal_id)
        if not selected_goal:
            return {"ok": False, "error_type": "goal_not_found", "goal_id": goal_id}
        request = {
            "goal": selected_goal.get("goal", ""),
            "project": playbook.get("project"),
            "repo": playbook.get("repo"),
            "context": selected_goal.get("context") or playbook.get("context"),
            "priority": playbook.get("priority", "normal"),
            "sensitive": bool(playbook.get("sensitive", False)),
            "needs_code": bool(playbook.get("needs_code", False)),
            "needs_large_context": bool(playbook.get("needs_large_context", False)),
            "needs_multimodal": bool(playbook.get("needs_multimodal", False)),
            "preferred_provider": playbook.get("preferred_provider"),
            "execution_mode": "safe_queue",
            "operator_approved": operator_approved,
        }
        return {
            "ok": True,
            "playbook_id": f"playbook-{uuid4().hex[:10]}",
            "mode": playbook.get("mode"),
            "selected_goal_id": selected_goal.get("id"),
            "validation": validation,
            "pipeline_request": request,
            "execution_strategy": self._execution_strategy(playbook),
        }

    def run(self, playbook: dict[str, Any], goal_id: str | None = None, operator_approved: bool = False, simulate: bool = False) -> dict[str, Any]:
        converted = self.to_pipeline_request(playbook=playbook, goal_id=goal_id, operator_approved=operator_approved)
        if not converted.get("ok"):
            return converted
        try:
            from app.services.real_orchestration_pipeline_service import real_orchestration_pipeline_service

            request = converted["pipeline_request"]
            pipeline = real_orchestration_pipeline_service.run(**request)
            return {
                "ok": True,
                "simulate": simulate,
                "converted": converted,
                "pipeline": pipeline,
                "operator_summary": self._summary(converted, pipeline),
            }
        except Exception as exc:
            return {
                "ok": False,
                "error_type": exc.__class__.__name__,
                "detail": str(exc)[:240],
                "converted": converted,
            }

    def _select_goal(self, playbook: dict[str, Any], goal_id: str | None) -> dict[str, Any] | None:
        goals = playbook.get("goals", [])
        if not goals:
            return None
        if not goal_id:
            return goals[0]
        for goal in goals:
            if goal.get("id") == goal_id:
                return goal
        return None

    def _execution_strategy(self, playbook: dict[str, Any]) -> dict[str, Any]:
        mode = playbook.get("mode", "sequential")
        return {
            "mode": mode,
            "real_parallel_execution_enabled": False,
            "manager_worker_enabled": mode == "hierarchical",
            "conditional_gates_enabled": mode in {"workflow", "prompt_chain", "evaluator_optimizer"},
            "safe_queue_only": True,
        }

    def _summary(self, converted: dict[str, Any], pipeline: dict[str, Any]) -> str:
        return f"Playbook convertido em pipeline {pipeline.get('pipeline_id')} no modo {converted.get('mode')}. {pipeline.get('operator_summary')}"

    def package(self) -> dict[str, Any]:
        return {
            "status": self.status(),
            "panel": self.panel(),
            "rules": self.rules(),
            "template": self.template(),
            "modes": PLAYBOOK_MODES,
        }


orchestration_playbook_service = OrchestrationPlaybookService()
