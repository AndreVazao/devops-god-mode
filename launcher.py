import subprocess
import time
import requests
import os
import sys
from datetime import datetime
from pathlib import Path

# Force UTF-8 encoding for stdout/stderr if supported (Python 3.7+)
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

# Paths configuration
PROJECT_ROOT = Path(__file__).resolve().parent
BACKEND_DIR = PROJECT_ROOT / "backend"
# We now use run_desktop.py as the primary entry point which handles supervisor
LAUNCHER_CMD = f"{sys.executable} run_desktop.py --headless"
HEALTH_URL = "http://127.0.0.1:8000/health"
LOG_FILE = PROJECT_ROOT / "watchdog.log"

def log(msg):
    line = f"[{datetime.now()}] {msg}"
    try:
        print(line)
    except UnicodeEncodeError:
        # Fallback for environments where UTF-8 reconfigure didn't work/apply
        print(line.encode('ascii', 'backslashreplace').decode('ascii'))

    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception as e:
        pass

def main():
    log("--- GOD MODE WATCHDOG STARTING ---")

    while True:
        log("🔄 Launching main loop...")
        proc = subprocess.Popen(
            LAUNCHER_CMD,
            shell=True,
            cwd=str(PROJECT_ROOT),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )

        # Thread to log output
        import threading
        def stream_output():
            for line in iter(proc.stdout.readline, ""):
                if line:
                    log(f"| {line.strip()}")

        threading.Thread(target=stream_output, daemon=True).start()

        # Wait for process to exit
        exit_code = proc.wait()
        log(f"❌ Main loop exited with code {exit_code}. Restarting in 5s...")
        time.sleep(5)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        log("Watchdog stopped.")
