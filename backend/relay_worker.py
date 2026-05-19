import json
import os
import subprocess
import sys
import tempfile
import time

import requests

# Add the parent directory to sys.path to import from app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from app.config import settings
    from app.services.execution_orchestrator import run_task

    HAS_BACKEND = True
    RELAY_URL = settings.RELAY_URL
    RELAY_CANDIDATES = getattr(settings, "RELAY_CANDIDATES", [settings.RELAY_URL])
    TOKEN = settings.RELAY_TOKEN
except ImportError:
    print("Backend modules not found. Running in standalone mode.")
    HAS_BACKEND = False
    RELAY_URL = os.getenv("RELAY_URL", "https://devops-god-mode.vercel.app/api")
    RELAY_CANDIDATES = [
        f"http://127.0.0.1:{os.getenv('APP_PORT', '8000')}/api",
        f"http://{os.getenv('TAILSCALE_PC_IP', '100.69.225.48')}:{os.getenv('APP_PORT', '8000')}/api",
        os.getenv("RENDER_RELAY_URL", "").rstrip("/"),
        RELAY_URL,
    ]
    TOKEN = os.getenv("RELAY_TOKEN", "GODMODE_SECURE_TOKEN")

HEADERS = {
    "Authorization": f"Bearer {TOKEN}"
}

# =========================
# MEMORY
# =========================
MEMORY_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "brain_memory.json")


def relay_candidates():
    unique = []
    for item in RELAY_CANDIDATES:
        normalized = (item or "").rstrip("/")
        if normalized and normalized not in unique:
            unique.append(normalized)
    return unique


def load_memory():
    if not os.path.exists(MEMORY_FILE):
        os.makedirs(os.path.dirname(MEMORY_FILE), exist_ok=True)
        return {}
    try:
        with open(MEMORY_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return {}


def save_memory(mem):
    with open(MEMORY_FILE, "w") as f:
        json.dump(mem, f, indent=2)


memory = load_memory()

# =========================
# EXECUTOR (SANDBOX)
# =========================
def run_python(code):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".py") as f:
        f.write(code.encode())
        path = f.name

    try:
        result = subprocess.run(
            [sys.executable, path],
            capture_output=True,
            text=True,
            timeout=15
        )
        return result.stdout + result.stderr
    except Exception as e:
        return str(e)
    finally:
        if os.path.exists(path):
            os.remove(path)

# =========================
# PLANNER (INTELIGENCIA)
# =========================
def decide(task):
    action = task.get("action")
    if action:
        return action

    text = (task.get("content") or task.get("message") or "").lower()

    if "criar ficheiro" in text or "write file" in text:
        return "write_file"

    if "executar código" in text or "run code" in text or "python" in text:
        return "run_code"

    if "guardar" in text or "lembra-te" in text:
        return "memory"

    return "chat"

# =========================
# ACTIONS
# =========================
def action_run_code(task):
    code = task.get("code") or task.get("content") or task.get("payload", {}).get("code")
    if not code and task.get("action") == "run_code":
        code = task.get("content") or task.get("message")

    output = run_python(code)
    return {
        "role": "gm",
        "text": f"Resultado da execução:\n```\n{output}\n```",
        "type": "text"
    }


def action_memory(task):
    content = task.get("content") or task.get("message")
    memory[str(time.time())] = content
    save_memory(memory)
    return {
        "role": "gm",
        "text": "Entendido. Guardei essa informação na minha memória persistente.",
        "type": "text"
    }


def pull_tasks():
    for relay_url in relay_candidates():
        try:
            response = requests.get(f"{relay_url}/pull", headers=HEADERS, timeout=10)
            if response.status_code == 200:
                data = response.json()
                return relay_url, data if isinstance(data, list) else []
            if response.status_code == 403:
                print("Unauthorized while pulling tasks. Check RELAY_TOKEN.")
                return relay_url, []
        except Exception as exc:
            print(f"Connection error pulling tasks via {relay_url}: {exc}")
    return RELAY_URL, []


def send_response(relay_url, task, result):
    try:
        payload = {
            "task": task,
            "result": result,
            "worker": {
                "source": "backend.relay_worker",
                "relay_url": relay_url
            }
        }
        response = requests.post(f"{relay_url}/respond", json=payload, headers=HEADERS, timeout=10)
        if response.status_code != 200:
            print(f"Error sending response: {response.status_code} - {response.text}")
    except Exception as exc:
        print(f"Connection error sending response: {exc}")


def execute_logic(task):
    print("EXECUTING TASK:", task)

    decision = decide(task)
    print(f"DECISION: {decision}")

    if decision == "run_code":
        return action_run_code(task)

    if decision == "memory":
        return action_memory(task)

    if HAS_BACKEND:
        try:
            result = run_task(task)
            return {
                "role": "gm",
                "text": result.get("message") or result.get("content") or str(result),
                "type": result.get("type", "text")
            }
        except Exception as exc:
            return {"role": "gm", "text": f"Erro no processamento: {str(exc)}", "type": "text"}

    return {
        "role": "gm",
        "text": f"Processado (Mock): {task.get('content') or task.get('message') or decision}",
        "type": "text"
    }


if __name__ == "__main__":
    print(f"Starting God Mode Brain (Worker Mode). Relay candidates: {relay_candidates()}")
    while True:
        try:
            relay_url, tasks = pull_tasks()
            for task in tasks:
                result = execute_logic(task)
                send_response(relay_url, task, result)
        except Exception as exc:
            print(f"Loop error: {exc}")

        time.sleep(2)
