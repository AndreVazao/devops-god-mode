from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List
from uuid import uuid4

from app.services.operator_priority_service import operator_priority_service
from app.services.project_intake_priority_handoff_service import project_intake_priority_handoff_service
from app.services.unified_project_intake_orchestrator_service import unified_project_intake_orchestrator_service
from app.services.real_work_command_pipeline_service import real_work_command_pipeline_service
from app.services.mobile_approval_cockpit_v2_service import mobile_approval_cockpit_v2_service
from app.utils.atomic_json_store import AtomicJsonStore

DATA_DIR = Path("data")
PLAN_FILE = DATA_DIR / "approved_deep_execution_plan.json"
PLAN_STORE = AtomicJsonStore(
    PLAN_FILE,
    default_factory=lambda: {
        "version": 1,
        "policy": "deep_execution_requires_operator_priorities_and_approval_gates",
        "plans": [],
    },
)


class ApprovedDeepExecutionPlanService:
    """Build an approval-gated execution plan after intake priorities are confirmed.

    This layer does not execute changes by itself. It turns the confirmed intake
    and operator priority order into lanes that the real work pipeline can run
    only through explicit approval gates.
    """

    GATED_ACTION_TYPES = [
        "external_ai_prompt_send",
        "conversation_rename",
        "repo_create",
        "project_file_write",
        "code_materialization",
        "build_trigger",
        "module_merge_or_delete",
    ]

    SAFE_ACTION_TYPES = [
        "read_inventory",
        "read_project_tree",
        "read_repo_metadata",
        "read_visible_chat_snapshot",
        "summarize_findings",
        "prepare_patch_preview",
    ]

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def readiness(self, tenant_id: str = "owner-andre") -> Dict[str, Any]:
        handoff = project_intake_priority_handoff_service.get_status()
        priorities = operator_priority_service.get_priorities()
        priority_state = priorities.get("state") or {}
        active_project = priority_state.get("active_project") or "GOD_MODE"
        blocked_reasons: List[Dict[str, Any]] = []
        if not handoff.get("deep_execution_unlocked"):
            blocked_reasons.append({
                "id": "priorities_not_confirmed",
                "label": "Prioridades do intake ainda não foram confirmadas pelo operador.",
                "endpoint": "/api/project-intake-priority-handoff/review",
            })
        if not priorities.get("ok"):
            blocked_reasons.append({
                "id": "operator_priority_unavailable",
                "label": "Motor de prioridades indisponível.",
                "endpoint": "/api/operator-priority/status",
            })
        return {
            "ok": len(blocked_reasons) == 0,
            "mode": "approved_deep_execution_readiness",
            "status": "ready" if not blocked_reasons else "blocked",
            "tenant_id": tenant_id,
            "active_project": active_project,
            "handoff_status": handoff,
            "priority_state": priority_state,
            "blocked_reasons": blocked_reasons,
            "operator_next": self._operator_next(blocked_reasons),
        }

    def build_plan(self, tenant_id: str = "owner-andre", requested_project: str | None = None) -> Dict[str, Any]:
        readiness = self.readiness(tenant_id=tenant_id)
        priority_state = readiness.get("priority_state") or {}
        projects = priority_state.get("projects") or []
        active_project = requested_project or readiness.get("active_project") or priority_state.get("active_project") or "GOD_MODE"
        intake = unified_project_intake_orchestrator_service.run_safe(tenant_id=tenant_id, requested_project=active_project)
        plan_id = f"approved-deep-execution-plan-{uuid4().hex[:12]}"
        lanes = self._build_lanes(projects=projects, active_project=active_project)
        gates = self._approval_gates(active_project=active_project)
        plan = {
            "plan_id": plan_id,
            "created_at": self._now(),
            "tenant_id": tenant_id,
            "requested_project": requested_project,
            "active_project": active_project,
            "mode": "approved_deep_execution_plan",
            "status": "ready_for_gated_execution" if readiness.get("ok") else "blocked_waiting_operator_priority_confirmation",
            "readiness": readiness,
            "intake_run_id": intake.get("run_id"),
            "operator_summary": intake.get("operator_summary"),
            "lanes": lanes,
            "approval_gates": gates,
            "safe_actions_without_extra_approval": self.SAFE_ACTION_TYPES,
            "gated_actions_requiring_approval": self.GATED_ACTION_TYPES,
            "execution_rules": self.execution_rules(),
            "operator_next": self._plan_next(readiness=readiness, plan_id=plan_id),
        }
        self._store_plan(plan)
        return {"ok": readiness.get("ok", False), "mode": "approved_deep_execution_plan_result", "plan": plan}

    def execution_rules(self) -> Dict[str, Any]:
        return {
            "priority_source": "operator_priority_service",
            "execute_in_priority_order": True,
            "safe_reads_can_run_first": True,
            "writes_require_approval": True,
            "external_ai_prompt_requires_gate": True,
            "repo_creation_requires_gate": True,
            "conversation_rename_requires_gate": True,
            "delete_or_merge_modules_requires_gate": True,
            "resume_after_disconnect": True,
            "do_not_store_credentials": True,
            "money_priority_enabled": False,
        }

    def _build_lanes(self, projects: List[Dict[str, Any]], active_project: str) -> List[Dict[str, Any]]:
        enabled_projects = [p for p in projects if p.get("enabled", True)]
        if not enabled_projects:
            enabled_projects = [{"project_id": active_project, "label": active_project, "enabled": True}]
        lanes = []
        for index, project in enumerate(enabled_projects[:12], start=1):
            project_id = project.get("project_id") or project.get("id") or project.get("label") or active_project
            lanes.append({
                "lane_id": f"lane-{index}-{project_id}",
                "priority": index,
                "project_id": project_id,
                "label": project.get("label") or project_id,
                "status": "active_first" if project_id == active_project else "queued",
                "safe_first_steps": [
                    {"id": "refresh_inventory", "label": "Atualizar inventário superficial", "action_type": "read_inventory", "approval_required": False},
                    {"id": "project_tree_snapshot", "label": "Ler árvore atual do projeto/repo", "action_type": "read_project_tree", "approval_required": False},
                    {"id": "summarize_blockers", "label": "Resumir blockers e próximos passos", "action_type": "summarize_findings", "approval_required": False},
                    {"id": "prepare_patch_preview", "label": "Preparar patch preview sem escrever", "action_type": "prepare_patch_preview", "approval_required": False},
                ],
                "gated_steps": [
                    {"id": "write_patch", "label": "Escrever/alterar ficheiros", "action_type": "project_file_write", "approval_required": True},
                    {"id": "materialize_from_conversation", "label": "Materializar código vindo de conversa", "action_type": "code_materialization", "approval_required": True},
                    {"id": "trigger_build", "label": "Disparar build real", "action_type": "build_trigger", "approval_required": True},
                ],
            })
        return lanes

    def _approval_gates(self, active_project: str) -> List[Dict[str, Any]]:
        return [
            {
                "gate_id": "external_ai_prompt_send",
                "label": "Enviar prompt para IA externa",
                "requires_operator_ok": True,
                "reason": "pode expor contexto de projeto/conversa",
                "default_decision": "blocked_until_explicit_ok",
            },
            {
                "gate_id": "conversation_rename",
                "label": "Renomear/organizar conversa externa",
                "requires_operator_ok": True,
                "reason": "altera estado no provider externo",
                "default_decision": "blocked_until_explicit_ok",
            },
            {
                "gate_id": "repo_create",
                "label": "Criar repo em falta",
                "requires_operator_ok": True,
                "reason": "cria recurso GitHub",
                "default_decision": "blocked_until_explicit_ok",
            },
            {
                "gate_id": "project_file_write",
                "label": f"Escrever ficheiros do projeto {active_project}",
                "requires_operator_ok": True,
                "reason": "altera código/estado local ou repo",
                "default_decision": "blocked_until_explicit_ok",
            },
            {
                "gate_id": "module_merge_or_delete",
                "label": "Fundir/apagar módulos duplicados",
                "requires_operator_ok": True,
                "reason": "mudança estrutural potencialmente destrutiva",
                "default_decision": "blocked_until_explicit_ok",
            },
        ]

    def create_approval_cards(self, tenant_id: str = "owner-andre", requested_project: str | None = None) -> Dict[str, Any]:
        plan_result = self.build_plan(tenant_id=tenant_id, requested_project=requested_project)
        plan = plan_result.get("plan") or {}
        if not plan_result.get("ok"):
            return {
                "ok": False,
                "mode": "approved_deep_execution_cards_blocked",
                "reason": "deep_execution_not_unlocked",
                "readiness": plan.get("readiness"),
                "operator_next": plan.get("operator_next"),
            }
        created_cards = []
        for gate in plan.get("approval_gates", []):
            # Use a conservative generic card through existing cockpit if the API is available.
            try:
                card = mobile_approval_cockpit_v2_service.create_card(
                    tenant_id=tenant_id,
                    title=gate["label"],
                    summary=gate["reason"],
                    payload={"plan_id": plan.get("plan_id"), "gate": gate},
                    priority="high",
                )
                created_cards.append(card)
            except Exception as exc:
                created_cards.append({"ok": False, "gate_id": gate.get("gate_id"), "error": exc.__class__.__name__, "detail": str(exc)[:300]})
        return {
            "ok": True,
            "mode": "approved_deep_execution_approval_cards",
            "plan_id": plan.get("plan_id"),
            "created_count": len(created_cards),
            "cards": created_cards,
        }

    def submit_safe_start_command(self, tenant_id: str = "owner-andre", requested_project: str | None = None) -> Dict[str, Any]:
        plan_result = self.build_plan(tenant_id=tenant_id, requested_project=requested_project)
        plan = plan_result.get("plan") or {}
        if not plan_result.get("ok"):
            return {
                "ok": False,
                "mode": "approved_deep_execution_safe_start_blocked",
                "reason": "priorities_or_handoff_not_confirmed",
                "operator_next": plan.get("operator_next"),
                "readiness": plan.get("readiness"),
            }
        command = (
            f"Executa apenas os passos seguros de leitura e preparação do projeto {plan.get('active_project')} "
            "sem escrever ficheiros, sem criar repos, sem renomear conversas e sem enviar prompts externos. "
            "Para qualquer ação destrutiva ou externa, cria aprovação antes."
        )
        result = real_work_command_pipeline_service.run_command(
            command=command,
            tenant_id=tenant_id,
            requested_project=plan.get("active_project"),
        )
        return {"ok": True, "mode": "approved_deep_execution_safe_start", "command": command, "result": result, "plan_id": plan.get("plan_id")}

    def _store_plan(self, plan: Dict[str, Any]) -> None:
        def mutate(state: Dict[str, Any]) -> Dict[str, Any]:
            state.setdefault("version", 1)
            state.setdefault("policy", "deep_execution_requires_operator_priorities_and_approval_gates")
            state.setdefault("plans", [])
            state["plans"].append(plan)
            state["plans"] = state["plans"][-100:]
            return state

        PLAN_STORE.update(mutate)

    def _operator_next(self, blocked_reasons: List[Dict[str, Any]]) -> Dict[str, Any]:
        if blocked_reasons:
            return {"label": "Confirmar prioridades primeiro", "endpoint": "/api/project-intake-priority-handoff/review", "route": "/app/home"}
        return {"label": "Gerar plano de execução aprovado", "endpoint": "/api/approved-deep-execution/plan", "route": "/app/home"}

    def _plan_next(self, readiness: Dict[str, Any], plan_id: str) -> Dict[str, Any]:
        if not readiness.get("ok"):
            return readiness.get("operator_next") or self._operator_next(readiness.get("blocked_reasons", []))
        return {"label": "Começar passos seguros", "endpoint": "/api/approved-deep-execution/start-safe", "route": "/app/home", "plan_id": plan_id}

    def latest(self) -> Dict[str, Any]:
        state = PLAN_STORE.load()
        plans = state.get("plans") or []
        return {"ok": True, "mode": "approved_deep_execution_latest", "latest_plan": plans[-1] if plans else None, "plan_count": len(plans)}

    def get_status(self) -> Dict[str, Any]:
        ready = self.readiness()
        latest = self.latest()
        return {
            "ok": True,
            "mode": "approved_deep_execution_status",
            "status": "ready" if ready.get("ok") else "blocked",
            "readiness": ready,
            "latest_plan_id": (latest.get("latest_plan") or {}).get("plan_id"),
            "plan_count": latest.get("plan_count", 0),
            "destructive_actions_allowed": False,
        }

    def get_package(self) -> Dict[str, Any]:
        return {"ok": True, "mode": "approved_deep_execution_package", "package": {"status": self.get_status(), "latest": self.latest()}}


approved_deep_execution_plan_service = ApprovedDeepExecutionPlanService()
