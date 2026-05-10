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
        # Use POST /api/pull as defined in the new relay
        r = requests.post(f"{RELAY_URL}/pull", headers=HEADERS, timeout=10)
        if r.status_code == 200:
            return r.json()
        else:
            print(f"Error pulling tasks: {r.status_code} - {r.text}")
    except Exception as e:
        print(f"Connection error pulling tasks: {e}")
    return []

def send_response(data):
    try:
        # Use POST /api/respond as defined in the new relay
        r = requests.post(f"{RELAY_URL}/respond", json=data, headers=HEADERS, timeout=10)
        if r.status_code != 200:
            print(f"Error sending response: {r.status_code} - {r.text}")
    except Exception as e:
        print(f"Connection error sending response: {e}")

def execute_logic(task):
    print("TASK RECEIVED:", task)

    # Handle evolution approval specifically
    if task.get("action") == "approve":
        try:
            from app.evolution.approval import approve_locally
            plan_id = task.get("payload", {}).get("plan_id")
            if plan_id:
                approve_locally(plan_id)
                return {"status": "approved_locally", "plan_id": plan_id}
        except ImportError:
            pass

    # Handle setup_env specifically if needed, or let it flow to orchestrator
    if task.get("action") == "setup_env":
        # Example of handling a specific action
        return {"status": "setup_triggered", "details": "Environment setup initialized on PC"}

    if HAS_BACKEND:
        try:
            return run_task(task)
        except Exception as e:
            return {"error": str(e), "status": "failed"}
    else:
        # Standalone mock mode logic
        return {
            "task": task,
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
                "status": "done",
                "timestamp": time.time()
            }

            send_response(response_payload)

        time.sleep(2)
