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
        logging.FileHandler("supervisor.log", encoding="utf-8")
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
        # Ensure PYTHONPATH includes backend
        python_path = self.env.get("PYTHONPATH", "")
        if str(BACKEND_DIR) not in python_path:
            self.env["PYTHONPATH"] = f"{BACKEND_DIR}{os.pathsep}{python_path}"

        # Ensure UTF-8 is enabled in child process output on Windows.
        self.env.setdefault("PYTHONUTF8", "1")
        # Force Python IO encoding to UTF-8 with replacement for invalid chars
        # so child process logging can't raise UnicodeEncodeError on Windows consoles.
        self.env.setdefault("PYTHONIOENCODING", "utf-8:replace")

        self.process = subprocess.Popen(
            self.command,
            cwd=self.cwd,
            env=self.env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            bufsize=1
        )

        import threading
        def log_output():
            try:
                for line in iter(self.process.stdout.readline, ""):
                    if line:
                        clean_line = line.strip()
                        print(f"[{self.name}] {clean_line}")
                        logger.info(f"[{self.name} OUTPUT] {clean_line}")
            except Exception as e:
                logger.error(f"Error reading output from {self.name}: {e}")

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
    logger.info("--- GOD MODE SUPERVISOR INITIALIZING ---")

    # FastAPI Server command
    # We use sys.executable to ensure we use the same environment
    api_cmd = [
        sys.executable, "-m", "uvicorn", "main:app",
        "--app-dir", str(BACKEND_DIR),
        "--host", os.getenv("APP_HOST", "127.0.0.1"),
        "--port", os.getenv("APP_PORT", "8000")
    ]

    processes = [
        ProcessManager("API", api_cmd)
    ]

    for p in processes:
        p.start()

    def signal_handler(sig, frame):
        logger.info("Interrupt received, shutting down God Mode...")
        for p in processes:
            p.stop()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    logger.info("Supervisor active and monitoring.")

    # Watchdog loop
    try:
        while True:
            for p in processes:
                if not p.is_alive():
                    exit_code = p.process.poll()
                    logger.warning(f"Process {p.name} died with exit code {exit_code}. Restarting in 3s...")
                    time.sleep(3)
                    p.start()
            time.sleep(5)
    except KeyboardInterrupt:
        signal_handler(None, None)

if __name__ == "__main__":
    main()
