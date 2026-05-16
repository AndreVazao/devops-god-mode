import requests
import time
from app.config import settings
from app.brain.agents.core.agents_registry import AGENTS
from app.brain.agents.core.planner import create_agent_plan

VERCEL_LOG = f"{settings.RELAY_URL}/logs"
VERCEL_STATE = f"{settings.RELAY_URL}/state"
HEADERS = {"Authorization": f"Bearer {settings.RELAY_TOKEN}", "Content-Type": "application/json"}

def log_remote(msg):
    try:
        requests.post(VERCEL_LOG, json={"text": msg}, headers=HEADERS, timeout=5)
    except:
        pass

def update_agent_status(agent_name, status, output=""):
    try:
        # Update Vercel state with agent status
        # This assumes the UI/Relay can handle this type of update
        payload = {
            "type": "UPDATE_AGENTS",
            "payload": {
                "name": agent_name,
                "status": status,
                "output": str(output)[:500]
            }
        }
        requests.post(VERCEL_STATE, json=payload, headers=HEADERS, timeout=5)
    except:
        pass

def run_task(task, chatId="global"):
    plan = create_agent_plan(task)
    context = {}
    results = []

    log_remote(f"🧠 [Orchestrator] Iniciando plano para: {task}")

    for step in plan:
        agent_key = step["agent"]
        if agent_key not in AGENTS:
            continue

        agent = AGENTS[agent_key]
        log_remote(f"🤖 {agent.name} iniciou: {step['task']}")
        update_agent_status(agent.name, "active", f"Executando: {step['task']}")

        try:
            result = agent.run(step["task"], context)
            update_agent_status(agent.name, "done", result)
            log_remote(f"✅ {agent.name} terminou com sucesso")

            context[agent.name] = result
            results.append({
                "agent": agent.name,
                "task": step["task"],
                "result": result,
                "status": "success"
            })
        except Exception as e:
            error_msg = f"Erro em {agent.name}: {str(e)}"
            log_remote(f"❌ {error_msg}")
            update_agent_status(agent.name, "error", error_msg)
            results.append({
                "agent": agent.name,
                "task": step["task"],
                "result": error_msg,
                "status": "failed"
            })
            # Decide if we should continue or stop (stopping for now)
            break

    return {
        "status": "completed",
        "task": task,
        "steps": results,
        "summary": f"Execução concluída com {len(results)} passos."
    }
