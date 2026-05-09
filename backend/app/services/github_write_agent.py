import subprocess
import requests
from typing import List
from app.config import settings

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
    run(["git", "add", "-A"])
    return run(["git", "commit", "-m", message])

def push_branch(name: str):
    return run(["git", "push", "origin", name])

def create_pull_request(branch: str):
    token = settings.GITHUB_TOKEN
    repo = settings.GITHUB_REPO
    url = f"https://api.github.com/repos/{repo}/pulls"

    data = {
        "title": f"Auto PR {branch}",
        "head": branch,
        "base": "main",
        "body": "Autonomous Dev Loop PR"
    }

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json"
    }

    r = requests.post(url, json=data, headers=headers)
    return r.json()
