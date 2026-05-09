import time
from .github_write_agent import create_branch, commit_all, push_branch, create_pull_request
from .ci_monitor_service import wait_for_ci, get_ci_logs, get_latest_run_id
from .ai_fix_service import generate_fix, apply_fix

MAX_RETRIES = 3

def run_dev_loop(task: dict):
    phase_number = task.get("phase_number", int(time.time()))
    branch_name = f"phase-{phase_number}-auto"

    print(f"[DEV LOOP] Starting for branch {branch_name}")

    # Capture latest run ID before pushing to avoid picking up old runs
    last_run_id = get_latest_run_id(branch_name)

    # 1. Criar branch
    create_branch(branch_name)

    # 2. Commit inicial
    msg = task.get("initial_message", f"auto initial commit for phase {phase_number}")
    commit_all(msg)

    # 3. Push
    push_branch(branch_name)

    # 4. Criar PR
    pr_res = create_pull_request(branch_name)
    print(f"[DEV LOOP] PR Created: {pr_res.get('html_url', 'unknown')}")

    retries = 0

    while retries < MAX_RETRIES:
        print(f"[DEV LOOP] Waiting for CI (Attempt {retries + 1}/{MAX_RETRIES})...")
        # Pass last_run_id to wait for a NEWER run
        res = wait_for_ci(branch_name, since_id=last_run_id)
        status = res["status"]
        run_id = res["run_id"]

        if status == "success":
            print(f"[DEV LOOP] CI passed on {branch_name}")
            return {"status": "completed", "branch": branch_name, "pr": pr_res.get("html_url")}

        if status == "timeout":
            print("[DEV LOOP] CI timed out.")
            return {"status": "failed_timeout", "branch": branch_name}

        print("[DEV LOOP] CI failed, analyzing logs...")
        logs = get_ci_logs(run_id)

        fix = generate_fix(logs)
        if not fix or fix.get("type") == "noop":
            print("[DEV LOOP] No fix generated or noop.")
            return {"status": "failed_no_fix", "branch": branch_name}

        print(f"[DEV LOOP] Applying fix: {fix}")
        # Note: apply_fix already has safety guards
        apply_fix(fix)

        # Update last_run_id for next iteration
        last_run_id = run_id

        commit_all(f"auto fix attempt {retries + 1}")
        push_branch(branch_name)

        retries += 1

    print("[DEV LOOP] Reached MAX_RETRIES.")
    return {"status": "failed_max_retries", "branch": branch_name}
