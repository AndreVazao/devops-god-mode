from typing import Any


class BrowserPromptBuilderV1:
    def build(self, payload: dict[str, Any]) -> dict[str, Any]:
        intake = payload.get("intake") or {}
        resolution = payload.get("resolution") or {}
        workflow_error = payload.get("workflow_error") or {}

        repo = resolution.get("resolved_repo") or intake.get("resolved_repo") or "repo-a-determinar"
        path = resolution.get("target_path") or intake.get("target_path") or "ficheiro-a-determinar"
        operation = resolution.get("primary_operation") or intake.get("primary_operation") or "analysis_only"

        if workflow_error:
            prompt = (
                "Analisa este erro de workflow/build e devolve correção objetiva.\n\n"
                f"Repo: {repo}\n"
                f"Categoria: {workflow_error.get('category')}\n"
                f"Causa provável: {workflow_error.get('probable_cause')}\n"
                f"Correção sugerida: {workflow_error.get('suggested_fix')}\n"
                f"Excerto do log:\n{workflow_error.get('log_excerpt', '')}\n"
            )
        else:
            prompt = (
                "Analisa este pedido de alteração de código e devolve instrução final de implementação.\n\n"
                f"Repo alvo: {repo}\n"
                f"Ficheiro alvo: {path}\n"
                f"Operação: {operation}\n"
                f"Código detetado: {bool(intake.get('code_blocks'))}\n"
            )
            code_blocks = intake.get("code_blocks") or []
            for index, block in enumerate(code_blocks, start=1):
                prompt += (
                    f"\nBloco {index} ({block.get('language')}):\n```{block.get('language')}\n"
                    f"{block.get('content', '')}\n```\n"
                )
            prompt += (
                "\nResponde dizendo claramente se é para substituir, adicionar, fazer patch ou criar ficheiro novo. "
                "Se houver conflito provável, pede validação explícita."
            )

        return {
            "ok": True,
            "mode": "browser_prompt",
            "target_surface": "browser_assisted_ai",
            "prompt": prompt,
            "repo": repo,
            "path": path,
            "operation": operation,
        }


browser_prompt_builder_v1 = BrowserPromptBuilderV1()
