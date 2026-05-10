import threading
from app.brain.multi_project_state import load, ensure_default_project
from app.brain.project_worker import run_project

def start_orchestrator():
    """Starts workers for all registered projects."""
    print("🧠 [Orchestrator] Initializing multi-project system...")

    # Ensure there's at least one project
    ensure_default_project()

    projects = load()

    for name in projects:
        print(f"🧵 [Orchestrator] Launching thread for project: {name}")
        threading.Thread(target=run_project, args=(name,), daemon=True, name=f"Worker-{name}").start()

    print(f"✅ [Orchestrator] {len(projects)} workers running in parallel.")

if __name__ == "__main__":
    start_orchestrator()
    # Keep main thread alive if run as script
    import time
    while True:
        time.sleep(1)
