from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Callable, Dict, List
from uuid import uuid4

from app.services.dedup_project_intake_audit_service import dedup_project_intake_audit_service
from app.services.initial_inventory_project_graph_service import initial_inventory_project_graph_service
from app.services.multi_ai_conversation_inventory_service import multi_ai_conversation_inventory_service
from app.services.conversation_organization_service import conversation_organization_service
from app.services.conversation_provider_linkage_service import conversation_provider_linkage_service
from app.services.conversation_repo_reconstruction_service import conversation_repo_reconstruction_service
from app.services.conversation_repo_materialization_service import conversation_repo_materialization_service
from app.services.external_ai_session_plan_service import external_ai_session_plan_service
from app.services.external_ai_browser_worker_service import external_ai_browser_worker_service
from app.services.external_ai_chat_reader_service import external_ai_chat_reader_service
from app.services.operator_priority_service import operator_priority_service
from app.services.project_tree_sync_guard_service import project_tree_sync_guard_service
from app.services.repo_relationship_graph_service import repo_relationship_graph_service


class UnifiedProjectIntakeOrchestratorService:
    """Canonical orchestrator for the first real God Mode project intake.

    This service intentionally reuses existing modules instead of creating a new
    parallel implementation. It coordinates inventory, project mapping, repo
    grouping, conversation intake, first audits and operator priority handoff.
    """

    CANONICAL_LAYERS = [
        {
            "id": "dedup_guard",
            "label": "Auditar duplicados e papéis canónicos",
            "owner": "dedup_project_intake_audit_service",
            "required": True,
        },
        {
            "id": "source_inventory",
            "label": "Inventariar fontes: conversas, repos e memória",
            "owner": "initial_inventory_project_graph_service + multi_ai_conversation_inventory_service",
            "required": True,
        },
        {
            "id": "conversation_project_map",
            "label": "Associar conversas a projetos e grupos",
            "owner": "conversation_organization_service + multi_ai_conversation_inventory_service",
            "required": True,
        },
        {
            "id": "provider_session_readiness",
            "label": "Preparar sessões externas de IA sem guardar credenciais",
            "owner": "external_ai_session_plan_service + external_ai_browser_worker_service + external_ai_chat_reader_service",
            "required": True,
        },
        {
            "id": "repo_project_map",
            "label": "Associar repos a projetos e detetar repos em falta",
            "owner": "repo_relationship_graph_service + conversation_repo_reconstruction_service",
            "required": True,
        },
        {
            "id": "project_tree_superficial_audit",
            "label": "Gerar árvore/auditoria superficial por projeto",
            "owner": "project_tree_sync_guard_service",
            "required": True,
        },
        {
            "id": "operator_priority_handoff",
            "label": "Enviar resumo ao operador e pedir prioridades",
            "owner": "operator_priority_service",
            "required": True,
        },
    ]

    KNOWN_PROJECT_GROUPS = [
        {
            "group_id": "baribudos_studio_ecosystem",
            "label": "Baribudos Studio Ecosystem",
            "repos": ["baribudos-studio", "baribudos-studio-website"],
            "roles": {
                "baribudos-studio": "studio/control-panel/content-creator",
                "baribudos-studio-website": "website/publishing-target",
            },
            "handling": "single_project_group_multi_repo",
        },
        {
            "group_id": "god_mode_core",
            "label": "God Mode Core",
            "repos": ["devops-god-mode"],
            "roles": {"devops-god-mode": "orchestrator/control-plane"},
            "handling": "main_system_project",
        },
    ]

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def _safe(self, label: str, fn: Callable[[], Any]) -> Dict[str, Any]:
        try:
            value = fn()
            return value if isinstance(value, dict) else {"ok": True, "mode": label, "value": value}
        except Exception as exc:
            return {
                "ok": False,
                "mode": label,
                "error": exc.__class__.__name__,
                "detail": str(exc)[:500],
            }

    def build_plan(self, tenant_id: str = "owner-andre", requested_project: str = "GOD_MODE") -> Dict[str, Any]:
        plan_id = f"unified-intake-plan-{uuid4().hex[:12]}"
        dedup = self._safe("dedup_project_intake_audit", dedup_project_intake_audit_service.build_audit)
        priority = self._safe("operator_priority", operator_priority_service.get_status)
        return {
            "ok": True,
            "mode": "unified_project_intake_plan",
            "plan_id": plan_id,
            "created_at": self._now(),
            "tenant_id": tenant_id,
            "requested_project": requested_project,
            "status": "ready_to_run_safe_inventory",
            "destructive_actions_allowed": False,
            "canonical_layers": self.CANONICAL_LAYERS,
            "known_project_groups": self.KNOWN_PROJECT_GROUPS,
            "dedup_status": {
                "ok": dedup.get("ok"),
                "status": dedup.get("status"),
                "overlap_count": dedup.get("overlap_count"),
                "strategy": (dedup.get("canonical_decision") or {}).get("strategy"),
            },
            "operator_priority_status": priority,
            "execution_rules": self.execution_rules(),
            "first_pc_boot_flow": self.first_pc_boot_flow(),
            "operator_next": {
                "label": "Executar intake unificado seguro",
                "endpoint": "/api/unified-project-intake/run-safe",
                "route": "/app/home",
            },
        }

    def run_safe(self, tenant_id: str = "owner-andre", requested_project: str = "GOD_MODE") -> Dict[str, Any]:
        """Run a non-destructive orchestration pass.

        This builds a consolidated report from existing services. It does not
        rename conversations, create repos, write project files, or send prompts
        to external AIs. Those steps remain approval-gated future actions.
        """
        run_id = f"unified-intake-run-{uuid4().hex[:12]}"
        plan = self.build_plan(tenant_id=tenant_id, requested_project=requested_project)
        snapshots = {
            "dedup": self._safe("dedup_project_intake_audit", dedup_project_intake_audit_service.build_audit),
            "initial_inventory": self._safe("initial_inventory_project_graph", initial_inventory_project_graph_service.get_package),
            "multi_ai_inventory": self._safe("multi_ai_conversation_inventory", multi_ai_conversation_inventory_service.get_package),
            "conversation_organization": self._safe("conversation_organization", conversation_organization_service.get_package),
            "provider_linkage": self._safe("conversation_provider_linkage", conversation_provider_linkage_service.get_package),
            "external_ai_session": self._safe("external_ai_session_plan", external_ai_session_plan_service.get_package),
            "external_ai_browser": self._safe("external_ai_browser_worker", external_ai_browser_worker_service.get_package),
            "external_ai_reader": self._safe("external_ai_chat_reader", external_ai_chat_reader_service.get_package),
            "repo_relationship": self._safe("repo_relationship_graph", repo_relationship_graph_service.get_package),
            "repo_reconstruction": self._safe("conversation_repo_reconstruction", conversation_repo_reconstruction_service.get_package),
            "repo_materialization": self._safe("conversation_repo_materialization", conversation_repo_materialization_service.get_package),
            "project_tree_guard": self._safe("project_tree_sync_guard", project_tree_sync_guard_service.get_package),
            "operator_priority": self._safe("operator_priority", operator_priority_service.get_status),
        }
        findings = self._build_findings(snapshots)
        groups = self._project_groups_from_snapshots(snapshots)
        blockers = [item for item in findings if item.get("severity") == "blocker"]
        warnings = [item for item in findings if item.get("severity") == "warning"]
        return {
            "ok": len(blockers) == 0,
            "mode": "unified_project_intake_run_safe",
            "run_id": run_id,
            "created_at": self._now(),
            "tenant_id": tenant_id,
            "requested_project": requested_project,
            "status": "needs_attention" if blockers else ("ready_for_operator_priorities" if warnings else "ready"),
            "plan": plan,
            "snapshots": snapshots,
            "project_groups": groups,
            "findings": findings,
            "blocker_count": len(blockers),
            "warning_count": len(warnings),
            "operator_summary": self._summary(blockers=blockers, warnings=warnings, groups=groups),
            "operator_questions": self.operator_priority_questions(groups),
            "approval_gates": self.approval_gates(),
            "operator_next": {
                "label": "Definir prioridades dos projetos",
                "endpoint": "/api/operator-priority/status",
                "route": "/app/home",
            },
        }

    def execution_rules(self) -> Dict[str, Any]:
        return {
            "inventory_before_execution": True,
            "operator_priority_before_deep_work": True,
            "destructive_changes_require_explicit_approval": True,
            "external_ai_prompt_send_requires_safety_gate": True,
            "manual_login_only_for_external_ai": True,
            "no_credentials_or_tokens_in_memory": True,
            "reuse_existing_services_first": True,
            "new_parallel_services_discouraged": True,
        }

    def first_pc_boot_flow(self) -> List[Dict[str, Any]]:
        return [
            {"step": 1, "id": "dedup_guard", "label": "Confirmar serviços canónicos e overlaps", "action": "/api/dedup-project-intake-audit/audit"},
            {"step": 2, "id": "source_inventory", "label": "Inventariar conversas/repos/memória", "action": "existing_inventory_services"},
            {"step": 3, "id": "conversation_project_map", "label": "Associar conversas a projetos", "action": "conversation_organization"},
            {"step": 4, "id": "repo_project_map", "label": "Associar repos a projetos e detetar repos em falta", "action": "repo_relationship_graph"},
            {"step": 5, "id": "project_tree_audit", "label": "Criar árvore/auditoria superficial por projeto", "action": "project_tree_sync_guard"},
            {"step": 6, "id": "operator_priority", "label": "Perguntar prioridades ao operador", "action": "operator_priority"},
            {"step": 7, "id": "deep_execution", "label": "Só depois executar recuperação/build/materialização", "action": "approval_gated_real_work"},
        ]

    def approval_gates(self) -> List[Dict[str, Any]]:
        return [
            {"id": "rename_external_conversations", "requires_approval": True, "reason": "altera estado em provider externo"},
            {"id": "create_missing_repo", "requires_approval": True, "reason": "cria recurso GitHub"},
            {"id": "materialize_code_from_conversation", "requires_approval": True, "reason": "escreve ficheiros"},
            {"id": "send_prompt_to_external_ai", "requires_approval": True, "reason": "pode expor contexto"},
            {"id": "merge_or_delete_modules", "requires_approval": True, "reason": "mudança estrutural/destrutiva"},
        ]

    def operator_priority_questions(self, groups: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        return [
            {
                "id": "main_projects_order",
                "question": "Quais são os projetos principais e qual é a ordem?",
                "default_options": [group["label"] for group in groups[:8]],
            },
            {
                "id": "secondary_projects",
                "question": "Quais ficam como secundários/espera?",
                "default_options": [],
            },
            {
                "id": "repo_group_confirmation",
                "question": "Confirmas os grupos de repos relacionados?",
                "default_options": [group["group_id"] for group in groups],
            },
            {
                "id": "external_ai_scan_permission",
                "question": "Autorizas preparar leitura/scroll das conversas externas por provider, com login manual quando necessário?",
                "default_options": ["sim_com_login_manual", "não_agora"],
            },
        ]

    def _build_findings(self, snapshots: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
        findings: List[Dict[str, Any]] = []
        for key, snapshot in snapshots.items():
            if not snapshot.get("ok", False):
                findings.append({
                    "id": f"{key}_not_ok",
                    "severity": "warning",
                    "label": f"{key} devolveu atenção/erro",
                    "detail": snapshot.get("error") or snapshot.get("detail") or snapshot.get("status"),
                })
        dedup = snapshots.get("dedup", {})
        if dedup.get("overlap_count", 0) > 0:
            findings.append({
                "id": "overlap_requires_unification",
                "severity": "warning",
                "label": "Há overlap entre serviços antigos e novos; usar orchestrator/adapters antes de criar mais serviços paralelos.",
                "detail": {"overlap_count": dedup.get("overlap_count")},
            })
        if not snapshots.get("operator_priority", {}).get("ok", False):
            findings.append({
                "id": "operator_priority_unavailable",
                "severity": "blocker",
                "label": "Prioridade do operador não disponível; não avançar para execução profunda.",
            })
        return findings

    def _project_groups_from_snapshots(self, snapshots: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
        # Start with known manual/canonical examples. Future phases may merge
        # detected groups from multi_ai_inventory/conversation_organization.
        groups = [dict(group) for group in self.KNOWN_PROJECT_GROUPS]
        groups.append({
            "group_id": "unknown_unclassified",
            "label": "Conversas/repos ainda por classificar",
            "repos": [],
            "roles": {},
            "handling": "requires_inventory_and_operator_review",
        })
        return groups

    def _summary(self, blockers: List[Dict[str, Any]], warnings: List[Dict[str, Any]], groups: List[Dict[str, Any]]) -> str:
        if blockers:
            return f"Intake unificado encontrou {len(blockers)} blocker(s). Não avançar para execução profunda."
        if warnings:
            return f"Intake unificado pronto com {len(warnings)} aviso(s). Próximo passo: confirmar prioridades e grupos de projetos."
        return f"Intake unificado pronto. {len(groups)} grupo(s) de projeto preparados para revisão do operador."

    def get_status(self) -> Dict[str, Any]:
        plan = self.build_plan()
        return {
            "ok": True,
            "mode": "unified_project_intake_status",
            "status": plan["status"],
            "canonical_layer_count": len(plan["canonical_layers"]),
            "known_project_group_count": len(plan["known_project_groups"]),
            "destructive_actions_allowed": False,
            "operator_next": plan["operator_next"],
        }

    def get_package(self) -> Dict[str, Any]:
        return {"ok": True, "mode": "unified_project_intake_package", "package": {"status": self.get_status(), "plan": self.build_plan()}}


unified_project_intake_orchestrator_service = UnifiedProjectIntakeOrchestratorService()
