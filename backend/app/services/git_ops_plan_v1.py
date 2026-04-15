from typing import Any


class GitOpsPlanV1:
    def build(self, payload: dict[str, Any]) -> dict[str, Any]:
        repo_full_name = payload.get("repo_full_name")
        operation = payload.get("operation") or "analysis_only"
        target_path = payload.get("target_path")
        proposed_branch = payload.get("proposed_branch") or self._default_branch_name(operation, target_path)
        approval_required = operation != "analysis_only"

        steps = [
            {"step": 1, "title": "Resolver repo alvo", "status": "planned"},
            {"step": 2, "title": "Criar branch de trabalho", "status": "planned"},
            {"step": 3, "title": "Aplicar alteração ao ficheiro alvo", "status": "planned"},
            {"step": 4, "title": "Gerar commit com contexto", "status": "planned"},
            {"step": 5, "title": "Abrir PR ou preparar merge", "status": "planned"},
        ]

        if operation == "analysis_only":
            steps = [{"step": 1, "title": "Analisar sem escrever", "status": "planned"}]

        return {
            "ok": True,
            "mode": "git_ops_plan",
            "repo_full_name": repo_full_name,
            "operation": operation,
            "target_path": target_path,
            "proposed_branch": proposed_branch,
            "approval_required": approval_required,
            "steps": steps,
            "merge_strategy": "pull_request_first" if approval_required else "none",
        }

    def _default_branch_name(self, operation: str, target_path: str | None) -> str:
        suffix = (target_path or operation or "change").replace('/', '-').replace('.', '-').strip('-')[:40]
        prefix_map = {
            "replace_file": "replace",
            "append_to_file": "append",
            "patch_existing_file": "patch",
            "new_file": "add",
            "analysis_only": "analysis",
        }
        prefix = prefix_map.get(operation, "change")
        return f"{prefix}/{suffix or 'target'}"


git_ops_plan_v1 = GitOpsPlanV1()
