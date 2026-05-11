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
        # GET /api/pull now returns { "items": [...] }
        r = requests.get(f"{RELAY_URL}/pull", headers=HEADERS, timeout=10)
        if r.status_code == 200:
            data = r.json()
            return data.get("items", [])
        else:
            print(f"Error pulling tasks: {r.status_code} - {r.text}")
    except Exception as e:
        print(f"Connection error pulling tasks: {e}")
    return []

def send_response(data):
    try:
        # POST /api/respond for sending results back
        r = requests.post(f"{RELAY_URL}/respond", json=data, headers=HEADERS, timeout=10)
        if r.status_code != 200:
            print(f"Error sending response: {r.status_code} - {r.text}")
    except Exception as e:
        print(f"Connection error sending response: {e}")

def execute_logic(task):
    print("TASK RECEIVED:", task)

    action = task.get("action")
    payload = task.get("payload", {})

    # Handle evolution approval specifically
    if action == "approve":
        try:
            from app.evolution.approval import approve_locally
            plan_id = payload.get("plan_id")
            if plan_id:
                approve_locally(plan_id)
                return {"status": "approved_locally", "plan_id": plan_id, "message": f"Plano {plan_id} aprovado localmente."}

            # Handle mobile gate approval (action_id)
            action_id = payload.get("action_id")
            decision = payload.get("decision")
            if action_id:
                # Logic to release a gated action could go here
                return {"status": "decision_recorded", "action_id": action_id, "decision": decision, "message": f"Decisão {decision} registada para {action_id}."}
        except Exception as e:
            return {"error": str(e), "status": "failed"}

    if action == "setup_env":
        return {"status": "setup_triggered", "message": "Ambiente do PC a ser preparado..."}

    if HAS_BACKEND:
        try:
            # The orchestrator handles chat and other actions
            return run_task(task)
        except Exception as e:
            return {"error": str(e), "status": "failed"}
    else:
        # Standalone mock mode logic
        return {
            "message": f"PC processou: {action}",
            "status": "done",
            "mock": True
        }

if __name__ == "__main__":
    if not RELAY_URL:
        print("CRITICAL: RELAY_URL not configured. Check your .env file.")
        sys.exit(1)

    print(f"Starting Production Relay Worker. Relay: {RELAY_URL}")
    while True:
        tasks = pull_tasks()

        for task in tasks:
            result = execute_logic(task)

            # Wrap result as requested or expected by mobile
            response_payload = {
                "task": task,
                "result": result,
                "chat_id": task.get("chat_id"),
                "status": "done",
                "timestamp": time.time()
            }

            send_response(response_payload)

        time.sleep(2)
