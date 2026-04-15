from typing import Any

from app.services.approval_shell_v1 import approval_shell_v1
from app.services.code_intake_pipeline_v1 import code_intake_pipeline_v1
from app.services.pr_execution_plan_v1 import pr_execution_plan_v1
from app.services.repo_visibility_policy_v1 import repo_visibility_policy_v1


class OpsExecutionPipelineV1:
    def run(self, payload: dict[str, Any]) -> dict[str, Any]:
        intake_pipeline = code_intake_pipeline_v1.run(payload)
        approval_shell = approval_shell_v1.build(intake_pipeline)

        resolution = intake_pipeline.get("resolution") or {}
        git_ops_plan = intake_pipeline.get("git_ops_plan") or {}

        visibility_policy = repo_visibility_policy_v1.plan(
            {
                "repo_full_name": resolution.get("resolved_repo"),
                "desired_visibility": payload.get("desired_visibility") or "private",
                "lifecycle_mode": payload.get("lifecycle_mode") or "private_only",
                "build_strategy": payload.get("build_strategy") or "standard",
                "product_ready": payload.get("product_ready") or False,
            }
        )

        pr_plan = pr_execution_plan_v1.build(
            {
                "repo_full_name": resolution.get("resolved_repo"),
                "proposed_branch": git_ops_plan.get("proposed_branch"),
                "base_branch": payload.get("base_branch") or "main",
                "operation": resolution.get("primary_operation"),
                "target_path": resolution.get("target_path"),
                "approval_required": approval_shell.get("approval_required", True),
            }
        )

        return {
            "ok": True,
            "mode": "ops_execution_pipeline",
            "intake_pipeline": intake_pipeline,
            "approval_shell": approval_shell,
            "visibility_policy": visibility_policy,
            "pr_execution_plan": pr_plan,
            "ready_for_pr": bool(pr_plan.get("repo_full_name") and pr_plan.get("head_branch")),
            "next_step": "Rever approval_shell e, se aprovado, abrir branch/PR conforme pr_execution_plan.",
        }


ops_execution_pipeline_v1 = OpsExecutionPipelineV1()
