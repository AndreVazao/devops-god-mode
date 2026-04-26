from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict
from uuid import uuid4

from app.services.apk_manifest_router_service import apk_manifest_router_service
from app.utils.atomic_json_store import AtomicJsonStore

CONFIG_PATH = Path("frontend/mobile-shell/apk-launch-config.json")
DATA_DIR = Path("data")
MOBILE_START_FILE = DATA_DIR / "mobile_start_config.json"
MOBILE_START_STORE = AtomicJsonStore(
    MOBILE_START_FILE,
    default_factory=lambda: {"reads": [], "validations": []},
)

REQUIRED_ROUTES = {
    "default_entry_route": "/app/apk-start",
    "preferred_chat_route": "/app/operator-chat-sync-cards",
    "legacy_chat_route": "/app/operator-chat-sync",
    "safe_home_route": "/app/home",
}


class MobileStartConfigService:
    """Versioned mobile/APK start configuration used by the WebView shell."""

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def _normalize_store(self, store: Dict[str, Any]) -> Dict[str, Any]:
        if not isinstance(store, dict):
            return {"reads": [], "validations": []}
        store.setdefault("reads", [])
        store.setdefault("validations", [])
        return store

    def _load_store(self) -> Dict[str, Any]:
        return self._normalize_store(MOBILE_START_STORE.load())

    def get_status(self) -> Dict[str, Any]:
        store = self._load_store()
        return {
            "ok": True,
            "mode": "mobile_start_config_status",
            "status": "mobile_start_config_ready",
            "config_path": str(CONFIG_PATH),
            "store_file": str(MOBILE_START_FILE),
            "atomic_store_enabled": True,
            "read_count": len(store.get("reads", [])),
            "validation_count": len(store.get("validations", [])),
        }

    def read_config(self) -> Dict[str, Any]:
        if not CONFIG_PATH.exists():
            return {"ok": False, "error": "config_not_found", "config_path": str(CONFIG_PATH)}
        config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        event = {"read_id": f"mobile-config-read-{uuid4().hex[:12]}", "created_at": self._now(), "config_version": config.get("config_version"), "profile": config.get("profile")}

        def mutate(store: Dict[str, Any]) -> Dict[str, Any]:
            store = self._normalize_store(store)
            store["reads"].append(event)
            store["reads"] = store["reads"][-300:]
            return store

        MOBILE_START_STORE.update(mutate)
        return {"ok": True, "mode": "mobile_start_config_read", "config": config, "event": event}

    def validate_config(self) -> Dict[str, Any]:
        read = self.read_config()
        if not read.get("ok"):
            return read
        config = read["config"]
        blockers = []
        for key, expected in REQUIRED_ROUTES.items():
            if config.get(key) != expected:
                blockers.append(f"{key} should be {expected}")
        if config.get("rules", {}).get("use_manifest_router_first") is not True:
            blockers.append("use_manifest_router_first must be true")
        if config.get("rules", {}).get("prefer_inline_cards_chat") is not True:
            blockers.append("prefer_inline_cards_chat must be true")
        if not config.get("webview", {}).get("javascript_enabled"):
            blockers.append("webview.javascript_enabled must be true")
        if not config.get("webview", {}).get("dom_storage_enabled"):
            blockers.append("webview.dom_storage_enabled must be true")
        validation = {
            "validation_id": f"mobile-config-validation-{uuid4().hex[:12]}",
            "created_at": self._now(),
            "status": "green" if not blockers else "red",
            "blockers": blockers,
            "entry_route": config.get("default_entry_route"),
            "preferred_chat_route": config.get("preferred_chat_route"),
            "legacy_chat_route": config.get("legacy_chat_route"),
        }

        def mutate(store: Dict[str, Any]) -> Dict[str, Any]:
            store = self._normalize_store(store)
            store["validations"].append(validation)
            store["validations"] = store["validations"][-300:]
            return store

        MOBILE_START_STORE.update(mutate)
        return {"ok": True, "mode": "mobile_start_config_validation", "validation": validation, "config": config}

    def build_launch_plan(self, tenant_id: str = "owner-andre", device_id: str = "android-apk") -> Dict[str, Any]:
        validation = self.validate_config()
        if not validation.get("ok"):
            return validation
        config = validation["config"]
        resolution = apk_manifest_router_service.resolve(tenant_id=tenant_id, device_id=device_id, prefer="auto")
        route = resolution.get("resolution", {}).get("route") or config.get("default_entry_route")
        plan = {
            "plan_id": f"mobile-start-plan-{uuid4().hex[:12]}",
            "created_at": self._now(),
            "tenant_id": tenant_id,
            "device_id": device_id,
            "open_first": config.get("default_entry_route"),
            "resolved_route": route,
            "fallback_route": resolution.get("resolution", {}).get("fallback_route") or config.get("legacy_chat_route"),
            "safe_home_route": config.get("safe_home_route"),
            "webview": config.get("webview", {}),
            "offline_cache_keys": config.get("offline_cache_keys", []),
            "safe_buttons": config.get("safe_buttons", []),
            "validation_status": validation["validation"]["status"],
        }
        return {"ok": True, "mode": "mobile_start_launch_plan", "plan": plan, "config": config, "resolution": resolution}

    def build_dashboard(self, tenant_id: str = "owner-andre", device_id: str = "android-apk") -> Dict[str, Any]:
        store = self._load_store()
        plan = self.build_launch_plan(tenant_id=tenant_id, device_id=device_id)
        return {
            "ok": True,
            "mode": "mobile_start_config_dashboard",
            "status": self.get_status(),
            "plan": plan.get("plan"),
            "config": plan.get("config"),
            "resolution": plan.get("resolution"),
            "recent_reads": store.get("reads", [])[-20:],
            "recent_validations": store.get("validations", [])[-20:],
        }

    def get_package(self) -> Dict[str, Any]:
        return {"ok": True, "mode": "mobile_start_config_package", "package": {"status": self.get_status(), "dashboard": self.build_dashboard()}}


mobile_start_config_service = MobileStartConfigService()
