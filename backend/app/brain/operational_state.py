from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Any, Dict, List

from app.utils.atomic_json_store import AtomicJsonStore

# Persistent state file
STATE_FILE = os.path.join("backend", "data", "operational_state.json")

DEFAULT_STATE = {
    "goals": [],
    "active_tasks": [],
    "completed_tasks": [],
    "last_update": None
}

store = AtomicJsonStore(STATE_FILE, default_factory=lambda: DEFAULT_STATE)

def load_state() -> Dict[str, Any]:
    """Loads the current operational state."""
    return store.load()

def save_state(state: Dict[str, Any]) -> None:
    """Saves the operational state with a timestamp."""
    state["last_update"] = datetime.now(timezone.utc).isoformat()
    store.save(state)

def add_goal(goal_text: str) -> Dict[str, Any]:
    """Adds a new goal to the state."""
    state = load_state()

    new_goal = {
        "id": str(len(state.get("goals", [])) + 1),
        "text": goal_text,
        "status": "active",
        "created_at": datetime.now(timezone.utc).isoformat()
    }

    if "goals" not in state:
        state["goals"] = []

    state["goals"].append(new_goal)
    save_state(state)
    return state
