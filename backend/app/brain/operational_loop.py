from __future__ import annotations

import time
import threading
from datetime import datetime, timezone
from typing import Dict, Any

from app.brain.operational_state import load_state, save_state
from app.brain.multi_project_state import get_repo_path
from app.brain.priority_engine import prioritize
from app.brain.task_generator import generate_tasks
# Replacing direct execute_tasks with SafeExecutor and BudgetManager logic
from app.brain.safe_executor import run_action
from app.brain.budget_manager import check_budget
from app.brain.learner import record

INTERVAL = 30  # Seconds between loops

def run_loop(project_name: str = "default"):
    """
    Main Operational Brain Loop.
    Decides, prioritizes, and executes tasks autonomously with safety gates.
    """
    print(f"🤖 [OperationalBrain] Controlled Autonomy Mode ACTIVE for project: {project_name}")
    repo_path = get_repo_path(project_name)

    while True:
        try:
            # 0. Check Budget
            if not check_budget():
                print(f"⏸ [OperationalBrain:{project_name}] Budget limit reached. Resting...")
                time.sleep(60)
                continue

            state = load_state(project_name)

            # 1. Prioritize Goals
            prioritized_goals = prioritize(state)

            if not prioritized_goals:
                # No active goals, rest for a while
                time.sleep(INTERVAL)
                continue

            # 2. Pick the top priority goal
            current_goal = prioritized_goals[0]
            print(f"🎯 [OperationalBrain:{project_name}] Goal: {current_goal.get('text')}")

            # 3. Generate Tasks for this goal
            tasks = generate_tasks(current_goal)

            # 4. Execute Tasks Safely
            results = []
            for task in tasks:
                action = task.get("type") or task.get("action")
                payload = task

                try:
                    result = run_action(action, payload, repo_path=repo_path)
                    results.append({
                        "task": action,
                        "status": result.get("status", "success"),
                        "result": result
                    })
                    record(action, result.get("status") != "error")
                except Exception as e:
                    print(f"❌ [OperationalBrain] Error executing {action}: {e}")
                    results.append({
                        "task": action,
                        "status": "error",
                        "message": str(e)
                    })
                    record(action, False)

            # 5. Update State: Goal is now completed (or needs further steps)
            now_iso = datetime.now(timezone.utc).isoformat()
            for goal in state.get("goals", []):
                if goal.get("id") == current_goal.get("id"):
                    goal["status"] = "completed"
                    goal["completed_at"] = now_iso

            state.setdefault("completed_tasks", []).append({
                "goal": current_goal,
                "tasks": tasks,
                "results": results,
                "timestamp": now_iso
            })

            save_state(state, project_name)
            print(f"✅ [OperationalBrain:{project_name}] Goal '{current_goal.get('text')}' processed.")

        except Exception as e:
            print(f"⚠️ [OperationalBrain:{project_name}] Loop Error: {e}")

        time.sleep(INTERVAL)

def start_operational_brain():
    """
    Starts the operational brain in a background daemon thread.
    """
    thread = threading.Thread(target=run_loop, daemon=True, name="OperationalBrain")
    thread.start()
    return thread
