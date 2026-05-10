from __future__ import annotations
from typing import Set

CRITICAL_ACTIONS: Set[str] = {
    "deploy", "merge", "delete", "billing", "secrets_write", "deploy_vercel"
}

def requires_approval(action: str) -> bool:
    """
    Determines if an action requires manual approval.
    """
    return action in CRITICAL_ACTIONS

def allowed(action: str) -> bool:
    """
    Checks if an action is globally allowed.
    Currently always returns True, but can be used to block specific actions.
    """
    return True
