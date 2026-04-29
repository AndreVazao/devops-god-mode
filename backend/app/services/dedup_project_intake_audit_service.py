from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


class DedupProjectIntakeAuditService:
    """Audit duplicated/overlapping modules and define the canonical project-intake flow.

    This service exists because older foundations already covered browser intake,
    conversation grouping, popup delivery and resumable actions before phases
    105-108 added safer external AI session contracts. It prevents future work
    from blindly duplicating services.
    """

    OLD_FOUNDATION_MODULES = [
        {
            "id": "browser_conversation_intake",
            "service": "browser_conversation_intake_service.py",
            "route": "browser_conversation_intake.py",
            "capabilities": ["open_chat_plan", "scroll_up_history_plan", "capture_code_blocks", "priority_queue"],
            "canonical_role": "legacy_foundation_to_reuse",
        },
        {
            "id": "browser_control_real",
            "service": "browser_control_real_service.py",
            "route": "browser_control_real.py",
            "capabilities": ["assisted_browser_control", "open_chat", "focus_thread", "scroll_capture"],
            "canonical_role": "legacy_foundation_to_reuse",
        },
        {
            "id": "multi_ai_conversation_inventory",
            "service": "multi_ai_conversation_inventory_service.py",
            "route": "multi_ai_conversation_inventory.py",
            "capabilities": ["multi_provider_inventory", "project_guess", "repo_roles", "project_map"],
            "canonical_role": "canonical_inventory_base",
        },
        {
            "id": "conversation_organization",
            "service": "conversation_organization_service.py",
            "route": "conversation_organization.py",
            "capabilities": ["conversation_groups", "relations", "continuation_signals", "next_focus"],
            "canonical_role": "canonical_grouping_base",
        },
        {
            "id": "conversation_provider_linkage",
            "service": "conversation_provider_linkage_service.py",
            "route": "conversation_provider_linkage.py",
            "capabilities": ["provider_linkages", "rename_conversation_plans", "new_conversation_plans", "repo_creation_plans"],
            "canonical_role": "legacy_provider_action_plan",
        },
        {
            "id": "conversation_repo_reconstruction",
            "service": "conversation_repo_reconstruction_service.py",
            "route": "conversation_repo_reconstruction.py",
            "capabilities": ["repo_reconstruction_proposal", "approval_required", "proposed_tree"],
            "canonical_role": "canonical_reconstruction_approval_base",
        },
        {
            "id": "conversation_repo_materialization",
            "service": "conversation_repo_materialization_service.py",
            "route": "conversation_repo_materialization.py",
            "capabilities": ["materialize_bundle_repo_plan", "write_workspace_files", "manifest"],
            "canonical_role": "canonical_materialization_base",
        },
        {
            "id": "initial_inventory_project_graph",
            "service": "initial_inventory_project_graph_service.py",
            "route": "initial_inventory_project_graph.py",
            "capabilities": ["initial_inventory_sources", "project_graph_links", "repo_and_chat_sources"],
            "canonical_role": "initial_scan_base",
        },
        {
            "id": "operator_popup_delivery",
            "service": "operator_popup_delivery_service.py",
            "route": "operator_popup_delivery.py",
            "capabilities": ["popup_delivery", "reissue_pending", "operator_response_ack"],
            "canonical_role": "canonical_popup_delivery_base",
        },
        {
            "id": "operator_resumable_action",
            "service": "operator_resumable_action_service.py",
            "route": "operator_resumable_action.py",
            "capabilities": ["resumable_action", "offline_sync", "resume_from_checkpoint"],
            "canonical_role": "canonical_resume_base",
        },
    ]

    NEW_EXTERNAL_AI_MODULES = [
        {
            "id": "ai_chat_webservice_audit",
            "service": "ai_chat_webservice_audit_service.py",
            "route": "ai_chat_webservice_audit.py",
            "capabilities": ["gap_audit", "external_ai_readiness", "missing_layers"],
            "canonical_role": "audit_only",
        },
        {
            "id": "external_ai_session_plan",
            "service": "external_ai_session_plan_service.py",
            "route": "external_ai_session_plan.py",
            "capabilities": ["provider_registry", "manual_login_popup_contract", "checkpoints_without_secrets", "resume_contract"],
            "canonical_role": "safe_session_contract",
        },
        {
            "id": "external_ai_browser_worker",
            "service": "external_ai_browser_worker_service.py",
            "route": "external_ai_browser_worker.py",
            "capabilities": ["browser_worker_capability", "manual_login_confirmation", "pc_runner_probe", "safe_browser_actions"],
            "canonical_role": "safe_browser_contract",
        },
        {
            "id": "external_ai_chat_reader",
            "service": "external_ai_chat_reader_service.py",
            "route": "external_ai_chat_reader.py",
            "capabilities": ["reader_plan", "scroll_plan", "runtime_instructions", "normalize_snapshot"],
            "canonical_role": "safe_reader_contract",
        },
    ]

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def _exists(self, path: str) -> bool:
        return Path(path).exists()

    def _module_status(self, module: Dict[str, Any]) -> Dict[str, Any]:
        service_path = f"backend/app/services/{module['service']}"
        route_path = f"backend/app/routes/{module['route']}"
        return {
            **module,
            "service_path": service_path,
            "route_path": route_path,
            "service_exists": self._exists(service_path),
            "route_exists": self._exists(route_path),
            "exists": self._exists(service_path) and self._exists(route_path),
        }

    def build_audit(self) -> Dict[str, Any]:
        old_modules = [self._module_status(item) for item in self.OLD_FOUNDATION_MODULES]
        new_modules = [self._module_status(item) for item in self.NEW_EXTERNAL_AI_MODULES]
        overlaps = self._overlaps(old_modules, new_modules)
        decision = self._canonical_decision(overlaps)
        return {
            "ok": True,
            "mode": "dedup_project_intake_audit",
            "created_at": self._now(),
            "status": "overlap_found_needs_unification" if overlaps else "no_overlap_found",
            "old_foundation_modules": old_modules,
            "new_external_ai_modules": new_modules,
            "overlap_count": len(overlaps),
            "overlaps": overlaps,
            "canonical_decision": decision,
            "main_goal_contract": self.main_goal_contract(),
            "first_pc_boot_flow": self.first_pc_boot_flow(),
            "project_grouping_examples": self.project_grouping_examples(),
            "operator_next": {
                "label": "Unificar camadas antigas e novas",
                "endpoint": "/api/dedup-project-intake-audit/audit",
                "route": "/app/home",
            },
        }

    def _overlaps(self, old_modules: List[Dict[str, Any]], new_modules: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        overlaps: List[Dict[str, Any]] = []
        matrix = [
            ("browser_conversation_intake", "external_ai_chat_reader", "scroll/read/capture overlap"),
            ("browser_control_real", "external_ai_browser_worker", "browser control/session overlap"),
            ("operator_popup_delivery", "external_ai_session_plan", "login popup delivery overlap"),
            ("operator_resumable_action", "external_ai_session_plan", "resume/checkpoint overlap"),
            ("conversation_provider_linkage", "external_ai_session_plan", "provider registry/linkage overlap"),
            ("initial_inventory_project_graph", "multi_ai_conversation_inventory", "initial inventory/project graph overlap"),
        ]
        old_by_id = {item["id"]: item for item in old_modules}
        new_by_id = {item["id"]: item for item in new_modules}
        for old_id, new_id, reason in matrix:
            old_item = old_by_id.get(old_id)
            new_item = new_by_id.get(new_id)
            overlaps.append({
                "old_module": old_id,
                "new_module": new_id,
                "reason": reason,
                "old_exists": bool(old_item and old_item.get("exists")),
                "new_exists": bool(new_item and new_item.get("exists")),
                "risk": "medium" if bool(old_item and old_item.get("exists")) and bool(new_item and new_item.get("exists")) else "low",
                "action": "unify_do_not_delete_without_approval",
            })
        return overlaps

    def _canonical_decision(self, overlaps: List[Dict[str, Any]]) -> Dict[str, Any]:
        return {
            "delete_anything_now": False,
            "destructive_cleanup_allowed": False,
            "strategy": "adapter_unification_not_deletion",
            "canonical_layers": [
                {
                    "layer": "inventory_and_project_map",
                    "canonical_service": "multi_ai_conversation_inventory_service",
                    "reuse": ["initial_inventory_project_graph_service", "conversation_organization_service"],
                },
                {
                    "layer": "browser_intake_and_scroll",
                    "canonical_service": "external_ai_chat_reader_service",
                    "reuse": ["browser_conversation_intake_service", "browser_control_real_service"],
                },
                {
                    "layer": "provider_session_and_login",
                    "canonical_service": "external_ai_session_plan_service",
                    "reuse": ["conversation_provider_linkage_service", "operator_popup_delivery_service"],
                },
                {
                    "layer": "resumable_actions",
                    "canonical_service": "external_ai_session_plan_service",
                    "reuse": ["operator_resumable_action_service"],
                },
                {
                    "layer": "repo_reconstruction_and_materialization",
                    "canonical_service": "conversation_repo_reconstruction_service",
                    "reuse": ["conversation_repo_materialization_service", "conversation_repo_reconstruction_service"],
                },
            ],
            "next_phase_should": "create_unified_project_intake_orchestrator_that_calls_existing_services",
        }

    def main_goal_contract(self) -> Dict[str, Any]:
        return {
            "goal": "God Mode must organize AI conversations, repos and projects before deep execution.",
            "must_do": [
                "inventory conversations across AI providers",
                "read and scroll conversations when operator grants session/login",
                "associate each conversation to a project",
                "detect project repos and missing repos",
                "rename/label conversations by project and sequence when provider allows it",
                "group related conversations into project groups",
                "detect related repos that belong to the same product/project",
                "generate a first project tree/audit per repo or reconstructed project",
                "ask operator for priority order before execution",
                "only then start repair/build/materialization work",
            ],
            "must_not_do": [
                "delete old modules without explicit approval",
                "store credentials/tokens/cookies",
                "send prompts to external AIs without safety gate",
                "prioritize projects by revenue instead of operator priority",
            ],
        }

    def first_pc_boot_flow(self) -> List[Dict[str, Any]]:
        return [
            {"step": 1, "id": "inventory_sources", "label": "Inventariar fontes: conversas AI, GitHub repos, pastas locais", "owner": "initial_inventory_project_graph + multi_ai_inventory"},
            {"step": 2, "id": "conversation_scan", "label": "Ler títulos/snippets e preparar leitura/scroll de conversas", "owner": "external_ai_chat_reader + browser_conversation_intake"},
            {"step": 3, "id": "project_mapping", "label": "Associar conversas a projetos e detetar grupos", "owner": "multi_ai_conversation_inventory + conversation_organization"},
            {"step": 4, "id": "repo_mapping", "label": "Associar repos a projetos e detetar repos em falta", "owner": "repo_relationship_graph + conversation_repo_reconstruction"},
            {"step": 5, "id": "project_tree_audit", "label": "Gerar árvore inicial e auditoria superficial por projeto", "owner": "project_tree_sync_guard + repo_relationship_graph"},
            {"step": 6, "id": "operator_priority", "label": "Enviar resumo e pedir prioridades ao operador", "owner": "operator_priority + approval cockpit"},
            {"step": 7, "id": "execution_plan", "label": "Só depois planear correção/build/materialização", "owner": "real work pipeline"},
        ]

    def project_grouping_examples(self) -> List[Dict[str, Any]]:
        return [
            {
                "project_group": "Baribudos Studio Ecosystem",
                "related_repos": ["baribudos-studio-website", "baribudos-studio"],
                "reason": "Studio creates/controls content and website publishes/serves it; separate repos but same product ecosystem.",
                "expected_handling": "Group as one project with multiple repos and roles: studio/control-panel + website/publishing-target.",
            },
            {
                "project_group": "God Mode",
                "related_repos": ["devops-god-mode"],
                "reason": "Primary orchestration system; high priority unless operator changes it.",
                "expected_handling": "Treat as main system and source of automation/control.",
            },
        ]

    def get_status(self) -> Dict[str, Any]:
        audit = self.build_audit()
        return {
            "ok": True,
            "mode": "dedup_project_intake_audit_status",
            "status": audit["status"],
            "overlap_count": audit["overlap_count"],
            "delete_anything_now": audit["canonical_decision"]["delete_anything_now"],
            "next_phase_should": audit["canonical_decision"]["next_phase_should"],
        }

    def get_package(self) -> Dict[str, Any]:
        return {"ok": True, "mode": "dedup_project_intake_audit_package", "package": {"status": self.get_status(), "audit": self.build_audit()}}


dedup_project_intake_audit_service = DedupProjectIntakeAuditService()
