import subprocess
import sys
import time
import os
import signal
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] SUPERVISOR: %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("supervisor.log")
    ]
)
logger = logging.getLogger(__name__)

BACKEND_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BACKEND_DIR.parent

class ProcessManager:
    def __init__(self, name, command, cwd=None, env=None):
        self.name = name
        self.command = command
        self.cwd = cwd or str(PROJECT_ROOT)
        self.env = env or os.environ.copy()
        self.process = None

    def start(self):
        logger.info(f"Starting {self.name}...")
        self.process = subprocess.Popen(
            self.command,
            cwd=self.cwd,
            env=self.env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        # Start a thread to log output
        import threading
        def log_output():
            for line in iter(self.process.stdout.readline, ""):
                if line:
                    print(f"[{self.name}] {line.strip()}")

        threading.Thread(target=log_output, daemon=True).start()

    def is_alive(self):
        if self.process is None:
            return False
        return self.process.poll() is None

    def stop(self):
        if self.process:
            logger.info(f"Stopping {self.name}...")
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()

def main():
    logger.info("God Mode Supervisor starting...")

    env = os.environ.copy()
    python_path = env.get("PYTHONPATH", "")
    if str(BACKEND_DIR) not in python_path:
        env["PYTHONPATH"] = f"{BACKEND_DIR}{os.pathsep}{python_path}"

    # 1. FastAPI Server
    api_cmd = [
        sys.executable, "-m", "uvicorn", "main:app",
        "--app-dir", str(BACKEND_DIR),
        "--host", os.getenv("APP_HOST", "0.0.0.0"),
        "--port", os.getenv("APP_PORT", "8000")
    ]

    # 2. Relay Worker (Standalone mode if preferred or as part of app)
    # The app already starts start_worker in lifespan, but having a watchdog for the whole process is better.

    processes = [
        ProcessManager("API", api_cmd, env=env)
    ]

    for p in processes:
        p.start()

    def signal_handler(sig, frame):
        logger.info("Interrupt received, shutting down processes...")
        for p in processes:
            p.stop()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    logger.info("Supervisor entering watchdog loop.")
    while True:
        for p in processes:
            if not p.is_alive():
                exit_code = p.process.poll()
                logger.warning(f"Process {p.name} died with exit code {exit_code}. Restarting...")
                p.start()

        time.sleep(5)

if __name__ == "__main__":
    main()
