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
    # Fallback if config is not where expected
    class Settings:
        APP_HOST = "127.0.0.1"
        APP_PORT = 8000
        APP_BASE_URL = f"http://{APP_HOST}:{APP_PORT}"
        APP_HEALTH_URL = f"{APP_BASE_URL}/health"
        SEMANTIC_INDEX_PATH = "data/semantic_index"
        REPOS_PATH = "repos"
    settings = Settings()

HOME_URL = f"{settings.APP_BASE_URL}/app/home"


def _build_env() -> dict[str, str]:
    env = os.environ.copy()
    python_path_parts = [str(BACKEND_DIR)]

    existing_python_path = env.get("PYTHONPATH")
    if existing_python_path:
        python_path_parts.append(existing_python_path)

    env["PYTHONPATH"] = os.pathsep.join(python_path_parts)
    return env


def _ensure_runtime_dirs() -> None:
    Path(settings.SEMANTIC_INDEX_PATH).mkdir(parents=True, exist_ok=True)
    Path(settings.REPOS_PATH).mkdir(parents=True, exist_ok=True)


def _wait_for_backend(timeout_seconds: int = 45) -> None:
    deadline = time.time() + timeout_seconds
    last_error = "backend did not answer"

    while time.time() < deadline:
        try:
            response = requests.get(settings.APP_HEALTH_URL, timeout=2)
            if response.ok:
                return
            last_error = f"unexpected status {response.status_code}"
        except requests.RequestException as exc:
            last_error = str(exc)

        time.sleep(1)

    raise RuntimeError(f"God Mode backend failed to start: {last_error}")


def main() -> int:
    parser = argparse.ArgumentParser(description="God Mode Desktop Launcher")
    parser.add_argument("--headless", action="store_true", help="Run without opening browser")
    args = parser.parse_args()

    print("Starting God Mode...")
    _ensure_runtime_dirs()

    log_file = open("backend_output.log", "w")

    backend = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "uvicorn",
            "main:app",
            "--app-dir",
            str(BACKEND_DIR),
            "--host",
            settings.APP_HOST,
            "--port",
            str(settings.APP_PORT),
        ],
        cwd=str(PROJECT_ROOT),
        env=_build_env(),
        stdout=log_file,
        stderr=subprocess.STDOUT,
    )

    print(f"Backend process started (PID: {backend.pid}). Logs in backend_output.log")

    try:
        if not args.headless:
            try:
                _wait_for_backend()
                webbrowser.open(HOME_URL)
                print(f"UI opened at {HOME_URL}")
            except Exception as e:
                print(f"Warning: Failed to open UI: {e}")
                print("Backend will continue running in headless mode.")

        return backend.wait()
    except KeyboardInterrupt:
        print("\nShutting down God Mode...")
        backend.terminate()
        return backend.wait()
    except Exception as e:
        print(f"Error: {e}")
        backend.terminate()
        backend.wait(timeout=10)
        raise
    finally:
        log_file.close()


if __name__ == "__main__":
    raise SystemExit(main())
