import json
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


class PackagingFoundationService:
    def __init__(self, storage_path: str = "data/packaging_foundation_store.json") -> None:
        self.storage_path = Path(storage_path)
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        self._ensure_store()

    def _ensure_store(self) -> None:
        if not self.storage_path.exists():
            self._write_store(
                {
                    "build_profiles": [
                        {
                            "profile_id": "pkg_windows_desktop",
                            "target_platform": "windows_desktop",
                            "artifact_type": ".exe",
                            "runtime_mode": "pc_and_phone_primary",
                            "entrypoint": "backend/main.py",
                            "output_name": "GodModeDesktop.exe",
                            "packaging_status": "planned",
                            "notes": [
                                "autodetect desktop runtime",
                                "autoconfig local paths",
                                "desktop UX should stay intuitive",
                            ],
                        },
                        {
                            "profile_id": "pkg_android_cockpit",
                            "target_platform": "android_phone",
                            "artifact_type": "apk",
                            "runtime_mode": "pc_and_phone_primary",
                            "entrypoint": "frontend/mobile-shell/index.html",
                            "output_name": "GodModeMobile.apk",
                            "packaging_status": "planned",
                            "notes": [
                                "phone cockpit should stay simple",
                                "autopair with PC runtime",
                                "zero-touch remote usage",
                            ],
                        },
                    ],
                    "runtime_topologies": [
                        {
                            "topology_id": "topo_pc_phone_primary",
                            "primary_runtime": "pc_local",
                            "remote_client": "android_phone",
                            "render_role": "temporary_test_only",
                            "tunnel_mode": "private_free_tunnel",
                            "persistence_mode": "pc_local_primary",
                            "autodetect": {
                                "desktop_runtime": True,
                                "phone_pairing": True,
                                "tunnel_endpoint": True,
                                "local_paths": True,
                            },
                            "autoconfig": {
                                "desktop_shortcut": True,
                                "zero_touch_defaults": True,
                                "phone_cockpit_profile": "simple_intuitive",
                            },
                        }
                    ],
                    "updated_at": self._now(),
                }
            )

    def _read_store(self) -> Dict[str, Any]:
        return json.loads(self.storage_path.read_text(encoding="utf-8"))

    def _write_store(self, payload: Dict[str, Any]) -> None:
        self.storage_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def get_foundation(self) -> Dict[str, Any]:
        with self._lock:
            store = self._read_store()
        return {
            "ok": True,
            "mode": "desktop_apk_packaging_foundation",
            "build_profiles": store.get("build_profiles", []),
            "runtime_topologies": store.get("runtime_topologies", []),
            "updated_at": store.get("updated_at"),
        }

    def list_build_profiles(self) -> List[Dict[str, Any]]:
        with self._lock:
            store = self._read_store()
        return store.get("build_profiles", [])

    def list_runtime_topologies(self) -> List[Dict[str, Any]]:
        with self._lock:
            store = self._read_store()
        return store.get("runtime_topologies", [])


packaging_foundation_service = PackagingFoundationService()
