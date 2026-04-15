from typing import Any


class ApprovalShellV1:
    def build(self, payload: dict[str, Any]) -> dict[str, Any]:
        intake = payload.get("intake") or {}
        resolution = payload.get("resolution") or {}
        git_ops_plan = payload.get("git_ops_plan") or {}
        next_action = payload.get("next_action") or {}

        target_repo = resolution.get("resolved_repo") or intake.get("resolved_repo")
        target_path = resolution.get("target_path") or intake.get("target_path")
        operation = resolution.get("primary_operation") or intake.get("primary_operation")
        branch = git_ops_plan.get("proposed_branch")

        return {
            "ok": True,
            "mode": "approval_shell",
            "headline": next_action.get("message") or "Rever ação proposta.",
            "decision": next_action.get("decision") or "ok",
            "approval_required": bool(next_action.get("approval_required")),
            "target": {
                "repo": target_repo,
                "path": target_path,
                "operation": operation,
                "branch": branch,
            },
            "buttons": [
                {"key": "ok", "label": "OK", "style": "primary", "meaning": "Aceitar a proposta atual"},
                {"key": "altera", "label": "ALTERA", "style": "warning", "meaning": "Aceitar mas alterar repo/path/estratégia antes de executar"},
                {"key": "rejeita", "label": "REJEITA", "style": "neutral", "meaning": "Rejeitar a ação proposta"}
            ],
            "compact_summary": {
                "repo": target_repo,
                "path": target_path,
                "branch": branch,
                "operation": operation,
            },
        }


approval_shell_v1 = ApprovalShellV1()
