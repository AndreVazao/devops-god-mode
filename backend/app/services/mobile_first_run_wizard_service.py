from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List
from uuid import uuid4

from app.services.apk_launch_manifest_service import apk_launch_manifest_service
from app.services.apk_manifest_router_service import apk_manifest_router_service
from app.services.chat_inline_card_renderer_service import chat_inline_card_renderer_service
from app.services.mobile_start_config_service import mobile_start_config_service
from app.services.operator_chat_runtime_snapshot_service import operator_chat_runtime_snapshot_service
from app.utils.atomic_json_store import AtomicJsonStore

DATA_DIR = Path("data")
FIRST_RUN_FILE = DATA_DIR / "mobile_first_run_wizard.json"
FIRST_RUN_STORE = AtomicJsonStore(
    FIRST_RUN_FILE,
    default_factory=lambda: {"checks": [], "starts": []},
)


class MobileFirstRunWizardService:
    """Simple mobile/APK first-run wizard with one clear next button."""

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def _normalize_store(self, store: Dict[str, Any]) -> Dict[str, Any]:
        if not isinstance(store, dict):
            return {"checks": [], "starts": []}
        store.setdefault("checks", [])
        store.setdefault("starts", [])
        return store

    def _load_store(self) -> Dict[str, Any]:
        return self._normalize_store(FIRST_RUN_STORE.load())

    def _safe(self, component: str, fn: Any) -> Dict[str, Any]:
        try:
            result = fn()
            return {"component": component, "ok": bool(result.get("ok", True)), "result": result}
        except Exception as exc:  # pragma: no cover - wizard must fail soft
            return {"component": component, "ok": False, "error": str(exc)}

    def get_status(self) -> Dict[str, Any]:
        store = self._load_store()
        return {
            "ok": True,
            "mode": "mobile_first_run_wizard_status",
            "status": "mobile_first_run_wizard_ready",
            "store_file": str(FIRST_RUN_FILE),
            "atomic_store_enabled": True,
            "check_count": len(store.get("checks", [])),
            "start_count": len(store.get("starts", [])),
        }

    def run_check(self, tenant_id: str = "owner-andre", device_id: str = "android-apk") -> Dict[str, Any]:
        checks = [
            self._safe("mobile_start_config", lambda: mobile_start_config_service.validate_config()),
            self._safe("launch_plan", lambda: mobile_start_config_service.build_launch_plan(tenant_id=tenant_id, device_id=device_id)),
            self._safe("apk_manifest", lambda: apk_launch_manifest_service.build_manifest(tenant_id=tenant_id, device_id=device_id)),
            self._safe("apk_router", lambda: apk_manifest_router_service.resolve(tenant_id=tenant_id, device_id=device_id, prefer="auto")),
            self._safe("chat_inline_renderer", lambda: chat_inline_card_renderer_service.build_manifest(tenant_id=tenant_id)),
            self._safe("chat_snapshot", lambda: operator_chat_runtime_snapshot_service.build_snapshot(tenant_id=tenant_id)),
        ]
        failed = [item for item in checks if not item.get("ok")]
        warning_components: List[str] = []
        for item in checks:
            result = item.get("result", {})
            if result.get("mode") == "mobile_start_config_validation" and result.get("validation", {}).get("status") != "green":
                warning_components.append(item["component"])
        status = "green" if not failed and not warning_components else ("yellow" if not failed else "red")
        router_result = next((item.get("result", {}) for item in checks if item.get("component") == "apk_router"), {})
        route = router_result.get("resolution", {}).get("route", "/app/apk-start")
        fallback = router_result.get("resolution", {}).get("fallback_route", "/app/operator-chat-sync")
        check = {
            "check_id": f"first-run-check-{uuid4().hex[:12]}",
            "created_at": self._now(),
            "tenant_id": tenant_id,
            "device_id": device_id,
            "status": status,
            "failed_components": [item["component"] for item in failed],
            "warning_components": warning_components,
            "recommended_route": route,
            "fallback_route": fallback,
            "safe_home_route": "/app/home",
            "checks": checks,
            "operator_message": self._operator_message(status, route, fallback),
        }

        def mutate(store: Dict[str, Any]) -> Dict[str, Any]:
            store = self._normalize_store(store)
            store["checks"].append(check)
            store["checks"] = store["checks"][-300:]
            return store

        FIRST_RUN_STORE.update(mutate)
        return {"ok": True, "mode": "mobile_first_run_check", "check": check}

    def _operator_message(self, status: str, route: str, fallback: str) -> str:
        if status == "green":
            return f"Tudo pronto. Abre {route}."
        if status == "yellow":
            return f"Quase pronto. Podes abrir {route}, mas mantém {fallback} como fallback."
        return f"Há falhas. Usa {fallback} ou /app/home até resolver."

    def start(self, tenant_id: str = "owner-andre", device_id: str = "android-apk") -> Dict[str, Any]:
        check = self.run_check(tenant_id=tenant_id, device_id=device_id).get("check", {})
        start = {
            "start_id": f"first-run-start-{uuid4().hex[:12]}",
            "created_at": self._now(),
            "tenant_id": tenant_id,
            "device_id": device_id,
            "status": check.get("status"),
            "open_route": check.get("recommended_route") if check.get("status") in {"green", "yellow"} else check.get("fallback_route"),
            "fallback_route": check.get("fallback_route"),
            "safe_home_route": check.get("safe_home_route"),
            "operator_message": check.get("operator_message"),
        }

        def mutate(store: Dict[str, Any]) -> Dict[str, Any]:
            store = self._normalize_store(store)
            store["starts"].append(start)
            store["starts"] = store["starts"][-300:]
            return store

        FIRST_RUN_STORE.update(mutate)
        return {"ok": True, "mode": "mobile_first_run_start", "start": start, "check": check}

    def build_dashboard(self, tenant_id: str = "owner-andre", device_id: str = "android-apk") -> Dict[str, Any]:
        store = self._load_store()
        check = self.run_check(tenant_id=tenant_id, device_id=device_id).get("check", {})
        return {
            "ok": True,
            "mode": "mobile_first_run_dashboard",
            "tenant_id": tenant_id,
            "device_id": device_id,
            "status": self.get_status(),
            "check": check,
            "buttons": [
                {"id": "start", "label": "Entrar no God Mode", "route": check.get("recommended_route", "/app/apk-start"), "priority": "critical"},
                {"id": "fallback", "label": "Chat fallback", "route": check.get("fallback_route", "/app/operator-chat-sync"), "priority": "high"},
                {"id": "home", "label": "Home segura", "route": "/app/home", "priority": "medium"},
                {"id": "config", "label": "Config mobile", "route": "/app/mobile-start-config", "priority": "low"},
            ],
            "recent_checks": store.get("checks", [])[-20:],
            "recent_starts": store.get("starts", [])[-20:],
        }

    def get_package(self) -> Dict[str, Any]:
        return {"ok": True, "mode": "mobile_first_run_wizard_package", "package": {"status": self.get_status(), "dashboard": self.build_dashboard()}}


mobile_first_run_wizard_service = MobileFirstRunWizardService()
