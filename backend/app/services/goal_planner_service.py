from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class GoalPlannerService:
    """Native God Mode planner: goal -> structured executable plan."""

    def status(self) -> dict[str, Any]:
        return {
            "ok": True,
            "service": "goal_planner",
            "created_at": _utc_now(),
            "mode": "native_god_mode_goal_planner",
            "inspired_by": "Ruflo research lab goal planner / swarm orchestration ideas",
            "dependency_policy": "no_runtime_dependency_on_ruflo",
        }

    def panel(self) -> dict[str, Any]:
        return {
            **self.status(),
            "headline": "Goal Planner God Mode",
            "description": "Transforma pedidos em planos executáveis: objetivo, projeto, repo, tarefas, riscos, memória, reusable code e validação.",
            "primary_actions": [
                {"label": "Criar plano", "endpoint": "/api/goal-planner/plan", "method": "POST", "safe": True},
                {"label": "Template", "endpoint": "/api/goal-planner/template", "method": "GET", "safe": True},
                {"label": "Política", "endpoint": "/api/goal-planner/policy", "method": "GET", "safe": True},
            ],
            "rules": self.rules(),
        }

    def rules(self) -> list[str]:
        return [
            "Todo objetivo longo deve virar plano antes de execução.",
            "O plano deve indicar projeto, repo, memória, tarefas, riscos, validações e próximo passo seguro.",
            "Antes de pedir código novo a IA, pesquisar Reusable Code Registry.",
            "Antes de mexer em repo, confirmar branch/PR alvo.",
            "Antes de enviar contexto a IA externa, filtrar segredos e usar AI Handoff Trace.",
            "Ações destrutivas exigem confirmação explícita do Oner.",
        ]

    def template(self) -> dict[str, Any]:
        return {
            "ok": True,
            "request_template": {
                "goal": "Descreve o objetivo final.",
                "project": "GOD_MODE",
                "repo": "AndreVazao/devops-god-mode",
                "context": "Contexto atual, limitações, erros ou screenshots.",
                "priority": "normal | high | critical",
                "execution_mode": "plan_only | safe_autopilot | needs_approval",
                "constraints": ["não apagar dados", "preservar memória", "validar build"],
            },
        }

    def policy(self) -> dict[str, Any]:
        return {
            "ok": True,
            "policy": {
                "planner_role": "converter pedidos humanos em planos executáveis pelo God Mode",
                "planner_does_not": [
                    "não executa ações destrutivas sozinho",
                    "não envia segredos para IA externa",
                    "não inventa estado técnico não confirmado",
                    "não substitui testes reais/builds",
                ],
                "planner_outputs": [
                    "goal_id",
                    "classification",
                    "memory_plan",
                    "reusable_code_check",
                    "tasks",
                    "risks",
                    "validation_plan",
                    "next_safe_action",
                ],
            },
        }

    def create_plan(
        self,
        goal: str,
        project: str | None = None,
        repo: str | None = None,
        context: str | None = None,
        priority: str = "normal",
        execution_mode: str = "safe_autopilot",
        constraints: list[str] | None = None,
    ) -> dict[str, Any]:
        clean_goal = goal.strip()
        clean_context = (context or "").strip()
        project_name = project or self._infer_project(clean_goal, clean_context)
        repo_name = repo or self._infer_repo(project_name)
        goal_id = f"goal-{uuid4().hex[:10]}"
        classification = self._classify_goal(clean_goal, clean_context, project_name, repo_name)
        memory_plan = self._memory_plan(classification, project_name)
        reusable_check = self._reusable_code_check(clean_goal, clean_context, classification)
        tasks = self._tasks(classification, repo_name, constraints or [])
        risks = self._risks(classification, execution_mode)
        blockers = self._blockers(clean_goal, clean_context, classification, constraints or [])
        validation = self._validation_plan(classification, repo_name)
        next_action = self._next_safe_action(tasks, blockers, execution_mode)
        return {
            "ok": True,
            "goal_id": goal_id,
            "created_at": _utc_now(),
            "goal": clean_goal,
            "project": project_name,
            "repo": repo_name,
            "priority": priority,
            "execution_mode": execution_mode,
            "classification": classification,
            "memory_plan": memory_plan,
            "reusable_code_check": reusable_check,
            "tasks": tasks,
            "risks": risks,
            "blockers": blockers,
            "validation_plan": validation,
            "next_safe_action": next_action,
            "operator_summary": self._operator_summary(project_name, repo_name, classification, tasks, blockers, next_action),
        }

    def _infer_project(self, goal: str, context: str) -> str:
        text = f"{goal}\n{context}".lower()
        known = {
            "god mode": "GOD_MODE",
            "ruflo": "GOD_MODE",
            "baribudos": "BARIBUDOS_STUDIO",
            "verbaforge": "VERBAFORGE",
            "proventil": "PROVENTIL",
            "lords": "BOT_LORDS_MOBILE",
            "ecu": "ECU_REPRO",
            "sheetpro": "SHEETPRO",
            "gcode": "CNC_CONVERTER",
            "cnc": "CNC_CONVERTER",
        }
        for marker, project in known.items():
            if marker in text:
                return project
        return "GOD_MODE"

    def _infer_repo(self, project: str) -> str | None:
        mapping = {
            "GOD_MODE": "AndreVazao/devops-god-mode",
            "BARIBUDOS_STUDIO": "AndreVazao/baribudos-studio",
            "PROVENTIL": "AndreVazao/proventil",
            "ECU_REPRO": "AndreVazao/ecu-pro-tune",
            "SHEETPRO": "AndreVazao/SheetProPrivate",
        }
        return mapping.get(project)

    def _classify_goal(self, goal: str, context: str, project: str, repo: str | None) -> dict[str, Any]:
        text = f"{goal}\n{context}".lower()
        tags: list[str] = []
        if any(word in text for word in ["bug", "erro", "falha", "crash", "não abre", "nao abre"]):
            tags.append("bugfix")
        if any(word in text for word in ["implementar", "adicionar", "criar", "nova função", "feature", "avança"]):
            tags.append("feature")
        if any(word in text for word in ["workflow", "build", "artifact", "apk", "exe", "ci"]):
            tags.append("build_release")
        if any(word in text for word in ["memória", "memoria", "obsidian", "andreos", "github memory"]):
            tags.append("memory")
        if any(word in text for word in ["ia", "provider", "chatgpt", "gemini", "deepseek", "grok", "ollama"]):
            tags.append("ai_orchestration")
        if any(word in text for word in ["segurança", "seguranca", "token", "password", "secret", "cookie"]):
            tags.append("security")
        if not tags:
            tags.append("general_execution")
        destructive = any(word in text for word in ["apagar", "delete", "limpar tudo", "remover repo", "destruir"])
        return {
            "project": project,
            "repo": repo,
            "tags": tags,
            "destructive_risk": destructive,
            "needs_branch": bool(repo),
            "needs_external_ai": "ai_orchestration" in tags or "código" in text or "codigo" in text,
            "needs_reusable_search": any(tag in tags for tag in ["feature", "bugfix", "build_release", "ai_orchestration"]),
        }

    def _memory_plan(self, classification: dict[str, Any], project: str) -> dict[str, Any]:
        return {
            "github_memory": {
                "use": True,
                "repo": "AndreVazao/andreos-memory",
                "project_path": f"AndreOS/02_PROJETOS/{project}/",
                "write_when": ["decisão técnica", "bugfix", "feature", "PR", "build", "release", "componente reutilizável"],
            },
            "obsidian_local": {
                "use": True,
                "write_when": ["rascunho", "observação local", "teste real", "prioridade", "evolução operacional"],
            },
            "reusable_registry": {
                "check_required": classification.get("needs_reusable_search", False),
                "endpoint": "/api/reusable-code-registry/search",
            },
            "ai_trace": {
                "required_if_external_ai": classification.get("needs_external_ai", False),
                "endpoint": "/api/ai-handoff-trace/panel",
            },
        }

    def _reusable_code_check(self, goal: str, context: str, classification: dict[str, Any]) -> dict[str, Any]:
        query = re.sub(r"\s+", " ", f"{goal} {context}").strip()[:220]
        return {
            "required": classification.get("needs_reusable_search", False),
            "query": query,
            "endpoint": "/api/reusable-code-registry/search",
            "rule": "pesquisar antes de pedir código novo a IA",
        }

    def _tasks(self, classification: dict[str, Any], repo: str | None, constraints: list[str]) -> list[dict[str, Any]]:
        tasks: list[dict[str, Any]] = [
            {"id": "T1", "title": "Confirmar contexto e classificação", "type": "analysis", "safe": True},
        ]
        if classification.get("needs_reusable_search"):
            tasks.append({"id": "T2", "title": "Pesquisar código reutilizável existente", "type": "reusable_code_search", "safe": True, "endpoint": "/api/reusable-code-registry/search"})
        if repo:
            tasks.append({"id": "T3", "title": "Preparar branch/PR técnico", "type": "github_workflow", "safe": True, "repo": repo})
        if classification.get("needs_external_ai"):
            tasks.append({"id": "T4", "title": "Preparar handoff seguro para IA externa", "type": "ai_handoff", "safe": True, "endpoint": "/api/ai-handoff-trace/panel"})
        tasks.append({"id": "T5", "title": "Executar alteração mínima validável", "type": "implementation", "safe": not classification.get("destructive_risk", False), "constraints": constraints})
        tasks.append({"id": "T6", "title": "Validar e registar memória", "type": "validation_memory", "safe": True})
        return tasks

    def _risks(self, classification: dict[str, Any], execution_mode: str) -> list[dict[str, Any]]:
        risks = []
        if classification.get("destructive_risk"):
            risks.append({"level": "critical", "risk": "ação destrutiva detectada", "mitigation": "exigir confirmação explícita do Oner"})
        if classification.get("needs_external_ai"):
            risks.append({"level": "high", "risk": "contexto enviado a IA externa", "mitigation": "filtrar segredos e usar trace"})
        if execution_mode == "safe_autopilot":
            risks.append({"level": "medium", "risk": "execução autónoma parcial", "mitigation": "limitar a ações seguras e PRs revisáveis"})
        if not risks:
            risks.append({"level": "low", "risk": "risco normal de implementação", "mitigation": "validar com testes e smoke checks"})
        return risks

    def _blockers(self, goal: str, context: str, classification: dict[str, Any], constraints: list[str]) -> list[dict[str, Any]]:
        blockers = []
        text = f"{goal} {context}".lower()
        if classification.get("destructive_risk"):
            blockers.append({"id": "B1", "reason": "pedido destrutivo", "needs": "confirmação explícita do Oner"})
        if "token" in text or "password" in text or "cookie" in text:
            blockers.append({"id": "B2", "reason": "possível segredo no contexto", "needs": "filtragem antes de persistir/enviar"})
        if any("sem confirmação" in item.lower() for item in constraints):
            blockers.append({"id": "B3", "reason": "constraint exige confirmação", "needs": "OK do operador"})
        return blockers

    def _validation_plan(self, classification: dict[str, Any], repo: str | None) -> dict[str, Any]:
        checks = ["universal_total_test"]
        tags = classification.get("tags", [])
        if "build_release" in tags or repo == "AndreVazao/devops-god-mode":
            checks.extend(["windows_exe_build", "boot_smoke_test", "android_apk_build_if_mobile"])
        if "memory" in tags:
            checks.append("memory_boundary_consistency")
        if "security" in tags or classification.get("needs_external_ai"):
            checks.append("secret_filter_review")
        return {"checks": checks, "must_pass_before_merge": bool(repo), "artifact_needed": "build_release" in tags}

    def _next_safe_action(self, tasks: list[dict[str, Any]], blockers: list[dict[str, Any]], execution_mode: str) -> dict[str, Any]:
        if blockers:
            return {"action": "request_operator_approval_or_cleanup", "reason": blockers[0]["reason"], "safe_to_execute_now": False}
        return {"action": "execute_next_safe_task" if execution_mode != "plan_only" else "show_plan_only", "task": tasks[0] if tasks else None, "safe_to_execute_now": execution_mode != "plan_only"}

    def _operator_summary(self, project: str, repo: str | None, classification: dict[str, Any], tasks: list[dict[str, Any]], blockers: list[dict[str, Any]], next_action: dict[str, Any]) -> str:
        blocker_text = "sem blockers" if not blockers else f"{len(blockers)} blocker(s)"
        return f"Plano criado para {project} ({repo or 'sem repo definido'}). Tags: {', '.join(classification.get('tags', []))}. Tarefas: {len(tasks)}. Estado: {blocker_text}. Próximo passo: {next_action.get('action')}."

    def package(self) -> dict[str, Any]:
        return {"status": self.status(), "panel": self.panel(), "rules": self.rules(), "template": self.template(), "policy": self.policy()}


goal_planner_service = GoalPlannerService()
