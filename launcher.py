import subprocess
import time
import requests
import os
import sys
from datetime import datetime
from pathlib import Path

# Paths configuration
PROJECT_ROOT = Path(__file__).resolve().parent
BACKEND_DIR = PROJECT_ROOT / "backend"
BACKEND_CMD = f"{sys.executable} -m uvicorn main:app --host 0.0.0.0 --port 8000"
HEALTH_URL = "http://127.0.0.1:8000/health"
LOG_FILE = PROJECT_ROOT / "launcher.log"

RESTART_DELAY = 3
MAX_RESTARTS = 999999

def log(msg):
    line = f"[{datetime.now()}] {msg}"
    print(line)
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception as e:
        print(f"Failed to write log: {e}")

def start_backend():
    log("🚀 Starting backend...")
    env = os.environ.copy()
    # Ensure backend is in PYTHONPATH
    python_path = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = f"{BACKEND_DIR}{os.pathsep}{python_path}"

    return subprocess.Popen(
        BACKEND_CMD,
        shell=True,
        cwd=str(BACKEND_DIR),
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )

def monitor_output(proc):
    # This should be run in a separate thread if we want concurrent health checks
    for line in proc.stdout:
        log(f"📡 {line.strip()}")

def health_check():
    try:
        r = requests.get(HEALTH_URL, timeout=2)
        return r.status_code == 200
    except:
        return False

def main():
    restarts = 0
    import threading

    while True:
        proc = start_backend()

        # Monitor output in a background thread
        monitor_thread = threading.Thread(target=monitor_output, args=(proc,), daemon=True)
        monitor_thread.start()

        start_time = time.time()

        while True:
            if proc.poll() is not None:
                log(f"❌ Backend crashed with code {proc.returncode}")
                break

            if not health_check():
                # If it's just started, give it some grace period
                if time.time() - start_time > 30:
                    log("⚠️ Health check failed")
                    # Optionally kill and restart if health check fails repeatedly
                    # For now, we follow the user's logic which just logs

            time.sleep(5)

        restarts += 1

        if restarts > MAX_RESTARTS:
            log("🔥 Too many restarts. Exiting.")
            sys.exit(1)

        log(f"🔁 Restarting in {RESTART_DELAY}s...")
        time.sleep(RESTART_DELAY)

if __name__ == "__main__":
    main()
