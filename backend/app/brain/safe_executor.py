from __future__ import annotations
import subprocess
from typing import Any, Dict, Optional

from app.brain.policy_engine import requires_approval
from app.evolution.approval import wait_for_approval
from app.brain.skill_registry import get_skill
from app.services.execution_orchestrator import run_task

def run_action(action: str, payload: Optional[Dict[str, Any]] = None, repo_path: str = None) -> Dict[str, Any]:
    """
    Executes an action safely, checking for required approvals and using the skill registry.
    """
    print(f"▶️ [SafeExecutor] Action: {action}")

    if action == "deploy_vercel":
        from app.evolution.approval import wait_for_approval
        if not wait_for_approval({
            "title": "Deploy Produção",
            "action": "deploy",
            "message": "Deploy to production?",
            "type": "critical"
        }):
             return {"status": "rejected", "action": action}

    elif requires_approval(action):
        print(f"⛔ [SafeExecutor] Waiting approval: {action}")
        # wait_for_approval expects a plan-like dict
        plan = {
            "title": f"Critical Action: {action}",
            "action": action,
            "type": "critical",
            "payload": payload
        }
        if not wait_for_approval(plan):
            return {"status": "rejected", "action": action}

    # 1. Check Skill Registry
    skill_script = get_skill(action)
    if skill_script:
        print(f"🛠️ [SafeExecutor] Executing skill script: {skill_script}")
        try:
            res = subprocess.run(["python", skill_script], capture_output=True, text=True, cwd=repo_path)
            return {
                "status": "success" if res.returncode == 0 else "error",
                "stdout": res.stdout,
                "stderr": res.stderr,
                "returncode": res.returncode
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    # 2. Fallback to Execution Orchestrator
    print(f"🔗 [SafeExecutor] Routing to ExecutionOrchestrator: {action}")
    task = {"action": action}
    if payload:
        task.update(payload)

    # Map some known types back to orchestrator actions if needed
    if action == "auto_fix" or action == "stability_fixes":
        task["action"] = "dev_loop"

    return run_task(task, repo_path=repo_path)
