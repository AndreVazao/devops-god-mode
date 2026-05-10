from .local_executor_service import execute_code
from .github_write_agent import create_branch, commit_all, push_branch
from .autonomous_dev_loop_service import run_dev_loop
from app.brain.god_brain import think
from app.brain.operational_state import add_goal
from typing import Dict, Any

def run_task(task: Dict[str, Any]) -> Dict[str, Any]:
    action = task.get("action")

    if action == "execute_code":
        code = task.get("code")
        if not code:
            return {"error": "no code provided"}
        return execute_code(code)

    if action == "dev_loop":
        return run_dev_loop(task)

    if action == "think":
        goal = task.get("payload", {}).get("goal") or task.get("goal")
        if not goal:
            return {"error": "no goal provided for think action"}
        return think(goal)

    if action == "goal":
        text = task.get("payload", {}).get("text") or task.get("text")
        if not text:
            return {"error": "no text provided for goal action"}
        return {"status": "goal_added", "state": add_goal(text)}

    if action == "git_commit":
        branch = task.get("branch", "auto-branch")
        message = task.get("message", "auto commit")

        cb_res = create_branch(branch)
        if cb_res.returncode != 0 and b"already exists" not in cb_res.stderr.encode():
             # If branch exists it might fail but we can continue or handle it
             pass

        commit_res = commit_all(message)
        push_res = push_branch(branch)

        return {
            "status": "git_done",
            "branch": branch,
            "commit_stdout": commit_res.stdout,
            "commit_stderr": commit_res.stderr,
            "push_stdout": push_res.stdout,
            "push_stderr": push_res.stderr
        }

    return {"error": f"unknown action: {action}"}
