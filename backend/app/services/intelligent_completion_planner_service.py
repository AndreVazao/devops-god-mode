from __future__ import annotations

from typing import Any, Dict, List

from app.services.capability_reuse_service import capability_reuse_service
from app.services.conversation_bundle_service import conversation_bundle_service
from app.services.conversation_reconciliation_service import conversation_reconciliation_service


class IntelligentCompletionPlannerService:
    def get_status(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "mode": "intelligent_completion_planner_status",
            "status": "intelligent_completion_planner_ready",
        }

    def build_completion_plan(
        self,
        bundle_id: str,
        target_project: str,
        desired_capabilities: List[str],
    ) -> Dict[str, Any]:
        bundle = conversation_bundle_service.get_bundle(bundle_id)
        if not bundle:
            return {
                "ok": False,
                "mode": "intelligent_completion_plan_result",
                "plan_status": "bundle_not_found",
                "bundle_id": bundle_id,
            }

        reconciliation = conversation_reconciliation_service.get_report(bundle_id)
        repo_plan = conversation_bundle_service.build_repo_materialization_plan(
            bundle_id=bundle_id,
            repository_name=target_project,
        )
        conflict_count = 0
        deduplicated_blocks: List[Dict[str, Any]] = []
        if reconciliation.get("ok"):
            report = reconciliation["report"]
            conflict_count = int(report.get("conflict_count") or 0)
            deduplicated_blocks = report.get("deduplicated_blocks", [])

        capability_actions: List[Dict[str, Any]] = []
        for capability_name in desired_capabilities:
            suggestion = capability_reuse_service.suggest_reuse_plan(
                capability_name=capability_name,
                target_project=target_project,
            )
            capability_actions.append(
                {
                    "capability_name": capability_name,
                    "reuse_candidate_count": suggestion.get("reuse_candidate_count", 0),
                    "plan_items": suggestion.get("plan_items", []),
                }
            )

        file_targets = []
        for item in repo_plan.get("plan", {}).get("file_plan", []):
            file_targets.append(
                {
                    "destination_path": item.get("destination_path"),
                    "provider": item.get("provider"),
                    "line_count": item.get("line_count"),
                }
            )

        action_items: List[Dict[str, Any]] = []
        if conflict_count > 0:
            action_items.append(
                {
                    "action": "review_reconciled_conflicts",
                    "priority": "high",
                    "detail": f"{conflict_count} conflitos reconciliados automaticamente; validar os ficheiros principais antes de aplicar em repo existente.",
                }
            )
        for capability in capability_actions:
            if capability["reuse_candidate_count"] > 0:
                action_items.append(
                    {
                        "action": "reuse_existing_capability",
                        "priority": "high",
                        "detail": f"Reaproveitar base existente para {capability['capability_name']} antes de gerar código novo.",
                        "capability_name": capability["capability_name"],
                    }
                )
            else:
                action_items.append(
                    {
                        "action": "implement_missing_capability",
                        "priority": "medium",
                        "detail": f"Não foram encontrados candidatos locais fortes para {capability['capability_name']}; gerar implementação nova ou complementar pela conversa.",
                        "capability_name": capability["capability_name"],
                    }
                )

        plan = {
            "bundle_id": bundle_id,
            "target_project": target_project,
            "provider_count": len(bundle.get("providers", [])),
            "desired_capabilities": desired_capabilities,
            "repo_file_target_count": len(file_targets),
            "reconciled_file_count": len(deduplicated_blocks),
            "conflict_count": conflict_count,
            "file_targets": file_targets,
            "capability_actions": capability_actions,
            "action_items": action_items,
            "plan_status": "completion_plan_ready",
        }
        return {
            "ok": True,
            "mode": "intelligent_completion_plan_result",
            "plan_status": "completion_plan_ready",
            "plan": plan,
        }

    def get_package(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "mode": "intelligent_completion_planner_package",
            "package": {
                "status": self.get_status(),
                "package_status": "intelligent_completion_planner_ready",
            },
        }


intelligent_completion_planner_service = IntelligentCompletionPlannerService()
