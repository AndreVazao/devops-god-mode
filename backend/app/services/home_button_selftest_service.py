from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Set

from app.services.god_mode_home_service import god_mode_home_service


class HomeButtonSelfTestService:
    """Validates that Home quick actions are reachable by the APK/WebView client."""

    SAFE_POST_ENDPOINTS = {
        "/api/pro-operator/panel",
        "/api/start-now/panel",
        "/api/professional-scorecard/scorecard",
        "/api/local-ai/panel",
        "/api/pc-link-helper/panel",
        "/api/home-command-wizard/panel",
        "/api/first-real-install-launcher/plan",
        "/api/home-operator-ux/panel",
        "/api/install-readiness-final/check",
        "/api/home-system-health/snapshot",
        "/api/install-first-run/guide",
        "/api/artifacts-center/dashboard",
        "/api/god-mode-home/start-autopilot",
        "/api/god-mode-home/stop-autopilot",
        "/api/god-mode-home/approve-next",
        "/api/ready-to-use/checklist",
    }

    DANGEROUS_OR_STATEFUL = {
        "/api/god-mode-home/start-autopilot",
        "/api/god-mode-home/stop-autopilot",
        "/api/god-mode-home/approve-next",
        "/api/god-mode-home/continue",
        "/api/pro-operator/run",
    }

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def _route_methods(self) -> Dict[str, Set[str]]:
        from main import app

        mapping: Dict[str, Set[str]] = {}
        for route in app.routes:
            path = getattr(route, "path", "")
            methods = getattr(route, "methods", set()) or set()
            if path:
                mapping.setdefault(path, set()).update(methods)
        return mapping

    def build_report(self, tenant_id: str = "owner-andre") -> Dict[str, Any]:
        home = god_mode_home_service.build_dashboard(tenant_id=tenant_id)
        actions = home.get("quick_actions", [])
        route_methods = self._route_methods()
        checks = [self._check_action(action, route_methods) for action in actions]
        failed = [item for item in checks if not item["ok"]]
        warnings = [item for item in checks if item.get("warning")]
        score = round((sum(1 for item in checks if item["ok"]) / len(checks)) * 100) if checks else 0
        return {
            "ok": not failed,
            "mode": "home_button_selftest_report",
            "created_at": self._now(),
            "tenant_id": tenant_id,
            "status": "ready" if not failed else "attention",
            "score": score,
            "action_count": len(actions),
            "passed_count": len(checks) - len(failed),
            "failed_count": len(failed),
            "warning_count": len(warnings),
            "checks": checks,
            "failed_checks": failed,
            "warnings": warnings,
            "operator_next": self._next_action(failed),
            "client_contract": {
                "home_buttons_may_call_post": True,
                "read_panels_have_post_aliases": True,
                "stateful_actions_are_marked": True,
                "routes_are_verified_against_fastapi_app": True,
            },
        }

    def _check_action(self, action: Dict[str, Any], route_methods: Dict[str, Set[str]]) -> Dict[str, Any]:
        action_id = action.get("id") or action.get("label") or "unknown"
        label = action.get("label") or action_id
        endpoint = action.get("endpoint")
        route = action.get("route")
        if route and not endpoint:
            return {
                "id": action_id,
                "label": label,
                "kind": "frontend_route",
                "route": route,
                "ok": route.startswith("/app/"),
                "methods": [],
                "warning": None if route.startswith("/app/") else "route_should_start_with_app",
            }
        if not endpoint:
            return {
                "id": action_id,
                "label": label,
                "kind": "unknown",
                "ok": False,
                "error": "missing_endpoint_or_route",
                "methods": [],
            }
        methods = sorted(route_methods.get(endpoint, set()))
        exists = bool(methods)
        post_ok = "POST" in methods
        get_ok = "GET" in methods
        stateful = endpoint in self.DANGEROUS_OR_STATEFUL
        read_alias_expected = endpoint in self.SAFE_POST_ENDPOINTS and not stateful
        ok = exists and (post_ok or get_ok)
        if read_alias_expected:
            ok = exists and post_ok
        warning = None
        if stateful:
            warning = "stateful_action"
        elif exists and not post_ok:
            warning = "post_alias_missing"
        return {
            "id": action_id,
            "label": label,
            "kind": "api_endpoint",
            "endpoint": endpoint,
            "methods": methods,
            "exists": exists,
            "get_ok": get_ok,
            "post_ok": post_ok,
            "stateful": stateful,
            "read_alias_expected": read_alias_expected,
            "ok": ok,
            "warning": warning,
        }

    def _next_action(self, failed: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not failed:
            return {"label": "Usar Home no APK", "route": "/app/home"}
        first = failed[0]
        return {"label": f"Corrigir botão: {first.get('label')}", "endpoint": first.get("endpoint"), "route": "/app/home"}

    def get_status(self, tenant_id: str = "owner-andre") -> Dict[str, Any]:
        report = self.build_report(tenant_id=tenant_id)
        return {
            "ok": report["ok"],
            "mode": "home_button_selftest_status",
            "status": report["status"],
            "score": report["score"],
            "action_count": report["action_count"],
            "failed_count": report["failed_count"],
            "warning_count": report["warning_count"],
            "operator_next": report["operator_next"],
        }

    def get_package(self, tenant_id: str = "owner-andre") -> Dict[str, Any]:
        return {"ok": True, "mode": "home_button_selftest_package", "package": {"status": self.get_status(tenant_id=tenant_id), "report": self.build_report(tenant_id=tenant_id)}}


home_button_selftest_service = HomeButtonSelfTestService()
