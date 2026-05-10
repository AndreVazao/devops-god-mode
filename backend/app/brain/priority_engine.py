from __future__ import annotations
from typing import Any, Dict, List

def prioritize(state: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Prioritizes active goals based on keywords and scores.
    """
    goals = state.get("goals", [])
    active_goals = [g for g in goals if g.get("status") == "active"]

    if not active_goals:
        return []

    scored = []
    for goal in active_goals:
        text = goal.get("text", "").lower()
        score = 0

        # Prioritization heuristics
        if "fix" in text:
            score += 10
        if "deploy" in text:
            score += 5
        if "ux" in text or "ui" in text:
            score += 3
        if "stabilize" in text or "estabilizar" in text:
            score += 7

        scored.append((score, goal))

    # Sort by score descending
    scored.sort(reverse=True, key=lambda x: x[0])

    return [g for _, g in scored]
