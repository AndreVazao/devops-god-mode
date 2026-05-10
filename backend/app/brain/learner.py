from __future__ import annotations
import os
from typing import Dict, Any

from app.utils.atomic_json_store import AtomicJsonStore

STATE_FILE = os.path.join("backend", "data", "learning.json")

DEFAULT_STATE: Dict[str, Any] = {}

store = AtomicJsonStore(STATE_FILE, default_factory=lambda: DEFAULT_STATE)

def record(action: str, success: bool) -> None:
    """
    Records the success or failure of an action to help the system learn.
    """
    data = store.load()
    if action not in data:
        data[action] = {"ok": 0, "fail": 0}

    if success:
        data[action]["ok"] += 1
    else:
        data[action]["fail"] += 1

    store.save(data)

def get_learning_data() -> Dict[str, Any]:
    return store.load()
