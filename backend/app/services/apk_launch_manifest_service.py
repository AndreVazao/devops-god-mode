from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict
from uuid import uuid4

from app.services.chat_action_cards_service import chat_action_cards_service
from app.services.chat_inline_card_renderer_service import chat_inline_card_renderer_service
from app.services.god_mode_home_service import god_mode_home_service
from app.services.mobile_approval_cockpit_v2_service import mobile_approval_cockpit_v2_service
from app.services.operator_chat_runtime_snapshot_service import operator_chat_runtime_snapshot_service
from app.utils.atomic_json_store import AtomicJsonStore

DATA_DIR = Path("data")
APK_LAUNCH_FILE = DATA_DIR / "apk_launch_manifest.json"
APK_LAUNCH_STORE = AtomicJsonStore(
    APK_LAUNCH_FILE,
    default_factory=lambda: {"launches": [], "health_checks": []},
)


class ApkLaunchManifestService:
    """Single boot manifest for the Android APK/mobile shell."""

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def _normalize_store(self, store: Dict[str, Any]) -> Dict[str, Any]:
        if not isinstance(store, dict):
            return {"launches": [], "health_checks": []}
        store.setdefault("launches", [])
        store.setdefault("health_checks", [])
        return store

    def _load_store(self) -> Dict[str, Any]:
        return self._normalize_store(APK_LAUNCH_STORE.load())

    def _safe(self, label: str, fn: Any) -> Dict[str, Any]:
        try:
            return {"ok": True, "label": label, "result": fn()}
        except Exception as exc:  # pragma: no cover - defensive manifest shell
            return {"ok": False, "label": label, "error": str(exc)}

    def get_status(self) -> Dict[str, Any]:
        store = self._load_store()
        return {
            "ok": True,
            "mode": "apk_launch_manifest_status",
            "status": "apk_launch_manifest_ready",
            "store_file": str(APK_LAUNCH_FILE),
            "atomic_store_enabled": True,
            "preferred_chat_surface": "/app/operator-chat-sync-cards",
            "fallback_chat_surface": "/app/operator-chat-sync",
            "launch_count": len(store.get("launches", [])),
            "health_check_count": len(store.get("health_checks", [])),
        }

    def build_manifest(self, tenant_id: str = "owner-andre", device_id: str = "android-apk") -> Dict[str, Any]:
        home = self._safe("god_mode_home", lambda: god_mode_home_service.build_dashboard(tenant_id=tenant_id))
        renderer = self._safe("chat_inline_card_renderer", lambda: chat_inline_card_renderer_service.build_manifest(tenant_id=tenant_id))
        cards = self._safe("chat_action_cards", lambda: chat_action_cards_service.build_dashboard(tenant_id=tenant_id))
        approvals = self._safe("mobile_approval", lambda: mobile_approval_cockpit_v2_service.build_dashboard(tenant_id=tenant_id))
        chat_snapshot = self._safe("chat_snapshot", lambda: operator_chat_runtime_snapshot_service.build_snapshot(tenant_id=tenant_id))
        manifest = {
            "manifest_id": f"apk-launch-{uuid4().hex[:12]}",
            "created_at": self._now(),
            "tenant_id": tenant_id,
            "device_id": device_id,
            "version": 1,
            "launch_policy": {
                "default_route": "/app/operator-chat-sync-cards",
                "default_api": "/api/chat-inline-card-renderer/send",
                "fallback_route": "/app/operator-chat-sync",
                "home_route": "/app/god-mode-home",
                "money_route": "/app/money-command-center",
                "approval_route": "/app/mobile-approval-cockpit-v2",
                "offline_safe_route": "/app/home",
            },
            "capabilities": {
                "continuous_chat": True,
                "inline_action_cards": True,
                "one_tap_actions": True,
                "mobile_approvals": True,
                "offline_cache_supported_by_sync_chat": True,
                "secret_like_message_blocking": True,
                "destructive_actions_require_approval": True,
            },
            "safe_buttons": [
                {"id": "chat", "label": "Chat", "route": "/app/operator-chat-sync-cards", "priority": "critical"},
                {"id": "money", "label": "Ganhar dinheiro", "route": "/app/money-command-center", "priority": "high"},
                {"id": "approvals", "label": "Aprovações", "route": "/app/mobile-approval-cockpit-v2", "priority": "high"},
                {"id": "home", "label": "Home", "route": "/app/god-mode-home", "priority": "medium"},
                {"id": "legacy-chat", "label": "Chat antigo", "route": "/app/operator-chat-sync", "priority": "low"},
            ],
            "snapshots": {
                "home": home,
                "renderer": renderer,
                "cards": cards,
                "approvals": approvals,
                "chat_snapshot": chat_snapshot,
            },
            "operator_hint": "Abrir /app/operator-chat-sync-cards por defeito. Usar /app/operator-chat-sync apenas como fallback.",
        }

        def mutate(store: Dict[str, Any]) -> Dict[str, Any]:
            store = self._normalize_store(store)
            store["launches"].append({
                "manifest_id": manifest["manifest_id"],
                "created_at": manifest["created_at"],
                "tenant_id": tenant_id,
                "device_id": device_id,
                "default_route": manifest["launch_policy"]["default_route"],
            })
            store["launches"] = store["launches"][-300:]
            return store

        APK_LAUNCH_STORE.update(mutate)
        return {"ok": True, "mode": "apk_launch_manifest", "manifest": manifest}

    def health(self, tenant_id: str = "owner-andre", device_id: str = "android-apk") -> Dict[str, Any]:
        manifest = self.build_manifest(tenant_id=tenant_id, device_id=device_id).get("manifest", {})
        snapshots = manifest.get("snapshots", {})
        required = ["home", "renderer", "cards", "approvals", "chat_snapshot"]
        failed = [name for name in required if not snapshots.get(name, {}).get("ok")]
        status = "green" if not failed else "yellow"
        report = {
            "health_id": f"apk-health-{uuid4().hex[:12]}",
            "created_at": self._now(),
            "tenant_id": tenant_id,
            "device_id": device_id,
            "status": status,
            "failed_components": failed,
            "default_route": manifest.get("launch_policy", {}).get("default_route"),
            "fallback_route": manifest.get("launch_policy", {}).get("fallback_route"),
        }

        def mutate(store: Dict[str, Any]) -> Dict[str, Any]:
            store = self._normalize_store(store)
            store["health_checks"].append(report)
            store["health_checks"] = store["health_checks"][-300:]
            return store

        APK_LAUNCH_STORE.update(mutate)
        return {"ok": True, "mode": "apk_launch_health", "health": report, "manifest": manifest}

    def build_dashboard(self, tenant_id: str = "owner-andre", device_id: str = "android-apk") -> Dict[str, Any]:
        store = self._load_store()
        health = self.health(tenant_id=tenant_id, device_id=device_id)
        return {
            "ok": True,
            "mode": "apk_launch_dashboard",
            "tenant_id": tenant_id,
            "device_id": device_id,
            "status": self.get_status(),
            "health": health.get("health"),
            "manifest": health.get("manifest"),
            "recent_launches": store.get("launches", [])[-20:],
            "recent_health_checks": store.get("health_checks", [])[-20:],
        }

    def get_package(self) -> Dict[str, Any]:
        return {"ok": True, "mode": "apk_launch_package", "package": {"status": self.get_status(), "dashboard": self.build_dashboard()}}


apk_launch_manifest_service = ApkLaunchManifestService()
