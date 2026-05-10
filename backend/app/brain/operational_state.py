from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Any, Dict, List

from app.utils.atomic_json_store import AtomicJsonStore

# Persistent state file
STATE_FILE = os.path.join("backend", "data", "operational_state.json")

def get_default_state():
    return {
        "goals": [],
        "active_tasks": [],
        "completed_tasks": [],
        "last_update": None
    }

# Global stores registry
_stores: Dict[str, AtomicJsonStore] = {}

def get_store(project_name: str = None) -> AtomicJsonStore:
    """Gets the AtomicJsonStore for a specific project."""
    name = project_name or "default"
    if name not in _stores:
        if name == "default":
            _stores[name] = AtomicJsonStore(STATE_FILE, default_factory=get_default_state)
        else:
            project_file = os.path.join("backend", "data", f"operational_state_{name}.json")
            _stores[name] = AtomicJsonStore(project_file, default_factory=get_default_state)
    return _stores[name]

# Global store for backwards compatibility or single-project use
store = get_store("default")

def load_state(project_name: str = None) -> Dict[str, Any]:
    """Loads the current operational state for a specific project."""
    return get_store(project_name).load()

def save_state(state: Dict[str, Any], project_name: str = None) -> None:
    """Saves the operational state with a timestamp for a specific project."""
    state["last_update"] = datetime.now(timezone.utc).isoformat()
    get_store(project_name).save(state)

def add_goal(goal_text: str, project_name: str = None) -> Dict[str, Any]:
    """Adds a new goal to the state of a specific project."""
    state = load_state(project_name)

    new_goal = {
        "id": str(len(state.get("goals", [])) + 1),
        "text": goal_text,
        "status": "active",
        "created_at": datetime.now(timezone.utc).isoformat()
    }

    if "goals" not in state:
        state["goals"] = []

    state["goals"].append(new_goal)
    save_state(state, project_name)
    return state
