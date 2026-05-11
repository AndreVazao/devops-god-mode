import requests
import subprocess
import time
import os
import sys
from app.config import settings

BASE = f"{settings.RELAY_URL}/cluster"
HEADERS = {"Authorization": f"Bearer {settings.RELAY_TOKEN}"}
TARGET_WORKERS = 1
MAX_WORKERS = 4

procs = []

def spawn():
    print("🚀 [Autoscale] Spawning new worker...")
    env = os.environ.copy()
    env["PYTHONPATH"] = "."
    # Use sys.executable to ensure we use the same python
    p = subprocess.Popen([sys.executable, "app/brain/worker_cluster.py"], env=env, cwd="backend")
    procs.append(p)

def kill_one():
    if procs:
        print("🛑 [Autoscale] Terminating one worker...")
        p = procs.pop()
        p.terminate()

if __name__ == "__main__":
    print("🧠 [Autoscale] Launcher started.")

    # Bootstrap
    for _ in range(TARGET_WORKERS):
        spawn()

    while True:
        try:
            r = requests.get(f"{BASE}/metrics", headers=HEADERS, timeout=5)
            if r.status_code == 200:
                m = r.json()
                avg = m.get("avg_latency", 0)

                print(f"📊 [Autoscale] Workers: {len(procs)}, Avg Latency: {avg}ms")

                # Scale by latency
                if avg > 2000 and len(procs) < MAX_WORKERS:
                    spawn()
                elif avg < 500 and len(procs) > TARGET_WORKERS:
                    kill_one()
            else:
                print(f"⚠️ [Autoscale] Failed to fetch metrics: {r.status_code}")

        except Exception as e:
            print(f"⚠️ [Autoscale] Error: {e}")

        time.sleep(10)
