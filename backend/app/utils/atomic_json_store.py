from __future__ import annotations

import json
import os
import shutil
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterator


class AtomicJsonStore:
    """Small local-first JSON persistence helper.

    It protects God Mode's local data files from partial writes by writing to a
    temporary file first, fsyncing it, keeping a best-effort backup of the last
    valid file and then atomically replacing the target file.
    """

    def __init__(self, file_path: str | Path, default_factory: Any | None = None) -> None:
        self.file_path = Path(file_path)
        self.default_factory = default_factory or dict
        self.backup_path = self.file_path.with_suffix(self.file_path.suffix + ".bak")
        self.lock_path = self.file_path.with_suffix(self.file_path.suffix + ".lock")

    def _default(self) -> Any:
        return self.default_factory() if callable(self.default_factory) else self.default_factory

    @contextmanager
    def lock(self) -> Iterator[None]:
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        lock_handle = self.lock_path.open("a+", encoding="utf-8")
        try:
            if os.name == "nt":
                import msvcrt

                msvcrt.locking(lock_handle.fileno(), msvcrt.LK_LOCK, 1)
            else:
                import fcntl

                fcntl.flock(lock_handle.fileno(), fcntl.LOCK_EX)
            yield
        finally:
            try:
                if os.name == "nt":
                    import msvcrt

                    lock_handle.seek(0)
                    msvcrt.locking(lock_handle.fileno(), msvcrt.LK_UNLCK, 1)
                else:
                    import fcntl

                    fcntl.flock(lock_handle.fileno(), fcntl.LOCK_UN)
            finally:
                lock_handle.close()

    def load(self) -> Any:
        with self.lock():
            return self._load_unlocked()

    def _load_unlocked(self) -> Any:
        if not self.file_path.exists():
            return self._default()
        try:
            return json.loads(self.file_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            if self.backup_path.exists():
                return json.loads(self.backup_path.read_text(encoding="utf-8"))
            return self._default()

    def save(self, payload: Any) -> Dict[str, Any]:
        with self.lock():
            return self._save_unlocked(payload)

    def _save_unlocked(self, payload: Any) -> Dict[str, Any]:
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        tmp_path = self.file_path.with_suffix(self.file_path.suffix + ".tmp")
        if self.file_path.exists():
            shutil.copy2(self.file_path, self.backup_path)
        with tmp_path.open("w", encoding="utf-8") as handle:
            json.dump(payload, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp_path, self.file_path)
        return {
            "ok": True,
            "file_path": str(self.file_path),
            "backup_path": str(self.backup_path),
            "written_at": datetime.now(timezone.utc).isoformat(),
        }

    def update(self, mutator: Any) -> Dict[str, Any]:
        with self.lock():
            payload = self._load_unlocked()
            updated = mutator(payload)
            if updated is not None:
                payload = updated
            result = self._save_unlocked(payload)
            result["payload"] = payload
            return result
