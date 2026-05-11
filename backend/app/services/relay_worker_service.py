import requests
import time
import os
import threading
from app.config import settings
from .execution_orchestrator import run_task

def process_task(task):
    print(f"[RelayWorker] Processing task: {task.get('id')} - {task.get('action')}")
    try:
        return run_task(task)
    except Exception as e:
        return {"error": str(e)}

def worker_loop():
    relay_url = settings.RELAY_URL
    token = settings.RELAY_TOKEN

    if not relay_url or not token:
        print("[RelayWorker] RELAY_URL or RELAY_TOKEN not configured. Worker disabled.")
        return

    print(f"[RelayWorker] Starting worker loop connecting to {relay_url}")

    while True:
        try:
            r = requests.post(
                f"{relay_url}/pull",
                headers={"Authorization": f"Bearer {token}"},
                timeout=10
            )

            if r.status_code == 200:
                tasks = r.json()
                for t in tasks:
                    result = process_task(t)

                    requests.post(
                        f"{relay_url}/respond",
                        json={"task": t, "result": result, "status": "done", "timestamp": time.time()},
                        headers={"Authorization": f"Bearer {token}"},
                        timeout=10
                    )
            else:
                if r.status_code != 404:
                    print(f"[RelayWorker] Unexpected status code: {r.status_code}")

        except Exception as e:
            print(f"[RelayWorker] Error: {e}")

        time.sleep(5)

def start_worker():
    t = threading.Thread(target=worker_loop, daemon=True)
    t.start()
    return t
