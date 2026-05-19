import os
import subprocess
import sys
import time
import webbrowser
import argparse
from pathlib import Path
import requests

# Add backend to sys.path to allow importing settings
PROJECT_ROOT = Path(__file__).resolve().parent
BACKEND_DIR = PROJECT_ROOT / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

try:
    from app.config import settings
except ImportError:
    class Settings:
        APP_HOST = os.getenv("APP_HOST", "127.0.0.1")
        APP_PORT = int(os.getenv("APP_PORT", "8000"))
        APP_BASE_URL = f"http://{APP_HOST}:{APP_PORT}"
        APP_HEALTH_URL = f"{APP_BASE_URL}/health"
        SEMANTIC_INDEX_PATH = str(Path.home() / ".godmode/semantic_index")
        REPOS_PATH = str(Path.home() / ".godmode/repos")
    settings = Settings()

HOME_URL = f"{settings.APP_BASE_URL}/index.html" # Standard entry point

def _ensure_runtime_dirs() -> None:
    Path(settings.SEMANTIC_INDEX_PATH).mkdir(parents=True, exist_ok=True)
    Path(settings.REPOS_PATH).mkdir(parents=True, exist_ok=True)

def _wait_for_backend(timeout_seconds: int = 60) -> None:
    deadline = time.time() + timeout_seconds
    last_error = "backend did not answer"

    print(f"Waiting for backend at {settings.APP_HEALTH_URL}...")
    while time.time() < deadline:
        try:
            response = requests.get(settings.APP_HEALTH_URL, timeout=2)
            if response.ok:
                print("✅ Backend is online!")
                return
            last_error = f"unexpected status {response.status_code}"
        except requests.RequestException as exc:
            last_error = str(exc)

        time.sleep(2)

    raise RuntimeError(f"God Mode backend failed to start: {last_error}")

def main() -> int:
    # Force UTF-8 encoding for stdout/stderr if supported
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    if hasattr(sys.stderr, 'reconfigure'):
        sys.stderr.reconfigure(encoding='utf-8')

    parser = argparse.ArgumentParser(description="God Mode Desktop Launcher")
    parser.add_argument("--headless", action="store_true", help="Run without opening browser")
    args = parser.parse_args()

    print("🚀 Starting God Mode Production Loop...")
    _ensure_runtime_dirs()

    env = os.environ.copy()
    python_path = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = f"{BACKEND_DIR}{os.pathsep}{python_path}"

    # Use supervisor as the primary engine
    supervisor_script = str(BACKEND_DIR / "supervisor.py")

    supervisor = subprocess.Popen(
        [sys.executable, supervisor_script],
        cwd=str(PROJECT_ROOT),
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )

    print(f"Supervisor active (PID: {supervisor.pid}). Monitoring backend logs...")

    # Log supervisor output in a separate thread
    import threading
    def log_supervisor():
        with open("launcher_output.log", "w", encoding="utf-8") as f:
            for line in iter(supervisor.stdout.readline, ""):
                f.write(line)
                f.flush()
                # Also print critical lines to console
                if "ERROR" in line or "CRITICAL" in line or "✅" in line:
                    print(f"[LOG] {line.strip()}")

    threading.Thread(target=log_supervisor, daemon=True).start()

    try:
        if not args.headless:
            try:
                _wait_for_backend()
                webbrowser.open(HOME_URL)
                print(f"✨ UI available at: {HOME_URL}")
            except Exception as e:
                print(f"⚠️ Warning: Failed to open UI: {e}")
                print("Backend is running (see launcher_output.log).")

        # Keep the main thread alive as long as supervisor is running
        return supervisor.wait()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down God Mode...")
        supervisor.terminate()
        try:
            supervisor.wait(timeout=5)
        except:
            supervisor.kill()
        return 0
    except Exception as e:
        print(f"❌ Error: {e}")
        supervisor.terminate()
        supervisor.wait(timeout=10)
        raise

if __name__ == "__main__":
    raise SystemExit(main())
