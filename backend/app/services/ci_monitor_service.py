import time
import requests
from app.config import settings

GITHUB_API = "https://api.github.com"

def wait_for_ci(branch: str, since_id: int = None):
    token = settings.GITHUB_TOKEN
    repo = settings.GITHUB_REPO
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json"
    }

    # Poll for a NEW run if since_id is provided
    for _ in range(60):
        r = requests.get(
            f"{GITHUB_API}/repos/{repo}/actions/runs",
            headers=headers,
            params={"per_page": 10}
        )

        if r.status_code != 200:
            time.sleep(5)
            continue

        runs = r.json().get("workflow_runs", [])

        for run in runs:
            if run["head_branch"] == branch:
                # If we are looking for a run newer than since_id
                if since_id and run["id"] <= since_id:
                    continue

                if run["status"] == "completed":
                    return {
                        "status": "success" if run["conclusion"] == "success" else "failed",
                        "run_id": run["id"]
                    }
                else:
                    # Still in progress
                    break

        time.sleep(5)

    return {"status": "timeout", "run_id": None}

def get_ci_logs(run_id: int):
    """
    Fetches logs for a specific run.
    Instead of downloading the ZIP from logs_url, we fetch the jobs and then their logs.
    """
    if not run_id:
        return ""

    token = settings.GITHUB_TOKEN
    repo = settings.GITHUB_REPO
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json"
    }

    # 1. Get jobs for the run
    r = requests.get(
        f"{GITHUB_API}/repos/{repo}/actions/runs/{run_id}/jobs",
        headers=headers
    )

    if r.status_code != 200:
        return ""

    jobs = r.json().get("jobs", [])
    all_logs = []

    for job in jobs:
        job_id = job["id"]
        # 2. Get logs for each job (returns text)
        log_res = requests.get(
            f"{GITHUB_API}/repos/{repo}/actions/jobs/{job_id}/logs",
            headers=headers
        )
        if log_res.status_code == 200:
            all_logs.append(f"--- JOB: {job['name']} ---\n{log_res.text}")

    return "\n".join(all_logs)

def get_latest_run_id(branch: str):
    token = settings.GITHUB_TOKEN
    repo = settings.GITHUB_REPO
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json"
    }
    r = requests.get(
        f"{GITHUB_API}/repos/{repo}/actions/runs",
        headers=headers,
        params={"head_branch": branch, "per_page": 1}
    )
    if r.status_code == 200:
        runs = r.json().get("workflow_runs", [])
        if runs:
            return runs[0]["id"]
    return None
