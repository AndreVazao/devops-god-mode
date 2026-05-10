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
except ImportError:
    print("Backend modules not found. Running in standalone mock mode.")
    HAS_BACKEND = False

RELAY_URL = os.getenv("RELAY_URL", "https://devops-god-mode.vercel.app/api")
TOKEN = os.getenv("RELAY_TOKEN", "GODMODE_SECURE_TOKEN")

HEADERS = {
    "Authorization": f"Bearer {TOKEN}"
}

def fetch_tasks():
    try:
        # User requested /pull for pulling tasks in FIX 3
        r = requests.post(f"{RELAY_URL}/pull", headers=HEADERS, timeout=10)
        if r.status_code == 200:
            return r.json()
    except Exception as e:
        print(f"Error fetching tasks: {e}")
    return []

def send_response(data):
    try:
        # User requested /respond for sending responses in FIX 3
        requests.post(f"{RELAY_URL}/respond", json=data, headers=HEADERS, timeout=10)
    except Exception as e:
        print(f"Error sending response: {e}")

def execute_logic(task):
    if HAS_BACKEND:
        try:
            return run_task(task)
        except Exception as e:
            return {"error": str(e), "status": "failed"}
    else:
        return {"status": "done", "mock": True}

if __name__ == "__main__":
    print(f"Starting sync worker. Relay: {RELAY_URL}")
    while True:
        tasks = fetch_tasks()

        for t in tasks:
            print("Executing:", t)

            # The task might be wrapped in an object or be the object itself
            # Depending on how it was pushed.

            result = execute_logic(t)

            response_payload = {
                "task_id": t.get("id") or t.get("payload", {}).get("pipeline_id"),
                "result": result,
                "status": "done"
            }

            send_response(response_payload)

        time.sleep(3)
