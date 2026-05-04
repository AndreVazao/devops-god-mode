from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, Dict, List

from app.services.home_app_control_surface_service import home_app_control_surface_service
from app.services.operator_action_journal_service import operator_action_journal_service


class CockpitRuntimeUxService:
    """Runtime UX layer for the mobile-first God Mode cockpit.

    This service does not execute privileged actions itself. It gives the cockpit
    a stable polling package and records operator-visible button events into the
    existing operator action journal.
    """

    SERVICE_ID = "cockpit_runtime_ux"
    VERSION = "phase_176_v1"
    DEFAULT_TENANT_ID = "owner-andre"
    COCKPIT_THREAD_ID = "god-mode-cockpit"

    def _now(self) -> str:
        return datetime.now(UTC).isoformat()

    def status(self, tenant_id: str = DEFAULT_TENANT_ID) -> Dict[str, Any]:
        control = home_app_control_surface_service.status()
        journal = operator_action_journal_service.get_status()
        return {
            "ok": True,
            "service": self.SERVICE_ID,
            "version": self.VERSION,
            "tenant_id": tenant_id,
            "generated_at": self._now(),
            "canonical_cockpit_route": "/app/home",
            "mobile_first": True,
            "pc_brain": True,
            "polling_enabled": True,
            "polling_seconds": 10,
            "button_logging_enabled": True,
            "visible_history_enabled": True,
            "control_surface_ok": bool(control.get("ok")),
            "journal_ok": bool(journal.get("ok")),
            "module_count": control.get("module_count", 0),
            "button_count": control.get("button_count", 0),
        }

    def package(self, tenant_id: str = DEFAULT_TENANT_ID, history_limit: int = 25) -> Dict[str, Any]:
        control = home_app_control_surface_service.package()
        history = self.history(tenant_id=tenant_id, limit=history_limit)
        return {
            "ok": True,
            "service": self.SERVICE_ID,
            "status": self.status(tenant_id=tenant_id),
            "control_surface": control,
            "history": history,
            "runtime_contract": {
                "poll_endpoint": "/api/cockpit-runtime-ux/package",
                "log_endpoint": "/api/cockpit-runtime-ux/log-button-event",
                "history_endpoint": "/api/cockpit-runtime-ux/history",
                "polling_seconds": 10,
                "tenant_id": tenant_id,
                "thread_id": self.COCKPIT_THREAD_ID,
            },
            "mobile_operator_rules": [
                "Use big buttons and short summaries on phone.",
                "Never expose secrets in output/history.",
                "High-risk actions must remain behind server-side gates.",
                "The PC is the execution brain; the phone is command/approval cockpit.",
            ],
        }

    def history(self, tenant_id: str = DEFAULT_TENANT_ID, limit: int = 25) -> Dict[str, Any]:
        return operator_action_journal_service.list_entries(
            tenant_id=tenant_id,
            thread_id=self.COCKPIT_THREAD_ID,
            limit=max(1, min(int(limit), 100)),
        )

    def log_button_event(
        self,
        button_id: str,
        label: str,
        endpoint: str,
        method: str = "GET",
        risk: str = "safe",
        phase: str = "clicked",
        outcome: str = "recorded",
        tenant_id: str = DEFAULT_TENANT_ID,
        module_id: str | None = None,
        status_code: int | None = None,
        ok: bool | None = None,
        error: str | None = None,
    ) -> Dict[str, Any]:
        safe_button_id = self._safe_text(button_id)[:120]
        safe_label = self._safe_text(label)[:180]
        safe_endpoint = self._safe_endpoint(endpoint)
        safe_method = self._safe_text(method).upper()[:12]
        safe_risk = self._safe_text(risk)[:40]
        safe_phase = self._safe_text(phase)[:40]
        summary = f"{safe_phase}: {safe_label} [{safe_method} {safe_endpoint}]"
        details = {
            "button_id": safe_button_id,
            "label": safe_label,
            "endpoint": safe_endpoint,
            "method": safe_method,
            "risk": safe_risk,
            "phase": safe_phase,
            "module_id": self._safe_text(module_id or "unknown")[:120],
            "status_code": status_code,
            "ok": ok,
            "error_summary": self._safe_text(error or "")[:240],
            "redacted": True,
        }
        return operator_action_journal_service.log_event(
            tenant_id=tenant_id,
            thread_id=self.COCKPIT_THREAD_ID,
            event_type="cockpit_button_event",
            summary=summary,
            outcome=self._safe_text(outcome)[:80],
            details=details,
            origin=self.SERVICE_ID,
        )

    def quick_history_cards(self, tenant_id: str = DEFAULT_TENANT_ID, limit: int = 10) -> Dict[str, Any]:
        history = self.history(tenant_id=tenant_id, limit=limit)
        cards: List[Dict[str, Any]] = []
        for item in history.get("entries", []):
            cards.append({
                "id": item.get("entry_id"),
                "title": item.get("summary"),
                "subtitle": item.get("outcome"),
                "created_at": item.get("created_at"),
                "event_type": item.get("event_type"),
            })
        return {"ok": True, "cards": cards, "count": len(cards)}

    def _safe_text(self, value: Any) -> str:
        text = str(value or "")
        blocked = ["password", "token", "secret", "cookie", "authorization", "bearer", "api_key", "private_key"]
        lowered = text.lower()
        if any(word in lowered for word in blocked):
            return "[REDACTED]"
        return text.replace("\n", " ").replace("\r", " ")

    def _safe_endpoint(self, endpoint: str) -> str:
        text = self._safe_text(endpoint)
        if not text.startswith("/"):
            return "/"
        return text.split("?", 1)[0][:180]


cockpit_runtime_ux_service = CockpitRuntimeUxService()
