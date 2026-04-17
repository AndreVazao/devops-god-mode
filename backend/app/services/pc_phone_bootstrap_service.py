import json
import secrets
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


class PcPhoneBootstrapService:
    def __init__(self, storage_path: str = "data/pc_phone_bootstrap_store.json") -> None:
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
                "bootstrap_profiles": [
                    {
                        "bootstrap_id": "bootstrap_pc_phone_primary",
                        "primary_runtime": "pc_local",
                        "remote_client": "android_phone",
                        "autodetect": {
                            "desktop_runtime": True,
                            "local_paths": True,
                            "backend_url": True,
                            "shell_url": True,
                            "phone_pairing": True,
                        },
                        "autoconfig": {
                            "zero_touch_defaults": True,
                            "desktop_shortcut": True,
                            "mobile_profile": "simple_intuitive",
                            "first_pairing_qr": True,
                        },
                        "local_backend_url": "http://127.0.0.1:8787",
                        "local_shell_url": "http://127.0.0.1:4173",
                        "pairing_mode": "qr_or_code",
                        "tunnel_mode": "private_free_tunnel",
                        "final_status": "planned",
                    }
                ],
                "updated_at": self._now(),
            }
        )

    def list_bootstrap_profiles(self) -> List[Dict[str, Any]]:
        with self._lock:
            store = self._read_store()
        return store.get("bootstrap_profiles", [])

    def get_bootstrap_foundation(self) -> Dict[str, Any]:
        profiles = self.list_bootstrap_profiles()
        return {
            "ok": True,
            "mode": "pc_phone_bootstrap_foundation",
            "bootstrap_profiles": profiles,
            "updated_at": self._read_store().get("updated_at"),
        }

    def generate_pairing_payload(self, bootstrap_id: str = "bootstrap_pc_phone_primary") -> Dict[str, Any]:
        profiles = self.list_bootstrap_profiles()
        profile = next((item for item in profiles if item.get("bootstrap_id") == bootstrap_id), None)
        if not profile:
            raise ValueError("bootstrap_profile_not_found")
        pairing_code = secrets.token_hex(4).upper()
        qr_payload = {
            "pairing_code": pairing_code,
            "local_backend_url": profile.get("local_backend_url"),
            "local_shell_url": profile.get("local_shell_url"),
            "pairing_mode": profile.get("pairing_mode"),
            "runtime_mode": "pc_and_phone_primary",
        }
        return {
            "ok": True,
            "mode": "pc_phone_pairing_payload",
            "bootstrap_id": bootstrap_id,
            "pairing_code": pairing_code,
            "qr_payload": qr_payload,
            "generated_at": self._now(),
        }

    def promote_runtime_mode(self, bootstrap_id: str = "bootstrap_pc_phone_primary") -> Dict[str, Any]:
        with self._lock:
            store = self._read_store()
            for item in store.get("bootstrap_profiles", []):
                if item.get("bootstrap_id") == bootstrap_id:
                    item["final_status"] = "pc_and_phone_primary_ready"
                    store["updated_at"] = self._now()
                    self._write_store(store)
                    return {"ok": True, "mode": "pc_phone_runtime_promoted", "bootstrap_profile": item}
        raise ValueError("bootstrap_profile_not_found")


pc_phone_bootstrap_service = PcPhoneBootstrapService()
