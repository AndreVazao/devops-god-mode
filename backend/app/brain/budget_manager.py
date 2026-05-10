from __future__ import annotations
import time
import os
from typing import Any, Dict

from app.utils.atomic_json_store import AtomicJsonStore

STATE_FILE = os.path.join("backend", "data", "budget_state.json")
MAX_CYCLES_PER_HOUR = 60

DEFAULT_STATE = {
    "cycle_count": 0,
    "last_reset": time.time()
}

store = AtomicJsonStore(STATE_FILE, default_factory=lambda: DEFAULT_STATE)

def check_budget() -> bool:
    """
    Checks if the current hour's cycle budget has been reached.
    Resets the budget every hour.
    """
    state = store.load()
    now = time.time()

    if now - state["last_reset"] > 3600:
        state["cycle_count"] = 0
        state["last_reset"] = now

    if state["cycle_count"] >= MAX_CYCLES_PER_HOUR:
        return False

    state["cycle_count"] += 1
    store.save(state)
    return True

def get_budget_state() -> Dict[str, Any]:
    return store.load()
