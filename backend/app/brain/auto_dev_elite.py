import requests
import time
from app.config import settings
from app.brain.planner import create_plan
from app.brain.agent_pool import run_step
from app.brain.executor import run_plan
from app.brain.validator import validate
from app.semantic.vector_memory import add, search

BASE = f"{settings.RELAY_URL}/cluster"
HEADERS = {"Authorization": f"Bearer {settings.RELAY_TOKEN}"}

def enqueue_task(content, role="dev", priority=5, chatId="global"):
    task = {
        "role": role,
        "content": content,
        "priority": priority,
        "chatId": chatId
    }
    try:
        requests.post(f"{BASE}/queue", json=task, headers=HEADERS, timeout=5)
    except: pass

def check_consensus(task_id, decision="approve"):
    try:
        r = requests.post(f"{BASE}/consensus", json={
            "task_id": task_id,
            "node_id": "master-brain",
            "decision": decision
        }, headers=HEADERS, timeout=5)
        return r.json().get("approved", False)
    except: return False

def auto_dev(task, chatId="global"):
    context = search(task)
    context_str = "\n".join(context)

    full_task = f"Contexto: {context_str}\nObjetivo: {task}"

    for attempt in range(3):
        steps, plan_source = create_plan(full_task)

        # Determine if we should use cluster or local execution
        # For this phase, let's distribute to the cluster
        for step in steps:
            role = "dev"
            priority = 5
            if "deploy" in step.lower() or "infra" in step.lower():
                role = "infra"
                priority = 3
            elif "erro" in step.lower() or "bug" in step.lower():
                role = "debug"
                priority = 2

            if "delete" in step.lower() or "remove" in step.lower() or "deploy" in step.lower():
                 # Critical actions should ideally wait for consensus
                 # Here we just flag or enqueue with high priority after consensus
                 print(f"⚠️ Critical step detected: {step}")

            enqueue_task(step, role=role, priority=priority, chatId=chatId)

        # local validation for summary (could be async later)
        # For now, we return a pending status since it's distributed
        return {
            "status": "distributed",
            "plan": steps,
            "summary": "Tarefas enviadas para o cluster de workers.",
            "source": plan_source,
            "elite": True
        }

    return {"status": "failed"}
