import time
from app.brain.orchestrator import start_orchestrator
from monitor import run as monitor_run
import threading
import sys
import os

# Add the current directory to sys.path so it can find the backend package if needed,
# although we are using top-level scripts for production_loop.
sys.path.append(os.getcwd())

def start():
    print("🔥 GOD MODE PRODUCTION")

    if not os.path.exists(".env"):
        print("⚙️ Initial configuration needed...")
        import setup_env
        setup_env.main()

    # Start Multi-Project Orchestrator
    start_orchestrator()

    # Start Monitor
    threading.Thread(target=monitor_run, daemon=True).start()

    print("🚀 All systems active. Press Ctrl+C to stop.")

    while True:
        try:
            time.sleep(60)
        except KeyboardInterrupt:
            print("\n🛑 Shutting down production...")
            break

if __name__ == "__main__":
    start()
