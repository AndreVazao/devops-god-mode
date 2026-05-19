from __future__ import annotations

from typing import Any, Dict, Optional

from app.brain.god_brain import think
from app.brain.operational_state import add_goal, load_state

from .autonomous_dev_loop_service import run_dev_loop
from .github_write_agent import create_branch, commit_all, push_branch
from .local_executor_service import execute_code

PROVIDER_HINTS = {
    "chatgpt": "generalist planning, coding help and structured execution",
    "grok": "live-web style reasoning, current-event sanity checks and broad discovery",
    "gemini": "google ecosystem workflows, multimodal input and product integration",
    "claude": "long-form reasoning, review quality and specification refinement",
    "deepseek": "strong coding focus, implementation detail and cost-aware iteration",
    "perplexity": "research-first flow, citations and quick source-driven synthesis",
}

AGENT_HINTS = {
    "planner": "define a concrete execution plan with milestones and ordering",
    "dispatcher": "decide which worker or subsystem should take each step",
    "frontend-agent": "focus on interface, shell behavior, UX flows and browser state",
    "backend-agent": "focus on APIs, orchestration, queues, services and persistence",
    "integration-agent": "focus on contracts, payloads, connectors and interoperability",
    "qa-agent": "focus on regressions, smoke tests, edge cases and verification",
    "review-agent": "focus on risks, code review findings and hidden regressions",
    "deploy-agent": "focus on deployment flow, environment checks and release safety",
    "incident-agent": "focus on diagnosis, recovery and operational containment",
}

DEPLOYER_HINTS = {
    "vercel": "optimize for web deployment, routing, edge behavior and production rollout on Vercel",
    "supabase": "optimize for database, auth, storage, edge functions and Supabase operations",
    "render": "optimize for backend services, workers and runtime hosting on Render",
    "cloudflare": "optimize for DNS, edge, tunnels and Cloudflare platform concerns",
    "github-actions": "optimize for CI pipelines, automation and release workflows",
}


def _normalize_repo_name(repo: Optional[str], repo_path: Optional[str] = None) -> str:
    candidate = (repo or repo_path or "default").strip()
    candidate = candidate.replace("\\", "/").rstrip("/")
    if "/" in candidate:
        candidate = candidate.split("/")[-1]
    sanitized = "".join(ch.lower() if ch.isalnum() else "_" for ch in candidate).strip("_")
    return sanitized or "default"


def _task_context(task: Dict[str, Any], repo_path: Optional[str] = None) -> Dict[str, str]:
    repo = (task.get("repo") or task.get("repository") or repo_path or "default").strip()
    provider = (task.get("provider") or "chatgpt").strip().lower()
    worker_view = (task.get("worker_view") or "agents").strip().lower()
    agent = (task.get("agent") or "planner").strip().lower()
    deployer = (task.get("deployer") or "vercel").strip().lower()
    project_name = _normalize_repo_name(repo, repo_path)
    return {
        "repo": repo or "default",
        "provider": provider,
        "worker_view": worker_view,
        "agent": agent,
        "deployer": deployer,
        "project_name": project_name,
    }


def _state_summary(project_name: str) -> Dict[str, Any]:
    state = load_state(project_name)
    goals = state.get("goals", [])
    active = [goal for goal in goals if goal.get("status") == "active"]
    completed = [goal for goal in goals if goal.get("status") == "completed"]
    return {
        "project": project_name,
        "goals_total": len(goals),
        "goals_active": len(active),
        "goals_completed": len(completed),
        "latest_goal": goals[-1]["text"] if goals else None,
        "last_update": state.get("last_update"),
        "state": state,
    }


def _context_brief(ctx: Dict[str, str]) -> str:
    provider_hint = PROVIDER_HINTS.get(ctx["provider"], "general reasoning and execution guidance")
    agent_hint = AGENT_HINTS.get(ctx["agent"], "general orchestration support")
    deployer_hint = DEPLOYER_HINTS.get(ctx["deployer"], "general deployment guidance")
    return (
        f"Projeto alvo: {ctx['repo']}\n"
        f"Provider preferido: {ctx['provider']} ({provider_hint})\n"
        f"Vista de worker: {ctx['worker_view']}\n"
        f"Agent ativo: {ctx['agent']} ({agent_hint})\n"
        f"Deployer ativo: {ctx['deployer']} ({deployer_hint})"
    )


def _compose_goal(message: str, ctx: Dict[str, str], mode: str = "execution") -> str:
    if mode == "review":
        opener = "Faz uma revisão operacional e técnica, priorizando riscos, regressões e passos concretos."
    elif mode == "deploy":
        opener = "Prepara um plano de deploy e verificação, incluindo riscos, pré-checks e rollback."
    elif mode == "plan":
        opener = "Transforma o pedido num plano faseado com prioridades e validação."
    else:
        opener = "Trabalha o pedido como operador DevOps autónomo e propõe a próxima melhor sequência de execução."

    return (
        f"{opener}\n\n"
        f"{_context_brief(ctx)}\n\n"
        f"Pedido do utilizador: {message}\n\n"
        "Responde com foco prático no projeto alvo, evitando genericidade."
    )


def _safe_think(goal: str, chat_id: str) -> Dict[str, Any]:
    try:
        result = think(goal, chatId=chat_id)
        return {"ok": True, "result": result}
    except Exception as exc:
        return {"ok": False, "error": str(exc)}


def _build_status_response(ctx: Dict[str, str]) -> Dict[str, Any]:
    summary = _state_summary(ctx["project_name"])
    message = (
        f"God Mode online para {ctx['repo']}. "
        f"Provider {ctx['provider']}, agent {ctx['agent']}, deployer {ctx['deployer']}. "
        f"Backlog: {summary['goals_active']} ativo(s), {summary['goals_completed']} concluído(s)."
    )
    return {
        "type": "chat_response",
        "message": message,
        "context": ctx,
        "summary": summary,
    }


def _build_chat_response(task: Dict[str, Any], repo_path: Optional[str] = None) -> Dict[str, Any]:
    message = task.get("message") or task.get("payload", {}).get("message") or task.get("text") or ""
    normalized = message.strip()
    lowered = normalized.lower()
    chat_id = task.get("chat_id") or task.get("chatId", "global")
    ctx = _task_context(task, repo_path)

    if not normalized:
        return {
            "type": "chat_response",
            "message": "Recebi uma mensagem vazia. Envia um objetivo, problema ou pedido de plano.",
            "context": ctx,
        }

    if lowered in {"status", "health", "estado"}:
        return _build_status_response(ctx)

    if lowered.startswith("goal:") or lowered.startswith("objetivo:"):
        _, _, goal_text = normalized.partition(":")
        goal_text = goal_text.strip()
        if not goal_text:
            return {
                "type": "chat_response",
                "message": "Faltou o texto do objetivo depois de goal:.",
                "context": ctx,
            }

        state = add_goal(goal_text, project_name=ctx["project_name"])
        return {
            "type": "chat_response",
            "message": f"Objetivo registado em {ctx['repo']}: {goal_text}",
            "context": ctx,
            "state": state,
        }

    if lowered.startswith("think:"):
        _, _, prompt = normalized.partition(":")
        prompt = prompt.strip()
        if not prompt:
            return {
                "type": "chat_response",
                "message": "Faltou o texto depois de think:.",
                "context": ctx,
            }

        thought = _safe_think(_compose_goal(prompt, ctx, mode="plan"), chat_id)
        if thought["ok"]:
            return {
                "type": "chat_response",
                "message": "Análise contextual concluída.",
                "context": ctx,
                "analysis": thought["result"],
            }

        state = add_goal(prompt, project_name=ctx["project_name"])
        return {
            "type": "chat_response",
            "message": f"Não consegui executar think agora: {thought['error']}. O pedido ficou registado no backlog de {ctx['repo']}.",
            "context": ctx,
            "state": state,
        }

    mode = "execution"
    if any(token in lowered for token in ["review", "rever", "auditoria", "audit"]):
        mode = "review"
    elif any(token in lowered for token in ["deploy", "publicar", "release", "rollout"]):
        mode = "deploy"
    elif any(token in lowered for token in ["plan", "plano", "organiza", "prioriza"]):
        mode = "plan"

    enriched_goal = _compose_goal(normalized, ctx, mode=mode)
    thought = _safe_think(enriched_goal, chat_id)
    if thought["ok"]:
        result = thought["result"]
        summary = result.get("summary") or result.get("status") or "Plano gerado."
        return {
            "type": "chat_response",
            "message": f"God Mode preparou resposta operacional para {ctx['repo']}: {summary}",
            "context": ctx,
            "analysis": result,
        }

    state = add_goal(normalized, project_name=ctx["project_name"])
    return {
        "type": "chat_response",
        "message": (
            f"Não consegui ativar a análise avançada agora ({thought['error']}). "
            f"Mesmo assim registei o pedido no backlog operacional de {ctx['repo']}."
        ),
        "context": ctx,
        "state": state,
    }


def run_task(task: Dict[str, Any], repo_path: str = None) -> Dict[str, Any]:
    action = task.get("action")
    ctx = _task_context(task, repo_path)

    if action == "execute_code":
        code = task.get("code")
        if not code:
            return {"error": "no code provided", "context": ctx}
        result = execute_code(code, repo_path=repo_path)
        if isinstance(result, dict):
            result.setdefault("context", ctx)
        return result

    if action == "dev_loop":
        result = run_dev_loop(task, repo_path=repo_path)
        if isinstance(result, dict):
            result.setdefault("context", ctx)
        return result

    if action == "think":
        goal = task.get("payload", {}).get("goal") or task.get("goal")
        chat_id = task.get("chat_id") or task.get("chatId", "global")
        if not goal:
            return {"error": "no goal provided for think action", "context": ctx}
        result = think(_compose_goal(goal, ctx, mode="plan"), chatId=chat_id)
        if isinstance(result, dict):
            result.setdefault("context", ctx)
        return result

    if action == "goal":
        text = task.get("payload", {}).get("text") or task.get("text")
        if not text:
            return {"error": "no text provided for goal action", "context": ctx}
        return {
            "status": "goal_added",
            "context": ctx,
            "state": add_goal(text, project_name=ctx["project_name"]),
        }

    if action == "chat":
        return _build_chat_response(task, repo_path=repo_path)

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
            "context": ctx,
            "commit_stdout": commit_res.stdout,
            "commit_stderr": commit_res.stderr,
            "push_stdout": push_res.stdout,
            "push_stderr": push_res.stderr,
        }

    return {"error": f"unknown action: {action}", "context": ctx}
