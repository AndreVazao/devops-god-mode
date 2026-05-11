import sys
import threading
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
BACKEND_DIR = PROJECT_ROOT / "backend"

for runtime_path in (PROJECT_ROOT, BACKEND_DIR):
    resolved = str(runtime_path)
    if resolved not in sys.path:
        sys.path.insert(0, resolved)

from app.brain.orchestrator import start_orchestrator
from app.config import settings
from monitor import run as monitor_run


def ensure_runtime_dirs() -> None:
    Path(settings.SEMANTIC_INDEX_PATH).mkdir(parents=True, exist_ok=True)
    Path(settings.REPOS_PATH).mkdir(parents=True, exist_ok=True)


def start() -> None:
    print("GOD MODE PRODUCTION")
    ensure_runtime_dirs()

    start_orchestrator()
    threading.Thread(target=monitor_run, daemon=True).start()

    print("All systems active. Press Ctrl+C to stop.")

    while True:
        try:
            time.sleep(60)
        except KeyboardInterrupt:
            print("\nStopping production...")
            break


if __name__ == "__main__":
    start()
