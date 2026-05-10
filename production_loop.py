import time
from autonomous_loop import run as auto_run
from monitor import run as monitor_run
import threading
import sys
import os

# Add the current directory to sys.path so it can find the backend package if needed,
# although we are using top-level scripts for production_loop.
sys.path.append(os.getcwd())

def start():
    print("🔥 GOD MODE PRODUCTION")

    # Start Autonomous Loop
    threading.Thread(target=auto_run, daemon=True).start()

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
