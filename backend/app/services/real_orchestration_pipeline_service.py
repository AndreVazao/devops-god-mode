from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class RealOrchestrationPipelineService:
    """Connects God Mode planning, roles, security, provider routing and tool validation.

    This is the first real connected orchestration layer. It does not execute
    destructive actions. It builds an executable-safe action queue with gates.
    """

    def status(self) -> dict[str, Any]:
        return {
            "ok": True,
            "service": "real_orchestration_pipeline",
            "created_at": _utc_now(),
            "mode": "connected_pipeline_v1",
            "execution_policy": "safe_queue_only_no_destructive_auto_execution",
            "pipeline": [
                "goal_planner",
                "agent_roles",
                "ai_handoff_security_guard",
                "ai_provider_router",
                "mcp_compatibility",
                "execution_gates",
                "safe_action_queue",
            ],
        }

    def panel(self) -> dict[str, Any]:
        return {
            **self.status(),
            "headline": "Orquestração Real v1",
            "description": "Liga Goal Planner, Papéis IA, Security Guard, Provider Router e MCP Tools numa fila de execução segura.",
            "primary_actions": [
                {"label": "Criar pipeline", "endpoint": "/api/real-orchestration/run", "method": "POST", "safe": True},
                {"label": "Simular execução", "endpoint": "/api/real-orchestration/simulate", "method": "POST", "safe": True},
                {"label": "Política", "endpoint": "/api/real-orchestration/policy", "method": "GET", "safe": True},
            ],
            "rules": self.rules(),
        }

    def rules(self) -> list[str]:
        return [
            "Todo pedido entra primeiro no Goal Planner.",
            "Papéis internos são atribuídos antes de criar fila de execução.",
            "Contexto passa pelo Security Guard antes de provider externo/local.",
            "Provider Router escolhe IA principal e fallback.",
            "MCP Compatibility valida tools antes de as pôr na fila.",
            "Ações low podem ficar prontas para execução segura.",
            "Ações medium exigem gates de segurança quando houver contexto sensível.",
            "Ações high/critical exigem aprovação explícita do Oner.",
            "Esta versão cria fila segura; não executa ações destrutivas sozinha.",
        ]

    def policy(self) -> dict[str, Any]:
        return {
            "ok": True,
            "approval_levels": {
                "auto_safe": "Leitura, planeamento, classificação, validação e preparação sem alteração destrutiva.",
                "operator_confirm": "PR, merge, release, alterações persistentes ou sync técnico.",
                "oner_required": "Ações destrutivas, credenciais, licenças, pagamentos, eliminação, alterações críticas.",
            },
            "default_mode": "safe_queue",
            "not_yet_enabled": [
                "execução automática de commits sem gate",
                "merge automático sem aprovação",
                "envio real para providers externos",
                "alterações destrutivas",
            ],
        }

    def run(
        self,
        goal: str,
        project: str | None = None,
        repo: str | None = None,
        context: str | None = None,
        priority: str = "normal",
        sensitive: bool = False,
        needs_code: bool = False,
        needs_large_context: bool = False,
        needs_multimodal: bool = False,
        preferred_provider: str | None = None,
        execution_mode: str = "safe_queue",
        operator_approved: bool = False,
    ) -> dict[str, Any]:
        pipeline_id = f"pipe-{uuid4().hex[:10]}"
        goal_plan = self._goal_plan(goal, project, repo, context, priority, execution_mode)
        tags = goal_plan.get("classification", {}).get("tags", [])
        assigned_roles = self._assign_roles(goal, tags, goal_plan.get("project"), goal_plan.get("repo"), context)
        security_package = self._security_prepare(goal, context, preferred_provider, goal_plan.get("project"), goal_plan.get("repo"))
        route = self._provider_route(
            goal=goal,
            tags=tags,
            context=context,
            sensitive=sensitive or security_package.get("handoff_security_package", {}).get("risk_level") in {"high", "critical"},
            needs_code=needs_code or "code_generation" in tags or "feature" in tags or "bugfix" in tags,
            needs_large_context=needs_large_context,
            needs_multimodal=needs_multimodal,
            preferred_provider=preferred_provider,
        )
        tool_plan = self._tool_plan(goal_plan=goal_plan, roles=assigned_roles, route=route, operator_approved=operator_approved)
        gates = self._execution_gates(goal_plan, assigned_roles, security_package, route, tool_plan, operator_approved)
        queue = self._safe_action_queue(goal_plan, assigned_roles, security_package, route, tool_plan, gates)
        return {
            "ok": True,
            "pipeline_id": pipeline_id,
            "created_at": _utc_now(),
            "goal": goal,
            "project": goal_plan.get("project"),
            "repo": goal_plan.get("repo"),
            "priority": priority,
            "execution_mode": execution_mode,
            "goal_plan": goal_plan,
            "agent_roles": assigned_roles,
            "security_package": security_package,
            "provider_route": route,
            "mcp_tool_plan": tool_plan,
            "execution_gates": gates,
            "safe_action_queue": queue,
            "ready_to_execute_safe_steps": [item for item in queue if item.get("status") == "ready"],
            "blocked_steps": [item for item in queue if item.get("status") == "blocked"],
            "operator_summary": self._summary(queue, gates, route),
        }

    def simulate(self, **kwargs: Any) -> dict[str, Any]:
        result = self.run(**kwargs)
        result["simulation"] = True
        result["note"] = "Simulação: nenhuma ação externa foi executada."
        return result

    def _goal_plan(self, goal: str, project: str | None, repo: str | None, context: str | None, priority: str, execution_mode: str) -> dict[str, Any]:
        try:
            from app.services.goal_planner_service import goal_planner_service

            return goal_planner_service.create_plan(
                goal=goal,
                project=project,
                repo=repo,
                context=context,
                priority=priority,
                execution_mode="safe_autopilot" if execution_mode != "plan_only" else "plan_only",
                constraints=["validar gates", "não executar destrutivo sem aprovação"],
            )
        except Exception as exc:
            return {"ok": False, "error_type": exc.__class__.__name__, "detail": str(exc)[:240], "project": project, "repo": repo, "classification": {"tags": ["general_execution"]}}

    def _assign_roles(self, goal: str, tags: list[str], project: str | None, repo: str | None, context: str | None) -> dict[str, Any]:
        try:
            from app.services.agent_roles_registry_service import agent_roles_registry_service

            return agent_roles_registry_service.execution_plan(goal=goal, tags=tags, project=project, repo=repo, context=context)
        except Exception as exc:
            return {"ok": False, "error_type": exc.__class__.__name__, "detail": str(exc)[:240], "steps": []}

    def _security_prepare(self, goal: str, context: str | None, provider: str | None, project: str | None, repo: str | None) -> dict[str, Any]:
        try:
            from app.services.ai_handoff_security_guard_service import ai_handoff_security_guard_service

            text = f"GOAL:\n{goal}\n\nCONTEXT:\n{context or ''}"
            return ai_handoff_security_guard_service.prepare_package(
                text=text,
                provider=provider,
                purpose="real_orchestration_pipeline",
                project=project,
                repo=repo,
                include_original=False,
            )
        except Exception as exc:
            return {"ok": False, "error_type": exc.__class__.__name__, "detail": str(exc)[:240], "handoff_security_package": {"risk_level": "unknown", "safe_to_send_external": False}}

    def _provider_route(
        self,
        goal: str,
        tags: list[str],
        context: str | None,
        sensitive: bool,
        needs_code: bool,
        needs_large_context: bool,
        needs_multimodal: bool,
        preferred_provider: str | None,
    ) -> dict[str, Any]:
        try:
            from app.services.ai_provider_router_service import ai_provider_router_service

            return ai_provider_router_service.route(
                goal=goal,
                task_tags=tags,
                context=context,
                sensitive=sensitive,
                needs_code=needs_code,
                needs_large_context=needs_large_context,
                needs_multimodal=needs_multimodal,
                primary_failed=False,
                provider_availability={},
                preferred_provider=preferred_provider,
            )
        except Exception as exc:
            return {"ok": False, "error_type": exc.__class__.__name__, "detail": str(exc)[:240], "selected_provider": None, "fallback_chain": []}

    def _tool_plan(self, goal_plan: dict[str, Any], roles: dict[str, Any], route: dict[str, Any], operator_approved: bool) -> dict[str, Any]:
        tool_ids = [
            "godmode.goal_planner.plan",
            "godmode.agent_roles.assign",
            "godmode.security.prepare_ai_handoff",
            "godmode.provider_router.route",
        ]
        if goal_plan.get("classification", {}).get("needs_reusable_search"):
            tool_ids.append("godmode.reusable_code.search")
        if goal_plan.get("repo"):
            tool_ids.append("godmode.home.health")
            tool_ids.append("godmode.release.final_readiness")
        try:
            from app.services.mcp_compatibility_map_service import mcp_compatibility_map_service

            validations = []
            for tool_id in tool_ids:
                validations.append(
                    mcp_compatibility_map_service.validate_tool_call(
                        tool_id=tool_id,
                        payload={"goal_id": goal_plan.get("goal_id"), "repo": goal_plan.get("repo")},
                        operator_approved=operator_approved,
                    )
                )
            return {"ok": True, "tool_ids": tool_ids, "validations": validations}
        except Exception as exc:
            return {"ok": False, "error_type": exc.__class__.__name__, "detail": str(exc)[:240], "tool_ids": tool_ids, "validations": []}

    def _execution_gates(
        self,
        goal_plan: dict[str, Any],
        roles: dict[str, Any],
        security: dict[str, Any],
        route: dict[str, Any],
        tool_plan: dict[str, Any],
        operator_approved: bool,
    ) -> dict[str, Any]:
        gates: list[dict[str, Any]] = []
        security_pack = security.get("handoff_security_package", {})
        risk = security_pack.get("risk_level", "unknown")
        if risk in {"high", "critical", "unknown"}:
            gates.append({"gate": "security_review", "status": "passed" if security_pack.get("safe_to_send_external") and risk != "critical" else "blocked", "reason": f"security risk {risk}"})
        if route.get("selected_provider") and route.get("selected_provider", {}).get("kind") != "local_ai":
            gates.append({"gate": "external_ai_handoff_trace", "status": "required", "reason": "external provider selected"})
        if goal_plan.get("classification", {}).get("destructive_risk"):
            gates.append({"gate": "oner_approval", "status": "passed" if operator_approved else "blocked", "reason": "destructive risk"})
        for validation in tool_plan.get("validations", []):
            for blocker in validation.get("blockers", []):
                gates.append({"gate": f"mcp_{validation.get('tool_id')}", "status": "blocked" if blocker != "security_guard_required_before_execution" else "required", "reason": blocker})
        return {
            "ok": True,
            "operator_approved": operator_approved,
            "gate_count": len(gates),
            "blocked_count": len([gate for gate in gates if gate.get("status") == "blocked"]),
            "required_count": len([gate for gate in gates if gate.get("status") == "required"]),
            "gates": gates,
        }

    def _safe_action_queue(
        self,
        goal_plan: dict[str, Any],
        roles: dict[str, Any],
        security: dict[str, Any],
        route: dict[str, Any],
        tool_plan: dict[str, Any],
        gates: dict[str, Any],
    ) -> list[dict[str, Any]]:
        queue: list[dict[str, Any]] = []
        blocked = gates.get("blocked_count", 0) > 0
        queue.append({
            "id": "Q1",
            "title": "Criar/confirmar plano do objetivo",
            "source": "goal_planner",
            "status": "ready",
            "risk": "low",
            "tool": "godmode.goal_planner.plan",
        })
        queue.append({
            "id": "Q2",
            "title": "Atribuir papéis internos",
            "source": "agent_roles",
            "status": "ready",
            "risk": "low",
            "tool": "godmode.agent_roles.assign",
        })
        queue.append({
            "id": "Q3",
            "title": "Usar contexto sanitizado para handoff IA",
            "source": "ai_handoff_security_guard",
            "status": "ready" if not blocked else "blocked",
            "risk": security.get("handoff_security_package", {}).get("risk_level", "unknown"),
            "tool": "godmode.security.prepare_ai_handoff",
        })
        queue.append({
            "id": "Q4",
            "title": "Selecionar provider IA e fallback",
            "source": "ai_provider_router",
            "status": "ready" if route.get("selected_provider") else "blocked",
            "risk": "low",
            "tool": "godmode.provider_router.route",
            "selected_provider": route.get("selected_provider", {}).get("provider_id") if route.get("selected_provider") else None,
        })
        if goal_plan.get("classification", {}).get("needs_reusable_search"):
            queue.append({
                "id": "Q5",
                "title": "Pesquisar código reutilizável antes de pedir código novo",
                "source": "reusable_code_registry",
                "status": "ready",
                "risk": "low",
                "tool": "godmode.reusable_code.search",
            })
        if goal_plan.get("repo"):
            queue.append({
                "id": "Q6",
                "title": "Preparar branch/PR, mas não fazer merge sem aprovação",
                "source": "github_gate",
                "status": "requires_approval",
                "risk": "high",
                "repo": goal_plan.get("repo"),
            })
        return queue

    def _summary(self, queue: list[dict[str, Any]], gates: dict[str, Any], route: dict[str, Any]) -> str:
        ready = len([item for item in queue if item.get("status") == "ready"])
        blocked = len([item for item in queue if item.get("status") == "blocked"])
        approval = len([item for item in queue if item.get("status") == "requires_approval"])
        provider = route.get("selected_provider", {}).get("provider_id") if route.get("selected_provider") else "nenhum"
        return f"Pipeline real criado: {ready} pronto(s), {blocked} bloqueado(s), {approval} com aprovação. Provider: {provider}. Gates bloqueados: {gates.get('blocked_count', 0)}."

    def package(self) -> dict[str, Any]:
        return {"status": self.status(), "panel": self.panel(), "rules": self.rules(), "policy": self.policy()}


real_orchestration_pipeline_service = RealOrchestrationPipelineService()
