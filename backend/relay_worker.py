import requests
import time
import os
import sys
import subprocess
import tempfile
import json

# Add the parent directory to sys.path to import from app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from app.services.execution_orchestrator import run_task
    from app.config import settings
    HAS_BACKEND = True
    RELAY_URL = settings.RELAY_URL
    TOKEN = settings.RELAY_TOKEN
except ImportError:
    print("Backend modules not found. Running in standalone mode.")
    HAS_BACKEND = False
    RELAY_URL = os.getenv("RELAY_URL", "https://devops-god-mode.vercel.app/api")
    TOKEN = os.getenv("RELAY_TOKEN", "GODMODE_SECURE_TOKEN")

HEADERS = {
    "Authorization": f"Bearer {TOKEN}"
}

# =========================
# MEMORY
# =========================
MEMORY_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "brain_memory.json")

def load_memory():
    if not os.path.exists(MEMORY_FILE):
        os.makedirs(os.path.dirname(MEMORY_FILE), exist_ok=True)
        return {}
    try:
        with open(MEMORY_FILE, "r") as f:
            return json.load(f)
    except:
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
# PLANNER (INTELIGÊNCIA)
# =========================
def decide(task):
    action = task.get("action")
    if action: return action

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
         # Extract from text if possible or use the text as code
         code = task.get("content") or task.get("message")

    output = run_python(code)
    return {
        "role": "gm",
        "text": f"💻 Resultado da execução:\n```\n{output}\n```",
        "type": "text"
    }

def action_memory(task):
    content = task.get("content") or task.get("message")
    memory[str(time.time())] = content
    save_memory(memory)
    return {
        "role": "gm",
        "text": "🧠 Entendido. Guardei essa informação na minha memória persistente.",
        "type": "text"
    }

def pull_tasks():
    try:
        r = requests.get(f"{RELAY_URL}/relay", headers=HEADERS, timeout=10)
        if r.status_code == 200:
            data = r.json()
            return data.get("items", [])
    except Exception as e:
        print(f"Connection error pulling tasks: {e}")
    return []

def send_response(chat_id, result):
    try:
        payload = {
            "type": "MESSAGE",
            "payload": {
                "chatId": chat_id or "default",
                "message": result
            }
        }
        r = requests.post(f"{RELAY_URL}/state", json=payload, headers=HEADERS, timeout=10)
        if r.status_code != 200:
            print(f"Error sending response: {r.status_code} - {r.text}")
    except Exception as e:
        print(f"Connection error sending response: {e}")

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
            res = run_task(task)
            return {
                "role": "gm",
                "text": res.get("message") or res.get("content") or str(res),
                "type": res.get("type", "text")
            }
        except Exception as e:
            return {"role": "gm", "text": f"Erro no processamento: {str(e)}", "type": "text"}
    else:
        return {
            "role": "gm",
            "text": f"🤖 Processado (Mock): {task.get('content') or task.get('message') or decision}",
            "type": "text"
        }

if __name__ == "__main__":
    print(f"Starting God Mode Brain (Worker Mode). Relay: {RELAY_URL}")
    while True:
        try:
            tasks = pull_tasks()
            for task in tasks:
                result = execute_logic(task)
                send_response(task.get("chat_id") or task.get("chatId"), result)
        except Exception as e:
            print(f"Loop error: {e}")

        time.sleep(2)
