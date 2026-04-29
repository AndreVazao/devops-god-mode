from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List

from app.services.god_mode_home_service import god_mode_home_service
from app.services.home_button_selftest_service import home_button_selftest_service
from app.services.professional_scorecard_service import professional_scorecard_service
from app.services.start_now_panel_service import start_now_panel_service


class MobileResultNormalizerService:
    """Normalize backend action results into mobile-friendly cards.

    The APK/WebView should not need to understand every service-specific JSON
    shape. This service creates a stable presentation contract for Home actions.
    """

    COLOR_BY_STATUS = {
        "ready": "green",
        "ready_to_install": "green",
        "ready_to_launch": "green",
        "professional_ready": "green",
        "executed": "green",
        "ok": "green",
        "attention": "yellow",
        "usable_with_attention": "yellow",
        "waiting_operator_approval": "yellow",
        "check_install_first": "yellow",
        "blocked": "red",
        "not_ready": "red",
        "failed": "red",
        "error": "red",
    }

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def normalize(self, payload: Dict[str, Any], source_endpoint: str | None = None, label: str | None = None) -> Dict[str, Any]:
        if not isinstance(payload, dict):
            payload = {"ok": False, "raw": payload}
        status = self._status(payload)
        ok = self._ok(payload, status)
        title = label or self._title(payload, source_endpoint)
        color = self.COLOR_BY_STATUS.get(status, "green" if ok else "yellow")
        card = {
            "title": title,
            "status": status,
            "color": color,
            "summary": self._summary(payload, status=status, ok=ok),
            "badges": self._badges(payload),
            "metrics": self._metrics(payload),
            "primary_action": self._primary_action(payload, source_endpoint=source_endpoint),
            "secondary_actions": self._secondary_actions(payload),
            "show_json_available": True,
        }
        return {
            "ok": ok,
            "mode": "mobile_result_normalized",
            "created_at": self._now(),
            "source_endpoint": source_endpoint,
            "source_mode": payload.get("mode"),
            "card": card,
            "raw": payload,
        }

    def normalize_home(self, tenant_id: str = "owner-andre") -> Dict[str, Any]:
        home = god_mode_home_service.build_dashboard(tenant_id=tenant_id)
        return self.normalize(home, source_endpoint="/api/god-mode-home/dashboard", label="Home")

    def build_catalog(self, tenant_id: str = "owner-andre", requested_project: str = "GOD_MODE") -> Dict[str, Any]:
        home = god_mode_home_service.build_dashboard(tenant_id=tenant_id)
        selftest = home_button_selftest_service.build_report(tenant_id=tenant_id)
        scorecard = professional_scorecard_service.build_scorecard(
            tenant_id=tenant_id,
            requested_project=requested_project,
        )
        start_now = start_now_panel_service.build_panel(
            tenant_id=tenant_id,
            requested_project=requested_project,
        )
        previews = [
            self.normalize(home, source_endpoint="/api/god-mode-home/dashboard", label="Home"),
            self.normalize(start_now, source_endpoint="/api/start-now/panel", label="Começar agora"),
            self.normalize(scorecard, source_endpoint="/api/professional-scorecard/scorecard", label="Score profissional"),
            self.normalize(selftest, source_endpoint="/api/home-button-selftest/report", label="Testar botões"),
        ]
        actions = [
            {
                "id": action.get("id"),
                "label": action.get("label"),
                "endpoint": action.get("endpoint"),
                "route": action.get("route"),
                "priority": action.get("priority"),
                "result_card_supported": bool(action.get("endpoint") or action.get("route")),
            }
            for action in home.get("quick_actions", [])
        ]
        return {
            "ok": True,
            "mode": "mobile_result_catalog",
            "created_at": self._now(),
            "tenant_id": tenant_id,
            "requested_project": requested_project,
            "contract": self.presentation_contract(),
            "preview_count": len(previews),
            "previews": previews,
            "home_action_count": len(actions),
            "home_actions": actions,
            "operator_next": {"label": "Abrir Home", "route": "/app/home"},
        }

    def presentation_contract(self) -> Dict[str, Any]:
        return {
            "version": 1,
            "card_fields": [
                "title",
                "status",
                "color",
                "summary",
                "badges",
                "metrics",
                "primary_action",
                "secondary_actions",
                "show_json_available",
            ],
            "colors": ["green", "yellow", "red", "blue"],
            "mobile_rules": [
                "show_title_first",
                "show_color_as_traffic_light",
                "show_primary_action_as_main_button",
                "keep_json_behind_toggle",
            ],
        }

    def _status(self, payload: Dict[str, Any]) -> str:
        for key in ["status", "state", "result_status"]:
            value = payload.get(key)
            if isinstance(value, str) and value:
                return value
        if payload.get("ready_to_install") is True:
            return "ready_to_install"
        if payload.get("ready_to_launch") is True:
            return "ready_to_launch"
        if payload.get("ok") is False:
            return "failed"
        return "ready" if payload.get("ok", True) else "attention"

    def _ok(self, payload: Dict[str, Any], status: str) -> bool:
        if payload.get("ok") is False:
            return False
        if payload.get("failed_count", 0):
            return False
        if payload.get("failed_checks"):
            return False
        return status not in {"blocked", "not_ready", "failed", "error"}

    def _title(self, payload: Dict[str, Any], source_endpoint: str | None) -> str:
        if payload.get("headline"):
            return str(payload["headline"])
        mode = str(payload.get("mode") or "").replace("_", " ").strip().title()
        if mode:
            return mode
        if source_endpoint:
            return source_endpoint.strip("/").split("/")[-1].replace("-", " ").title()
        return "Resultado"

    def _summary(self, payload: Dict[str, Any], status: str, ok: bool) -> str:
        for key in ["operator_summary", "summary", "operator_message", "headline"]:
            value = payload.get(key)
            if isinstance(value, str) and value:
                return value[:260]
        if payload.get("failed_count"):
            return f"{payload.get('failed_count')} ponto(s) precisam atenção."
        if payload.get("score") is not None:
            return f"Estado {status} · score {payload.get('score')}%."
        return "Pronto." if ok else "Precisa atenção."

    def _badges(self, payload: Dict[str, Any]) -> List[Dict[str, str]]:
        badges: List[Dict[str, str]] = []
        for key in ["mode", "status", "grade", "requested_project", "tenant_id"]:
            value = payload.get(key)
            if value is not None and value != "":
                badges.append({"label": key, "value": str(value)[:80]})
        if payload.get("ready_to_install") is True:
            badges.append({"label": "install", "value": "ready"})
        if payload.get("ready_to_launch") is True:
            badges.append({"label": "launch", "value": "ready"})
        return badges[:8]

    def _metrics(self, payload: Dict[str, Any]) -> List[Dict[str, Any]]:
        metrics: List[Dict[str, Any]] = []
        candidates = [
            ("score", "Score"),
            ("health_score", "Saúde"),
            ("readiness_score", "Prontidão"),
            ("action_count", "Ações"),
            ("failed_count", "Falhas"),
            ("warning_count", "Avisos"),
            ("artifact_count", "Artifacts"),
            ("blocker_count", "Blockers"),
        ]
        for key, label in candidates:
            value = payload.get(key)
            if value is not None:
                metrics.append({"label": label, "value": value})
        signals = payload.get("signals")
        if isinstance(signals, dict):
            for key in ["install_score", "artifact_count", "wizard_command_count", "local_ai_status"]:
                if key in signals:
                    metrics.append({"label": key.replace("_", " ").title(), "value": signals[key]})
        return metrics[:8]

    def _primary_action(self, payload: Dict[str, Any], source_endpoint: str | None) -> Dict[str, Any]:
        action = payload.get("operator_next") or payload.get("primary_action") or {}
        if isinstance(action, dict) and action:
            return action
        if source_endpoint:
            return {"label": "Recarregar", "endpoint": source_endpoint}
        return {"label": "Voltar à Home", "route": "/app/home"}

    def _secondary_actions(self, payload: Dict[str, Any]) -> List[Dict[str, Any]]:
        actions: List[Dict[str, Any]] = []
        for key in ["quick_buttons", "home_actions"]:
            value = payload.get(key)
            if isinstance(value, list):
                actions.extend(item for item in value if isinstance(item, dict))
        actions.append({"label": "Home", "route": "/app/home"})
        return actions[:6]

    def get_status(self, tenant_id: str = "owner-andre") -> Dict[str, Any]:
        catalog = self.build_catalog(tenant_id=tenant_id)
        return {
            "ok": True,
            "mode": "mobile_result_normalizer_status",
            "preview_count": catalog["preview_count"],
            "home_action_count": catalog["home_action_count"],
            "contract_version": catalog["contract"]["version"],
            "operator_next": catalog["operator_next"],
        }

    def get_package(self, tenant_id: str = "owner-andre", requested_project: str = "GOD_MODE") -> Dict[str, Any]:
        return {
            "ok": True,
            "mode": "mobile_result_normalizer_package",
            "package": {
                "status": self.get_status(tenant_id=tenant_id),
                "catalog": self.build_catalog(tenant_id=tenant_id, requested_project=requested_project),
            },
        }


mobile_result_normalizer_service = MobileResultNormalizerService()
