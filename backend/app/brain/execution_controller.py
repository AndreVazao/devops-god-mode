from __future__ import annotations
from typing import Any, Dict, List
from app.evolution.executor import execute_plan

def execute_tasks(tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Executes a list of tasks using the evolution executor.
    """
    results = []

    for task in tasks:
        task_type = task.get("type", "unknown")
        print(f"🚀 [ExecutionController] Executing task: {task_type}")

        # execute_plan expects a dict that execution_orchestrator can handle
        # and it includes a 'title' for logging.
        if "title" not in task:
            task["title"] = f"Brain Task: {task_type}"

        try:
            result = execute_plan(task)
            results.append({
                "task": task_type,
                "status": "success",
                "result": result
            })
        except Exception as e:
            print(f"❌ [ExecutionController] Error executing {task_type}: {e}")
            results.append({
                "task": task_type,
                "status": "error",
                "message": str(e)
            })

    return results
