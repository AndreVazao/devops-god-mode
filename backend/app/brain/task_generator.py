from __future__ import annotations
from typing import Any, Dict, List

def generate_tasks(goal: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Generates a list of executable tasks based on a goal.
    """
    text = goal.get("text", "").lower()
    tasks = []

    if "deploy" in text:
        tasks.extend([
            {"action": "execute_code", "code": "print('Checking environment for deploy...')", "type": "check_env"},
            {"action": "execute_code", "code": "print('Building project...')", "type": "build"},
            {"action": "execute_code", "code": "print('Deploying to Vercel...')", "type": "deploy_vercel"},
        ])

    if "fix" in text:
        tasks.extend([
            {"action": "execute_code", "code": "print('Scanning for errors...')", "type": "scan_errors"},
            {"action": "dev_loop", "type": "auto_fix", "goal": f"Fix issues related to: {text}"},
        ])

    if "ux" in text or "ui" in text:
        tasks.extend([
            {"action": "execute_code", "code": "print('Analyzing UI/UX components...')", "type": "analyze_ui"},
            {"action": "execute_code", "code": "print('Improving navigation flow...')", "type": "improve_navigation"},
        ])

    if "stabilize" in text or "estabilizar" in text:
        tasks.extend([
            {"action": "execute_code", "code": "print('Running system diagnostics...')", "type": "diagnostics"},
            {"action": "think", "goal": "Identify stability bottlenecks", "type": "analyze_stability"},
            {"action": "dev_loop", "type": "stability_fixes", "goal": "Apply stability improvements"},
        ])

    # Default fallback if no keywords match
    if not tasks:
        tasks.append({
            "action": "think",
            "goal": text,
            "type": "generic_analysis"
        })

    return tasks
