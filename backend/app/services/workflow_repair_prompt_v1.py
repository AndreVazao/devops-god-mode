from typing import Any


class WorkflowRepairPromptV1:
    def build(self, payload: dict[str, Any]) -> dict[str, Any]:
        workflow_error = payload.get("workflow_error") or {}
        repo_full_name = workflow_error.get("repo_full_name") or payload.get("repo_full_name") or "repo-a-determinar"
        category = workflow_error.get("category") or "unknown"
        probable_cause = workflow_error.get("probable_cause") or "Análise manual necessária."
        suggested_fix = workflow_error.get("suggested_fix") or "Gerar proposta de correção baseada no erro."
        log_excerpt = workflow_error.get("log_excerpt") or payload.get("error_text") or ""

        prompt = (
            "Analisa este erro de workflow/build/deploy e devolve uma correção objetiva e segura.\n\n"
            f"Repo: {repo_full_name}\n"
            f"Categoria: {category}\n"
            f"Causa provável: {probable_cause}\n"
            f"Correção sugerida: {suggested_fix}\n\n"
            "Responde dizendo: \n"
            "1) ficheiro provável a alterar\n"
            "2) se é substituição total, patch parcial ou ajuste de config\n"
            "3) código final sugerido\n"
            "4) motivo técnico da correção\n\n"
            f"Excerto do erro:\n{log_excerpt}\n"
        )

        return {
            "ok": True,
            "mode": "workflow_repair_prompt",
            "repo_full_name": repo_full_name,
            "prompt": prompt,
            "category": category,
        }


workflow_repair_prompt_v1 = WorkflowRepairPromptV1()
