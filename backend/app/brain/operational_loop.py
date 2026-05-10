from __future__ import annotations

import time
import threading
from datetime import datetime, timezone
from typing import Dict, Any

from app.brain.operational_state import load_state, save_state
from app.brain.priority_engine import prioritize
from app.brain.task_generator import generate_tasks
from app.brain.execution_controller import execute_tasks

INTERVAL = 30  # Seconds between loops

def run_loop():
    """
    Main Operational Brain Loop.
    Decides, prioritizes, and executes tasks autonomously.
    """
    print("🧠 [OperationalBrain] Operational Loop ACTIVE")

    while True:
        try:
            state = load_state()

            # 1. Prioritize Goals
            prioritized_goals = prioritize(state)

            if not prioritized_goals:
                # No active goals, rest for a while
                time.sleep(INTERVAL)
                continue

            # 2. Pick the top priority goal
            current_goal = prioritized_goals[0]
            print(f"🎯 [OperationalBrain] Current Goal: {current_goal.get('text')}")

            # 3. Generate Tasks for this goal
            tasks = generate_tasks(current_goal)

            # 4. Execute Tasks
            results = execute_tasks(tasks)

            # 5. Update State: Goal is now completed (or needs further steps)
            # Find the goal in the original state to update its status
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

            save_state(state)
            print(f"✅ [OperationalBrain] Goal '{current_goal.get('text')}' processed.")

        except Exception as e:
            print(f"⚠️ [OperationalBrain] Loop Error: {e}")

        time.sleep(INTERVAL)

def start_operational_brain():
    """
    Starts the operational brain in a background daemon thread.
    """
    thread = threading.Thread(target=run_loop, daemon=True, name="OperationalBrain")
    thread.start()
    return thread
