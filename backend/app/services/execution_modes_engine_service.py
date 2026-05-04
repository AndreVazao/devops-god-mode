from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class ExecutionModesEngineService:
    """Native execution modes inspired by Praison/Ruflo patterns.

    This service transforms a validated playbook/pipeline into an executable
    strategy plan. It does not run destructive actions. It prepares structured
    execution graphs for the pipeline store/executor.
    """

    SUPPORTED_MODES = {
        "sequential": "Executa passos por ordem, com gates entre passos.",
        "hierarchical": "Manager/worker: um manager decide ordem e delega a roles.",
        "workflow": "DAG simples com condições e dependências.",
        "prompt_chain": "Cadeia de prompts/checks com validação entre etapas.",
        "evaluator_optimizer": "Gera uma solução, avalia, cria melhoria e só avança se score passar.",
        "parallel_safe": "Agrupa passos independentes low-risk para execução paralelizável futura.",
    }

    def status(self) -> dict[str, Any]:
        return {
            "ok": True,
            "service": "execution_modes_engine",
            "created_at": _utc_now(),
            "supported_modes": list(self.SUPPORTED_MODES.keys()),
            "mode": "native_execution_strategy_builder",
            "dependency_policy": "inspired_by_praison_ruflo_no_runtime_dependency",
        }

    def panel(self) -> dict[str, Any]:
        return {
            **self.status(),
            "headline": "Execution Modes Engine v1",
            "description": "Converte playbooks/pipelines em estratégias de execução: sequential, hierarchical, workflow, prompt_chain, evaluator_optimizer e parallel_safe.",
            "primary_actions": [
                {"label": "Criar estratégia", "endpoint": "/api/execution-modes/build-strategy", "method": "POST", "safe": True},
                {"label": "Explicar modo", "endpoint": "/api/execution-modes/modes/{mode}", "method": "GET", "safe": True},
                {"label": "Simular", "endpoint": "/api/execution-modes/simulate", "method": "POST", "safe": True},
            ],
            "rules": self.rules(),
        }

    def rules(self) -> list[str]:
        return [
            "Execution Modes criam estratégia, não executam ações destrutivas.",
            "Sequential é o modo padrão e mais seguro.",
            "Hierarchical atribui manager e workers, mas ainda usa safe queue.",
            "Workflow cria dependências e gates condicionais.",
            "Prompt chain exige validação entre prompts.",
            "Evaluator optimizer exige score mínimo antes de recomendar avanço.",
            "Parallel safe apenas marca grupos paralelizáveis; execução paralela real vem depois.",
            "High/critical steps continuam dependentes de aprovação explícita do Oner.",
        ]

    def modes(self) -> dict[str, Any]:
        return {"ok": True, "modes": self.SUPPORTED_MODES}

    def get_mode(self, mode: str) -> dict[str, Any]:
        if mode not in self.SUPPORTED_MODES:
            return {"ok": False, "error_type": "unsupported_mode", "mode": mode, "supported": list(self.SUPPORTED_MODES.keys())}
        return {
            "ok": True,
            "mode": mode,
            "description": self.SUPPORTED_MODES[mode],
            "template": self._mode_template(mode),
            "safety": self._mode_safety(mode),
        }

    def build_strategy(
        self,
        mode: str,
        steps: list[dict[str, Any]] | None = None,
        playbook: dict[str, Any] | None = None,
        pipeline: dict[str, Any] | None = None,
        operator_approved: bool = False,
    ) -> dict[str, Any]:
        if mode not in self.SUPPORTED_MODES:
            return {"ok": False, "error_type": "unsupported_mode", "mode": mode, "supported": list(self.SUPPORTED_MODES.keys())}
        normalized_steps = self._normalize_steps(steps=steps, playbook=playbook, pipeline=pipeline)
        builder = {
            "sequential": self._sequential,
            "hierarchical": self._hierarchical,
            "workflow": self._workflow,
            "prompt_chain": self._prompt_chain,
            "evaluator_optimizer": self._evaluator_optimizer,
            "parallel_safe": self._parallel_safe,
        }[mode]
        strategy = builder(normalized_steps, operator_approved)
        return {
            "ok": True,
            "strategy_id": f"exec-{uuid4().hex[:10]}",
            "created_at": _utc_now(),
            "mode": mode,
            "description": self.SUPPORTED_MODES[mode],
            "step_count": len(normalized_steps),
            "operator_approved": operator_approved,
            "strategy": strategy,
            "blocked_count": len([item for item in strategy.get("nodes", []) if item.get("status") == "blocked"]),
            "approval_required_count": len([item for item in strategy.get("nodes", []) if item.get("status") == "requires_approval"]),
            "operator_summary": self._summary(mode, strategy),
        }

    def simulate(
        self,
        mode: str,
        steps: list[dict[str, Any]] | None = None,
        playbook: dict[str, Any] | None = None,
        pipeline: dict[str, Any] | None = None,
        operator_approved: bool = False,
    ) -> dict[str, Any]:
        built = self.build_strategy(
            mode=mode,
            steps=steps,
            playbook=playbook,
            pipeline=pipeline,
            operator_approved=operator_approved,
        )
        built["simulation"] = True
        built["note"] = "Simulação: nenhuma ação externa/destrutiva foi executada."
        return built

    def _normalize_steps(
        self,
        steps: list[dict[str, Any]] | None,
        playbook: dict[str, Any] | None,
        pipeline: dict[str, Any] | None,
    ) -> list[dict[str, Any]]:
        if steps:
            return [self._normalize_step(item, index) for index, item in enumerate(steps, start=1)]
        if pipeline and pipeline.get("safe_action_queue"):
            return [self._normalize_step(item, index) for index, item in enumerate(pipeline.get("safe_action_queue", []), start=1)]
        if playbook and playbook.get("goals"):
            converted = []
            for index, goal in enumerate(playbook.get("goals", []), start=1):
                converted.append(
                    {
                        "id": goal.get("id") or f"goal_{index}",
                        "title": goal.get("goal", f"Goal {index}"),
                        "source": "playbook_goal",
                        "risk": "low" if not playbook.get("sensitive") else "medium",
                        "status": "ready",
                        "depends_on": goal.get("depends_on", []),
                    }
                )
            return [self._normalize_step(item, index) for index, item in enumerate(converted, start=1)]
        return []

    def _normalize_step(self, item: dict[str, Any], index: int) -> dict[str, Any]:
        risk = item.get("risk", "low")
        status = item.get("status") or ("requires_approval" if risk in {"high", "critical"} else "ready")
        return {
            "id": item.get("id") or f"S{index}",
            "order": index,
            "title": item.get("title") or item.get("goal") or f"Step {index}",
            "source": item.get("source", "unknown"),
            "risk": risk,
            "status": status,
            "depends_on": item.get("depends_on", []),
            "role": item.get("role") or item.get("role_id"),
            "tool": item.get("tool"),
            "raw": item,
        }

    def _sequential(self, steps: list[dict[str, Any]], operator_approved: bool) -> dict[str, Any]:
        nodes = []
        previous = None
        for step in steps:
            node = self._gate_node(step, operator_approved)
            node["depends_on"] = [previous] if previous else []
            nodes.append(node)
            previous = step["id"]
        return {"type": "sequential", "nodes": nodes, "edges": self._edges(nodes), "parallel_groups": []}

    def _hierarchical(self, steps: list[dict[str, Any]], operator_approved: bool) -> dict[str, Any]:
        manager = {
            "id": "manager",
            "title": "Manager — coordenar execução e delegar workers",
            "role": "architect",
            "risk": "low",
            "status": "ready",
            "depends_on": [],
        }
        nodes = [manager]
        for step in steps:
            node = self._gate_node(step, operator_approved)
            node["depends_on"] = ["manager"] + list(node.get("depends_on", []))
            node["assigned_worker"] = step.get("role") or self._worker_for(step)
            nodes.append(node)
        return {"type": "hierarchical", "manager": manager, "nodes": nodes, "edges": self._edges(nodes), "parallel_groups": []}

    def _workflow(self, steps: list[dict[str, Any]], operator_approved: bool) -> dict[str, Any]:
        nodes = []
        known_ids = {step["id"] for step in steps}
        for step in steps:
            node = self._gate_node(step, operator_approved)
            node["depends_on"] = [dep for dep in step.get("depends_on", []) if dep in known_ids]
            node["condition"] = "all_dependencies_passed" if node["depends_on"] else "start"
            nodes.append(node)
        return {"type": "workflow", "nodes": nodes, "edges": self._edges(nodes), "parallel_groups": self._parallel_groups(nodes)}

    def _prompt_chain(self, steps: list[dict[str, Any]], operator_approved: bool) -> dict[str, Any]:
        nodes = []
        previous = None
        for step in steps:
            node = self._gate_node(step, operator_approved)
            node["depends_on"] = [previous] if previous else []
            node["validation_gate"] = "output_must_be_structured_and_traceable"
            node["handoff_required"] = step.get("source") in {"ai_provider_router", "ai_handoff_security_guard"}
            nodes.append(node)
            previous = step["id"]
        return {"type": "prompt_chain", "nodes": nodes, "edges": self._edges(nodes), "parallel_groups": []}

    def _evaluator_optimizer(self, steps: list[dict[str, Any]], operator_approved: bool) -> dict[str, Any]:
        nodes = []
        for step in steps:
            base = self._gate_node(step, operator_approved)
            generate = {**base, "id": f"{step['id']}_generate", "phase": "generate"}
            evaluate = {**base, "id": f"{step['id']}_evaluate", "phase": "evaluate", "depends_on": [generate["id"]], "score_threshold": 0.75}
            optimize = {**base, "id": f"{step['id']}_optimize", "phase": "optimize", "depends_on": [evaluate["id"]], "condition": "score_below_threshold"}
            nodes.extend([generate, evaluate, optimize])
        return {"type": "evaluator_optimizer", "nodes": nodes, "edges": self._edges(nodes), "parallel_groups": []}

    def _parallel_safe(self, steps: list[dict[str, Any]], operator_approved: bool) -> dict[str, Any]:
        nodes = [self._gate_node(step, operator_approved) for step in steps]
        safe = [node["id"] for node in nodes if node.get("risk") == "low" and node.get("status") == "ready"]
        gated = [node["id"] for node in nodes if node["id"] not in safe]
        return {
            "type": "parallel_safe",
            "nodes": nodes,
            "edges": self._edges(nodes),
            "parallel_groups": [{"id": "parallel_low_risk", "nodes": safe, "real_parallel_execution_enabled": False}],
            "gated_nodes": gated,
        }

    def _gate_node(self, step: dict[str, Any], operator_approved: bool) -> dict[str, Any]:
        node = dict(step)
        risk = node.get("risk", "low")
        if risk in {"high", "critical"} and not operator_approved:
            node["status"] = "requires_approval"
            node["gate"] = "operator_approval_required"
        elif node.get("status") == "blocked":
            node["gate"] = "blocked_upstream"
        else:
            node["status"] = node.get("status", "ready")
            node["gate"] = "passed_or_low_risk"
        return node

    def _edges(self, nodes: list[dict[str, Any]]) -> list[dict[str, str]]:
        edges = []
        for node in nodes:
            for dep in node.get("depends_on", []) or []:
                if dep:
                    edges.append({"from": dep, "to": node["id"]})
        return edges

    def _parallel_groups(self, nodes: list[dict[str, Any]]) -> list[dict[str, Any]]:
        roots = [node["id"] for node in nodes if not node.get("depends_on") and node.get("status") == "ready"]
        return [{"id": "workflow_roots", "nodes": roots, "real_parallel_execution_enabled": False}] if len(roots) > 1 else []

    def _worker_for(self, step: dict[str, Any]) -> str:
        source = step.get("source")
        if source == "goal_planner":
            return "architect"
        if source == "agent_roles":
            return "architect"
        if source == "ai_provider_router":
            return "ai_research"
        if source == "reusable_code_registry":
            return "reusable_code"
        if step.get("risk") in {"high", "critical"}:
            return "security"
        return "builder"

    def _mode_template(self, mode: str) -> dict[str, Any]:
        return {
            "mode": mode,
            "steps": [
                {"id": "S1", "title": "Planear", "source": "goal_planner", "risk": "low"},
                {"id": "S2", "title": "Atribuir roles", "source": "agent_roles", "risk": "low", "depends_on": ["S1"]},
                {"id": "S3", "title": "Validar segurança", "source": "ai_handoff_security_guard", "risk": "medium", "depends_on": ["S2"]},
            ],
        }

    def _mode_safety(self, mode: str) -> dict[str, Any]:
        return {
            "destructive_actions_enabled": False,
            "external_ai_send_enabled": False,
            "parallel_real_execution_enabled": False,
            "operator_approval_required_for_high_risk": True,
            "mode": mode,
        }

    def _summary(self, mode: str, strategy: dict[str, Any]) -> str:
        nodes = strategy.get("nodes", [])
        ready = len([node for node in nodes if node.get("status") == "ready"])
        approval = len([node for node in nodes if node.get("status") == "requires_approval"])
        blocked = len([node for node in nodes if node.get("status") == "blocked"])
        return f"Estratégia {mode}: {ready} ready, {approval} requires_approval, {blocked} blocked."

    def package(self) -> dict[str, Any]:
        return {"status": self.status(), "panel": self.panel(), "rules": self.rules(), "modes": self.modes()}


execution_modes_engine_service = ExecutionModesEngineService()
