from __future__ import annotations

from pathlib import Path
from typing import Any
from app.utils.atomic_json_store import AtomicJsonStore

STORE_PATH = Path("data/pattern_library.json")

def _default_store() -> dict[str, Any]:
    return {
        "patterns": {},
        "last_updated_at": None,
    }

class PatternLibraryService:
    """Library for storing and retrieving identified code patterns."""

    def __init__(self) -> None:
        self.store = AtomicJsonStore(STORE_PATH, default_factory=_default_store)

    def _load(self) -> dict[str, Any]:
        payload = self.store.load()
        if not isinstance(payload, dict):
            return _default_store()
        payload.setdefault("patterns", {})
        return payload

    def store_patterns(self, patterns: list[dict[str, str]]) -> None:
        payload = self._load()
        stored_patterns = payload["patterns"]

        for p in patterns:
            key = p["type"]
            file_path = p["file"]

            if key not in stored_patterns:
                stored_patterns[key] = []

            if file_path not in stored_patterns[key]:
                stored_patterns[key].append(file_path)

        from datetime import datetime, timezone
        payload["last_updated_at"] = datetime.now(timezone.utc).isoformat()
        self.store.save(payload)

    def get_pattern(self, pattern_type: str) -> list[str]:
        payload = self._load()
        return payload["patterns"].get(pattern_type, [])

    def get_all_patterns(self) -> dict[str, list[str]]:
        payload = self._load()
        return payload["patterns"]

pattern_library_service = PatternLibraryService()
