from typing import Any


class PRExecutionPlanV1:
    def build(self, payload: dict[str, Any]) -> dict[str, Any]:
        repo_full_name = payload.get("repo_full_name")
        proposed_branch = payload.get("proposed_branch") or "change/target"
        base_branch = payload.get("base_branch") or "main"
        operation = payload.get("operation") or "analysis_only"
        target_path = payload.get("target_path")
        approval_required = bool(payload.get("approval_required", True))

        title = self._build_pr_title(operation, target_path)
        body = self._build_pr_body(repo_full_name, operation, target_path, proposed_branch, base_branch, approval_required)

        return {
            "ok": True,
            "mode": "pr_execution_plan",
            "repo_full_name": repo_full_name,
            "base_branch": base_branch,
            "head_branch": proposed_branch,
            "title": title,
            "body": body,
            "draft": True,
            "approval_required": approval_required,
            "merge_policy": "manual_after_review",
        }

    def _build_pr_title(self, operation: str, target_path: str | None) -> str:
        path_part = target_path or "target"
        prefix_map = {
            "replace_file": "replace",
            "append_to_file": "append",
            "patch_existing_file": "patch",
            "new_file": "add",
            "analysis_only": "analyze",
        }
        prefix = prefix_map.get(operation, "change")
        return f"{prefix}: {path_part}"

    def _build_pr_body(
        self,
        repo_full_name: str | None,
        operation: str,
        target_path: str | None,
        proposed_branch: str,
        base_branch: str,
        approval_required: bool,
    ) -> str:
        return (
            f"Repo: {repo_full_name or 'a_resolver'}\n"
            f"Operação: {operation}\n"
            f"Ficheiro alvo: {target_path or 'a_resolver'}\n"
            f"Head branch: {proposed_branch}\n"
            f"Base branch: {base_branch}\n"
            f"Aprovação obrigatória: {'sim' if approval_required else 'não'}\n\n"
            "Este PR foi preparado pelo God Mode para revisão manual antes de merge."
        )


pr_execution_plan_v1 = PRExecutionPlanV1()
