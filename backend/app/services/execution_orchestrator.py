from typing import Any, Dict

from app.brain.god_brain import think
from app.brain.operational_state import add_goal

from .autonomous_dev_loop_service import run_dev_loop
from .github_write_agent import create_branch, commit_all, push_branch
from .local_executor_service import execute_code


def _build_chat_response(message: str) -> Dict[str, Any]:
    normalized = (message or "").strip()
    lowered = normalized.lower()

    if not normalized:
        return {
            "type": "chat_response",
            "message": "Recebi uma mensagem vazia. Envia um objetivo ou comando curto.",
        }

    if lowered in {"status", "health", "estado"}:
        return {
            "type": "chat_response",
            "message": "God Mode online. O relay cloud responde e o backend local pode continuar a processar tarefas.",
        }

    if lowered.startswith("goal:") or lowered.startswith("objetivo:"):
        _, _, goal_text = normalized.partition(":")
        goal_text = goal_text.strip()
        if not goal_text:
            return {
                "type": "chat_response",
                "message": "Faltou o texto do objetivo depois de goal:.",
            }

        state = add_goal(goal_text)
        return {
            "type": "chat_response",
            "message": f"Objetivo registado: {goal_text}",
            "state": state,
        }

    if lowered.startswith("think:"):
        _, _, prompt = normalized.partition(":")
        prompt = prompt.strip()
        if not prompt:
            return {
                "type": "chat_response",
                "message": "Faltou o texto depois de think:.",
            }

        try:
            result = think(prompt)
            return {
                "type": "chat_response",
                "message": "Análise concluída.",
                "analysis": result,
            }
        except Exception as exc:
            return {
                "type": "chat_response",
                "message": f"Não consegui executar think agora: {exc}",
            }

    state = add_goal(normalized)
    return {
        "type": "chat_response",
        "message": f"Pedido recebido e adicionado ao backlog operacional: {normalized}",
        "state": state,
    }


def run_task(task: Dict[str, Any], repo_path: str = None) -> Dict[str, Any]:
    action = task.get("action")

    if action == "execute_code":
        code = task.get("code")
        if not code:
            return {"error": "no code provided"}
        return execute_code(code, repo_path=repo_path)

    if action == "dev_loop":
        return run_dev_loop(task, repo_path=repo_path)

    if action == "think":
        goal = task.get("payload", {}).get("goal") or task.get("goal")
        if not goal:
            return {"error": "no goal provided for think action"}
        return think(goal)

    if action == "goal":
        text = task.get("payload", {}).get("text") or task.get("text")
        if not text:
            return {"error": "no text provided for goal action"}
        return {"status": "goal_added", "state": add_goal(text)}

    if action == "chat":
        message = task.get("message") or task.get("payload", {}).get("message") or task.get("text")
        return _build_chat_response(message)

    if action == "git_commit":
        branch = task.get("branch", "auto-branch")
        message = task.get("message", "auto commit")

        cb_res = create_branch(branch)
        if cb_res.returncode != 0 and b"already exists" not in cb_res.stderr.encode():
            pass

        commit_res = commit_all(message)
        push_res = push_branch(branch)

        return {
            "status": "git_done",
            "branch": branch,
            "commit_stdout": commit_res.stdout,
            "commit_stderr": commit_res.stderr,
            "push_stdout": push_res.stdout,
            "push_stderr": push_res.stderr,
        }

    return {"error": f"unknown action: {action}"}
