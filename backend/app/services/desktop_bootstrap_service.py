import json
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


class DesktopBootstrapService:
    def __init__(self, storage_path: str = "data/desktop_bootstrap_store.json") -> None:
        self.storage_path = Path(storage_path)
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        self._ensure_store()

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def _write_store(self, payload: Dict[str, Any]) -> None:
        self.storage_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    def _read_store(self) -> Dict[str, Any]:
        return json.loads(self.storage_path.read_text(encoding="utf-8"))

    def _ensure_store(self) -> None:
        if self.storage_path.exists():
            return
        self._write_store(
            {
                "desktop_bootstrap_profiles": [
                    {
                        "bootstrap_id": "desktop_bootstrap_pc_primary",
                        "runtime_mode": "pc_and_phone_primary",
                        "desktop_shortcut": True,
                        "autostart": False,
                        "first_run_actions": [
                            "create_local_config",
                            "prepare_shortcut_payload",
                            "open_local_cockpit",
                        ],
                        "local_backend_url": "http://127.0.0.1:8787",
                        "local_shell_url": "http://127.0.0.1:4173",
                        "bootstrap_status": "planned",
                    }
                ],
                "updated_at": self._now(),
            }
        )

    def list_profiles(self) -> List[Dict[str, Any]]:
        with self._lock:
            store = self._read_store()
        return store.get("desktop_bootstrap_profiles", [])

    def get_foundation(self) -> Dict[str, Any]:
        with self._lock:
            store = self._read_store()
        return {
            "ok": True,
            "mode": "desktop_bootstrap_foundation",
            "desktop_bootstrap_profiles": store.get("desktop_bootstrap_profiles", []),
            "updated_at": store.get("updated_at"),
        }

    def generate_first_run_payload(self, bootstrap_id: str = "desktop_bootstrap_pc_primary") -> Dict[str, Any]:
        profiles = self.list_profiles()
        profile = next((item for item in profiles if item.get("bootstrap_id") == bootstrap_id), None)
        if not profile:
            raise ValueError("desktop_bootstrap_profile_not_found")
        payload = {
            "bootstrap_id": bootstrap_id,
            "runtime_mode": profile.get("runtime_mode"),
            "desktop_shortcut": profile.get("desktop_shortcut"),
            "autostart": profile.get("autostart"),
            "local_backend_url": profile.get("local_backend_url"),
            "local_shell_url": profile.get("local_shell_url"),
            "first_run_actions": profile.get("first_run_actions", []),
            "generated_at": self._now(),
        }
        return {"ok": True, "mode": "desktop_first_run_payload", "payload": payload}

    def set_autostart(self, enabled: bool, bootstrap_id: str = "desktop_bootstrap_pc_primary") -> Dict[str, Any]:
        with self._lock:
            store = self._read_store()
            for item in store.get("desktop_bootstrap_profiles", []):
                if item.get("bootstrap_id") == bootstrap_id:
                    item["autostart"] = enabled
                    item["bootstrap_status"] = "autostart_enabled" if enabled else "autostart_disabled"
                    store["updated_at"] = self._now()
                    self._write_store(store)
                    return {"ok": True, "mode": "desktop_autostart_updated", "desktop_bootstrap_profile": item}
        raise ValueError("desktop_bootstrap_profile_not_found")


Desktop_bootstrap_service = DesktopBootstrapService()
