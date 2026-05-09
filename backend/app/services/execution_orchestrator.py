from .local_executor_service import execute_code
from .github_write_agent import create_branch, commit_all, push_branch
from typing import Dict, Any

def run_task(task: Dict[str, Any]) -> Dict[str, Any]:
    action = task.get("action")

    if action == "execute_code":
        code = task.get("code")
        if not code:
            return {"error": "no code provided"}
        return execute_code(code)

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
