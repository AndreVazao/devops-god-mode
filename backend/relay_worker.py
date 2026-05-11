import requests
import time
import os
import sys

# Add the parent directory to sys.path to import from app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from app.services.execution_orchestrator import run_task
    from app.config import settings
    HAS_BACKEND = True
    RELAY_URL = settings.RELAY_URL
    TOKEN = settings.RELAY_TOKEN
except ImportError:
    print("Backend modules not found. Running in standalone mock mode.")
    HAS_BACKEND = False
    RELAY_URL = os.getenv("RELAY_URL", "https://devops-god-mode.vercel.app/api")
    TOKEN = os.getenv("RELAY_TOKEN", "GODMODE_SECURE_TOKEN")

HEADERS = {
    "Authorization": f"Bearer {TOKEN}"
}

def pull_tasks():
    try:
        r = requests.get(f"{RELAY_URL}/relay", headers=HEADERS, timeout=10)
        if r.status_code == 200:
            data = r.json()
            return data.get("items", [])
        else:
            print(f"Error pulling tasks: {r.status_code} - {r.text}")
    except Exception as e:
        print(f"Connection error pulling tasks: {e}")
    return []

def send_response(chat_id, result):
    try:
        # PC now posts directly to /api/state to update history
        payload = {
            "type": "MESSAGE",
            "payload": {
                "chatId": chat_id or "auto",
                "message": {
                    "role": "gm",
                    "text": result.get("message") or result.get("content") or str(result),
                    "type": result.get("type", "text"),
                    "actionId": result.get("action_id")
                }
            }
        }
        r = requests.post(f"{RELAY_URL}/state", json=payload, headers=HEADERS, timeout=10)
        if r.status_code != 200:
            print(f"Error sending response: {r.status_code} - {r.text}")
    except Exception as e:
        print(f"Connection error sending response: {e}")

def execute_logic(task):
    print("TASK RECEIVED:", task)

    action = task.get("action")
    payload = task.get("payload", {})

    if action == "file":
        filename = payload.get("name")
        content = payload.get("content")
        print(f"FILE RECEIVED: {filename} ({len(content)} bytes)")
        # In a real scenario, we might save this file
        return {"message": f"Ficheiro {filename} recebido e processado no PC.", "status": "done"}

    if action == "approve":
        try:
            from app.evolution.approval import approve_locally
            plan_id = payload.get("plan_id")
            if plan_id:
                approve_locally(plan_id)
                return {"message": f"Plano {plan_id} aprovado localmente.", "status": "approved_locally"}

            action_id = payload.get("action_id")
            decision = payload.get("decision")
            if action_id:
                return {"message": f"Decisão {decision} registada para {action_id}.", "status": "decision_recorded"}
        except Exception as e:
            return {"message": f"Erro na aprovação: {str(e)}", "status": "failed"}

    if action == "setup_env":
        return {"message": "Ambiente do PC a ser preparado...", "status": "setup_triggered"}

    if HAS_BACKEND:
        try:
            return run_task(task)
        except Exception as e:
            return {"message": f"Erro: {str(e)}", "status": "failed"}
    else:
        return {
            "message": f"PC processou: {action}",
            "status": "done",
            "mock": True
        }

if __name__ == "__main__":
    if not RELAY_URL:
        print("CRITICAL: RELAY_URL not configured. Check your .env file.")
        sys.exit(1)

    print(f"Starting Phase 230 Relay Worker. Relay: {RELAY_URL}")
    while True:
        tasks = pull_tasks()

        for task in tasks:
            result = execute_logic(task)
            send_response(task.get("chat_id"), result)

        time.sleep(2)
