from typing import Any


class MobileCockpitPayloadV1:
    def build(self, payload: dict[str, Any]) -> dict[str, Any]:
        execution = payload.get("execution") or {}
        intake_pipeline = execution.get("intake_pipeline") or {}
        approval_shell = execution.get("approval_shell") or {}
        visibility_policy = execution.get("visibility_policy") or {}
        pr_plan = execution.get("pr_execution_plan") or {}

        resolution = intake_pipeline.get("resolution") or {}
        git_ops_plan = intake_pipeline.get("git_ops_plan") or {}
        next_action = intake_pipeline.get("next_action") or {}

        return {
            "ok": True,
            "mode": "mobile_cockpit",
            "headline": approval_shell.get("headline") or next_action.get("message") or "Sem ação prioritária.",
            "decision": approval_shell.get("decision") or next_action.get("decision") or "ok",
            "approval_required": bool(approval_shell.get("approval_required") or next_action.get("approval_required")),
            "target": {
                "repo": resolution.get("resolved_repo"),
                "path": resolution.get("target_path"),
                "operation": resolution.get("primary_operation"),
                "branch": git_ops_plan.get("proposed_branch"),
                "base_branch": pr_plan.get("base_branch"),
            },
            "visibility": {
                "now": visibility_policy.get("visibility_now"),
                "when_ready": visibility_policy.get("visibility_when_ready"),
                "current_recommendation": visibility_policy.get("current_recommendation"),
            },
            "pull_request": {
                "title": pr_plan.get("title"),
                "draft": pr_plan.get("draft"),
                "merge_policy": pr_plan.get("merge_policy"),
                "ready_for_pr": execution.get("ready_for_pr", False),
            },
            "buttons": approval_shell.get("buttons") or [
                {"key": "ok", "label": "OK"},
                {"key": "altera", "label": "ALTERA"},
                {"key": "rejeita", "label": "REJEITA"},
            ],
            "compact_cards": [
                {
                    "key": "repo",
                    "title": "Repo alvo",
                    "value": resolution.get("resolved_repo") or "por resolver",
                },
                {
                    "key": "path",
                    "title": "Ficheiro alvo",
                    "value": resolution.get("target_path") or "por resolver",
                },
                {
                    "key": "branch",
                    "title": "Branch sugerida",
                    "value": git_ops_plan.get("proposed_branch") or "por resolver",
                },
                {
                    "key": "visibility",
                    "title": "Visibilidade",
                    "value": visibility_policy.get("current_recommendation") or "por resolver",
                },
            ],
            "next_step": execution.get("next_step"),
        }


mobile_cockpit_payload_v1 = MobileCockpitPayloadV1()
