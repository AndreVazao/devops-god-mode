from typing import Any


class WorkflowErrorIntakeV1:
    def parse(self, payload: dict[str, Any]) -> dict[str, Any]:
        source = payload.get("source") or "unknown"
        repo_full_name = payload.get("repo_full_name")
        error_text = (payload.get("error_text") or "").strip()
        lowered = error_text.lower()

        category = "unknown"
        probable_cause = "Análise manual necessária."
        suggested_fix = "Rever logs completos e comparar com ficheiros alvo."

        if "uvicorn: command not found" in lowered:
            category = "runtime_command_misplaced"
            probable_cause = "Start command foi usado em contexto de build ou dependência não instalada no estágio esperado."
            suggested_fix = "Separar build command e start command; garantir instalação antes do arranque."
        elif "module not found" in lowered or "cannot find module" in lowered:
            category = "missing_dependency_or_path"
            probable_cause = "Dependência ausente, import incorreto ou path errado."
            suggested_fix = "Verificar imports, package manager e ficheiro alvo referido no erro."
        elif "syntax error" in lowered or "syntaxerror" in lowered:
            category = "syntax_error"
            probable_cause = "Erro de sintaxe num ficheiro alterado recentemente."
            suggested_fix = "Abrir o ficheiro citado e corrigir sintaxe antes de novo build."
        elif "health check" in lowered and "timeout" in lowered:
            category = "startup_health_timeout"
            probable_cause = "Serviço arranca lentamente, porta errada ou health path incorreto."
            suggested_fix = "Validar health path, start command, porta e tempo de arranque."
        elif "permission denied" in lowered:
            category = "permission_issue"
            probable_cause = "Permissão de execução ou acesso insuficiente."
            suggested_fix = "Rever permissões, scripts executáveis e credenciais do ambiente."

        return {
            "ok": True,
            "mode": "workflow_error_intake",
            "source": source,
            "repo_full_name": repo_full_name,
            "category": category,
            "probable_cause": probable_cause,
            "suggested_fix": suggested_fix,
            "requires_external_ai": category == "unknown",
            "log_excerpt": error_text[:1200],
        }


workflow_error_intake_v1 = WorkflowErrorIntakeV1()
