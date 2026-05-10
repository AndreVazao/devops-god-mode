from app.brain.operational_loop import run_loop

def run_project(name: str):
    """Runs the autonomous loop for a specific project."""
    print(f"🚀 [ProjectWorker] Starting worker for project: {name}")
    run_loop(project_name=name)
