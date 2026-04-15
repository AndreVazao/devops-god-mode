from typing import Any

from app.services.browser_prompt_builder_v1 import browser_prompt_builder_v1
from app.services.code_intake_parser_v1 import code_intake_parser_v1
from app.services.git_ops_plan_v1 import git_ops_plan_v1
from app.services.repo_resolution_engine_v1 import repo_resolution_engine_v1


class CodeIntakePipelineV1:
    def run(self, payload: dict[str, Any]) -> dict[str, Any]:
        intake = code_intake_parser_v1.parse(payload)

        registry_context = payload.get("registry_context") or {}
        resolution = repo_resolution_engine_v1.resolve(
            {
                "intake": intake,
                "registry_context": registry_context,
            }
        )

        git_plan = git_ops_plan_v1.build(
            {
                "repo_full_name": resolution.get("resolved_repo"),
                "operation": resolution.get("primary_operation"),
                "target_path": resolution.get("target_path"),
                "proposed_branch": payload.get("proposed_branch"),
            }
        )

        browser_prompt = browser_prompt_builder_v1.build(
            {
                "intake": intake,
                "resolution": resolution,
            }
        )

        return {
            "ok": True,
            "mode": "code_intake_pipeline",
            "intake": intake,
            "resolution": resolution,
            "git_ops_plan": git_plan,
            "browser_prompt": browser_prompt,
            "next_action": self._build_next_action(resolution, git_plan),
        }

    def _build_next_action(self, resolution: dict[str, Any], git_plan: dict[str, Any]) -> dict[str, Any]:
        operation = resolution.get("primary_operation") or "analysis_only"
        target_repo_action = resolution.get("target_repo_action") or "repo_resolution_required"
        branch = git_plan.get("proposed_branch")

        if resolution.get("create_new_repo"):
            return {
                "decision": "altera",
                "message": "Criar repo nova antes de aplicar código.",
                "approval_required": True,
            }
        if operation == "analysis_only":
            return {
                "decision": "ok",
                "message": "Sem escrita ainda. Rever análise e decidir operação.",
                "approval_required": False,
            }
        return {
            "decision": "altera",
            "message": f"Preparar branch {branch} e seguir com {target_repo_action}.",
            "approval_required": True,
        }


code_intake_pipeline_v1 = CodeIntakePipelineV1()
