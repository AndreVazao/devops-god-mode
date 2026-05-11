import os
import time
import requests
import random
from app.config import settings
from app.brain.agent_pool import run_step

BASE = f"{settings.RELAY_URL}/cluster"
HEADERS = {"Authorization": f"Bearer {settings.RELAY_TOKEN}"}
NODE_ID = os.getenv("NODE_ID", f"pc-{random.randint(100, 999)}")
ROLE = os.getenv("NODE_ROLE", "dev")

def register():
    try:
        requests.post(f"{BASE}/register", json={
            "node_id": NODE_ID,
            "role": ROLE,
            "status": "online"
        }, headers=HEADERS, timeout=5)
    except: pass

def heartbeat():
    try:
        requests.post(f"{BASE}/register", json={
            "node_id": NODE_ID,
            "status": "online"
        }, headers=HEADERS, timeout=5)
    except: pass

def execute(task):
    print(f"⚙️ [{NODE_ID}/{ROLE}] Executing: {task['content']}")
    try:
        # Usa o pool de agentes real
        result_data = run_step(task['content'])
        ok = "error" not in str(result_data).lower()
        return ok, result_data.get("result", str(result_data))
    except Exception as e:
        return False, str(e)

def send_response_to_chat(chat_id, message_text, role, node_id):
    try:
        payload = {
            "type": "MESSAGE",
            "payload": {
                "chatId": chat_id,
                "message": {
                    "role": "gm",
                    "text": f"✅ {node_id} ({role}): {message_text}",
                    "metadata": {"cluster": True, "node": node_id, "role": role}
                }
            }
        }
        requests.post(f"{settings.RELAY_URL}/state", json=payload, headers=HEADERS, timeout=5)
    except: pass

if __name__ == "__main__":
    print(f"🐝 Cluster Worker {NODE_ID} ({ROLE}) started.")
    register()

    while True:
        try:
            r = requests.get(f"{BASE}/queue?role={ROLE}&node_id={NODE_ID}", headers=HEADERS, timeout=10)
            data = r.json()
            task = data.get("task")

            if task:
                t0 = time.time()
                ok, result = execute(task)
                latency = int((time.time() - t0) * 1000)

                # Report Metrics
                requests.post(f"{BASE}/metrics", json={"latency": latency, "cost": 0.001, "ok": ok}, headers=HEADERS, timeout=5)
                # Report Budget
                requests.post(f"{BASE}/budget", json={"cost": 0.001}, headers=HEADERS, timeout=5)
                # Ack Task
                requests.put(f"{BASE}/queue", json={"task_id": task["id"], "ok": ok, "task": task}, headers=HEADERS, timeout=5)

                # Update UI
                send_response_to_chat(task.get("chatId", "global"), result, ROLE, NODE_ID)

            heartbeat()
        except Exception as e:
            print(f"Worker error: {e}")

        time.sleep(2)
