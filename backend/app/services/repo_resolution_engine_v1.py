from typing import Any


class RepoResolutionEngineV1:
    def resolve(self, payload: dict[str, Any]) -> dict[str, Any]:
        intake = payload.get("intake") or {}
        registry_context = payload.get("registry_context") or {}

        resolved_repo = intake.get("resolved_repo")
        target_repo_action = intake.get("target_repo_action")
        target_path = intake.get("target_path")
        primary_operation = intake.get("primary_operation")

        ecosystem_hint = registry_context.get("ecosystem_key")
        related_repos = registry_context.get("related_repos") or []

        confidence = "high" if resolved_repo else "medium" if related_repos else "low"
        create_new_repo = False
        suggested_repo_name = None

        if not resolved_repo and related_repos:
            resolved_repo = related_repos[0]
            target_repo_action = "related_repo_selected"
        elif not resolved_repo:
            create_new_repo = True
            suggested_repo_name = registry_context.get("suggested_repo_name") or "new-god-mode-target"
            target_repo_action = "new_repo_required"

        target_file_strategy = "unknown"
        if primary_operation == "replace_file":
            target_file_strategy = "replace_exact_path"
        elif primary_operation == "append_to_file":
            target_file_strategy = "append_exact_path"
        elif primary_operation == "patch_existing_file":
            target_file_strategy = "patch_exact_path"
        elif primary_operation == "new_file":
            target_file_strategy = "create_new_path"
        elif primary_operation == "analysis_only":
            target_file_strategy = "no_write"

        return {
            "ok": True,
            "mode": "repo_resolution",
            "resolved_repo": resolved_repo,
            "target_repo_action": target_repo_action,
            "target_path": target_path,
            "primary_operation": primary_operation,
            "target_file_strategy": target_file_strategy,
            "create_new_repo": create_new_repo,
            "suggested_repo_name": suggested_repo_name,
            "ecosystem_hint": ecosystem_hint,
            "confidence": confidence,
        }


repo_resolution_engine_v1 = RepoResolutionEngineV1()
