from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict
from uuid import uuid4

from app.services.apk_launch_manifest_service import apk_launch_manifest_service
from app.utils.atomic_json_store import AtomicJsonStore

DATA_DIR = Path("data")
APK_ROUTER_FILE = DATA_DIR / "apk_manifest_router.json"
APK_ROUTER_STORE = AtomicJsonStore(
    APK_ROUTER_FILE,
    default_factory=lambda: {"resolutions": [], "errors": []},
)

SAFE_FALLBACK_ROUTE = "/app/home"
LEGACY_CHAT_ROUTE = "/app/operator-chat-sync"
DEFAULT_CHAT_ROUTE = "/app/operator-chat-sync-cards"


class ApkManifestRouterService:
    """Resolve the best APK route from the launch manifest and keep safe fallbacks."""

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def _normalize_store(self, store: Dict[str, Any]) -> Dict[str, Any]:
        if not isinstance(store, dict):
            return {"resolutions": [], "errors": []}
        store.setdefault("resolutions", [])
        store.setdefault("errors", [])
        return store

    def _load_store(self) -> Dict[str, Any]:
        return self._normalize_store(APK_ROUTER_STORE.load())

    def get_status(self) -> Dict[str, Any]:
        store = self._load_store()
        return {
            "ok": True,
            "mode": "apk_manifest_router_status",
            "status": "apk_manifest_router_ready",
            "store_file": str(APK_ROUTER_FILE),
            "atomic_store_enabled": True,
            "default_chat_route": DEFAULT_CHAT_ROUTE,
            "legacy_chat_route": LEGACY_CHAT_ROUTE,
            "safe_fallback_route": SAFE_FALLBACK_ROUTE,
            "resolution_count": len(store.get("resolutions", [])),
            "error_count": len(store.get("errors", [])),
        }

    def _record_resolution(self, resolution: Dict[str, Any]) -> None:
        def mutate(store: Dict[str, Any]) -> Dict[str, Any]:
            store = self._normalize_store(store)
            store["resolutions"].append(resolution)
            store["resolutions"] = store["resolutions"][-500:]
            return store

        APK_ROUTER_STORE.update(mutate)

    def _record_error(self, error: Dict[str, Any]) -> None:
        def mutate(store: Dict[str, Any]) -> Dict[str, Any]:
            store = self._normalize_store(store)
            store["errors"].append(error)
            store["errors"] = store["errors"][-200:]
            return store

        APK_ROUTER_STORE.update(mutate)

    def resolve(self, tenant_id: str = "owner-andre", device_id: str = "android-apk", prefer: str = "auto") -> Dict[str, Any]:
        created_at = self._now()
        try:
            launch = apk_launch_manifest_service.build_manifest(tenant_id=tenant_id, device_id=device_id)
            manifest = launch.get("manifest", {}) if launch.get("ok") else {}
            policy = manifest.get("launch_policy", {})
            capabilities = manifest.get("capabilities", {})
            if prefer == "legacy":
                route = policy.get("fallback_route") or LEGACY_CHAT_ROUTE
                reason = "operator_requested_legacy"
            elif prefer == "home":
                route = policy.get("home_route") or SAFE_FALLBACK_ROUTE
                reason = "operator_requested_home"
            elif capabilities.get("inline_action_cards") and policy.get("default_route"):
                route = policy["default_route"]
                reason = "inline_action_cards_available"
            else:
                route = policy.get("fallback_route") or LEGACY_CHAT_ROUTE
                reason = "inline_cards_unavailable_using_legacy"
            resolution = {
                "resolution_id": f"apk-route-{uuid4().hex[:12]}",
                "created_at": created_at,
                "tenant_id": tenant_id,
                "device_id": device_id,
                "prefer": prefer,
                "route": route,
                "fallback_route": policy.get("fallback_route") or LEGACY_CHAT_ROUTE,
                "safe_fallback_route": policy.get("offline_safe_route") or SAFE_FALLBACK_ROUTE,
                "reason": reason,
                "manifest_id": manifest.get("manifest_id"),
                "ok": True,
            }
            self._record_resolution(resolution)
            return {"ok": True, "mode": "apk_manifest_route_resolution", "resolution": resolution, "manifest": manifest}
        except Exception as exc:  # pragma: no cover - defensive launcher fallback
            error = {
                "error_id": f"apk-route-error-{uuid4().hex[:12]}",
                "created_at": created_at,
                "tenant_id": tenant_id,
                "device_id": device_id,
                "prefer": prefer,
                "error": str(exc),
                "route": SAFE_FALLBACK_ROUTE,
                "fallback_route": LEGACY_CHAT_ROUTE,
                "ok": False,
            }
            self._record_error(error)
            return {"ok": False, "mode": "apk_manifest_route_resolution_error", "resolution": error}

    def dashboard(self, tenant_id: str = "owner-andre", device_id: str = "android-apk") -> Dict[str, Any]:
        store = self._load_store()
        latest = self.resolve(tenant_id=tenant_id, device_id=device_id)
        return {
            "ok": True,
            "mode": "apk_manifest_router_dashboard",
            "tenant_id": tenant_id,
            "device_id": device_id,
            "status": self.get_status(),
            "latest_resolution": latest.get("resolution"),
            "manifest": latest.get("manifest", {}),
            "recent_resolutions": store.get("resolutions", [])[-30:],
            "recent_errors": store.get("errors", [])[-20:],
        }

    def get_package(self) -> Dict[str, Any]:
        return {"ok": True, "mode": "apk_manifest_router_package", "package": {"status": self.get_status(), "dashboard": self.dashboard()}}


apk_manifest_router_service = ApkManifestRouterService()
