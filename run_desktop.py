import os
import subprocess
import sys
import time
import webbrowser
from pathlib import Path

import requests

from backend.app.config import settings

PROJECT_ROOT = Path(__file__).resolve().parent
BACKEND_DIR = PROJECT_ROOT / "backend"
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
    print("Starting God Mode...")
    _ensure_runtime_dirs()

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
    )

    try:
        _wait_for_backend()
        webbrowser.open(HOME_URL)
        print(f"UI opened at {HOME_URL}")
        return backend.wait()
    except Exception:
        backend.terminate()
        backend.wait(timeout=10)
        raise


if __name__ == "__main__":
    raise SystemExit(main())
