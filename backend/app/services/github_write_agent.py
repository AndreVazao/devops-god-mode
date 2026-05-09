import subprocess
from typing import List

REPO_PATH = "."

def run(cmd: List[str]):
    """Runs a command as a list of arguments to prevent shell injection."""
    return subprocess.run(cmd, capture_output=True, text=True)

def create_branch(name: str):
    # Check if branch exists
    res = run(["git", "show-ref", "--verify", f"refs/heads/{name}"])
    if res.returncode == 0:
        # Branch exists, just checkout
        return run(["git", "checkout", name])
    else:
        # Create and checkout
        return run(["git", "checkout", "-b", name])

def commit_all(message: str):
    run(["git", "add", "."])
    return run(["git", "commit", "-m", message])

def push_branch(name: str):
    return run(["git", "push", "origin", name])
