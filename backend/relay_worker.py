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
import time
import requests
import os

RELAY_URL = os.getenv("RELAY_URL")
TOKEN = os.getenv("RELAY_TOKEN")

def pull_tasks():
    headers = {}
    if TOKEN:
        headers["Authorization"] = f"Bearer {TOKEN}"
    r = requests.get(f"{RELAY_URL}/pull-tasks", headers=headers)
    return r.json().get("tasks", [])


def push_result(result):
    headers = {}
    if TOKEN:
        headers["Authorization"] = f"Bearer {TOKEN}"
    requests.post(f"{RELAY_URL}/push-result", json=result, headers=headers)


def execute(task):
    print("Executar:", task)

    if task.get("action") == "ping":
        return {"status": "pong"}

    if task.get("action") == "run_code":
        try:
            # Note: exec() is dangerous, used here as requested for the prototype
            exec(task["code"])
            return {"status": "done"}
        except Exception as e:
            return {"error": str(e)}

    if task.get("action") == "chat":
        return {"type": "chat_response", "message": f"PC recebeu: {task.get('message')}"}

    return {"status": "unknown"}


def loop():
    print(f"Worker ligado ao relay: {RELAY_URL}")

    while True:
        try:
            tasks = pull_tasks()

            for t in tasks:
                result = execute(t)
                push_result(result)

        except Exception as e:
            print("Erro:", e)

        time.sleep(2)


if __name__ == "__main__":
    if not RELAY_URL:
        print("Erro: RELAY_URL não configurada.")
    else:
        loop()
