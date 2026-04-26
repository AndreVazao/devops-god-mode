from __future__ import annotations

import threading
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List
from uuid import uuid4

from app.services.chat_autopilot_supervisor_service import chat_autopilot_supervisor_service
from app.services.request_worker_loop_service import request_worker_loop_service
from app.utils.atomic_json_store import AtomicJsonStore

DATA_DIR = Path("data")
PC_AUTOPILOT_FILE = DATA_DIR / "pc_autopilot_loop.json"
PC_AUTOPILOT_STORE = AtomicJsonStore(
    PC_AUTOPILOT_FILE,
    default_factory=lambda: {
        "version": 1,
        "settings": {
            "enabled": False,
            "interval_seconds": 30,
            "tenant_id": "owner-andre",
            "max_rounds_per_cycle": 3,
            "max_jobs_per_round": 4,
            "run_when_apk_disconnected": True,
            "approval_bypass": False,
        },
        "cycles": [],
        "events": [],
    },
)


class PcAutopilotLoopService:
    """PC-side autopilot loop controller.

    The service is safe by default: it is disabled until started, never bypasses
    approvals, and only drives the existing request worker/autopilot stack.
    """

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._thread: threading.Thread | None = None
        self._stop_event = threading.Event()

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def _normalize(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        payload.setdefault("version", 1)
        payload.setdefault("settings", {})
        payload.setdefault("cycles", [])
        payload.setdefault("events", [])
        settings = payload["settings"]
        settings.setdefault("enabled", False)
        settings.setdefault("interval_seconds", 30)
        settings.setdefault("tenant_id", "owner-andre")
        settings.setdefault("max_rounds_per_cycle", 3)
        settings.setdefault("max_jobs_per_round", 4)
        settings.setdefault("run_when_apk_disconnected", True)
        settings.setdefault("approval_bypass", False)
        return payload

    def _load(self) -> Dict[str, Any]:
        return self._normalize(PC_AUTOPILOT_STORE.load())

    def _save_event(self, event: str, detail: str | None = None) -> None:
        def mutate(payload: Dict[str, Any]) -> Dict[str, Any]:
            payload = self._normalize(payload)
            payload["events"].append({"created_at": self._now(), "event": event, "detail": detail})
            payload["events"] = payload["events"][-300:]
            return payload

        PC_AUTOPILOT_STORE.update(mutate)

    def _save_cycle(self, cycle: Dict[str, Any]) -> None:
        def mutate(payload: Dict[str, Any]) -> Dict[str, Any]:
            payload = self._normalize(payload)
            payload["cycles"].append(cycle)
            payload["cycles"] = payload["cycles"][-500:]
            return payload

        PC_AUTOPILOT_STORE.update(mutate)

    def configure(
        self,
        enabled: bool | None = None,
        interval_seconds: int | None = None,
        tenant_id: str | None = None,
        max_rounds_per_cycle: int | None = None,
        max_jobs_per_round: int | None = None,
    ) -> Dict[str, Any]:
        def mutate(payload: Dict[str, Any]) -> Dict[str, Any]:
            payload = self._normalize(payload)
            settings = payload["settings"]
            if enabled is not None:
                settings["enabled"] = bool(enabled)
            if interval_seconds is not None:
                settings["interval_seconds"] = max(5, min(int(interval_seconds), 3600))
            if tenant_id:
                settings["tenant_id"] = tenant_id
            if max_rounds_per_cycle is not None:
                settings["max_rounds_per_cycle"] = max(1, min(int(max_rounds_per_cycle), 20))
            if max_jobs_per_round is not None:
                settings["max_jobs_per_round"] = max(1, min(int(max_jobs_per_round), 20))
            settings["approval_bypass"] = False
            settings["run_when_apk_disconnected"] = True
            return payload

        updated = PC_AUTOPILOT_STORE.update(mutate)
        state = self._normalize(updated.get("payload", {}))
        self._save_event("configure", "settings updated")
        return {"ok": True, "mode": "pc_autopilot_loop_configure", "settings": state["settings"]}

    def get_status(self) -> Dict[str, Any]:
        state = self._load()
        worker = request_worker_loop_service.get_status()
        thread_alive = bool(self._thread and self._thread.is_alive())
        return {
            "ok": True,
            "mode": "pc_autopilot_loop_status",
            "status": "running" if thread_alive else ("enabled_idle" if state["settings"].get("enabled") else "disabled"),
            "settings": state["settings"],
            "thread_alive": thread_alive,
            "apk_disconnect_safe": True,
            "approval_bypass": False,
            "cycle_count": len(state.get("cycles", [])),
            "event_count": len(state.get("events", [])),
            "worker_status": worker,
        }

    def run_cycle(self, reason: str = "manual_cycle") -> Dict[str, Any]:
        state = self._load()
        settings = state["settings"]
        cycle_id = f"pc-autopilot-cycle-{uuid4().hex[:12]}"
        tenant_id = settings.get("tenant_id", "owner-andre")
        started_at = self._now()
        supervisor = chat_autopilot_supervisor_service.run_until_blocked_or_idle(
            tenant_id=tenant_id,
            job_id=None,
            reason=reason,
            max_rounds=int(settings.get("max_rounds_per_cycle", 3)),
            max_jobs_per_round=int(settings.get("max_jobs_per_round", 4)),
        )
        report = supervisor.get("report", {}) if isinstance(supervisor, dict) else {}
        cycle = {
            "cycle_id": cycle_id,
            "started_at": started_at,
            "finished_at": self._now(),
            "tenant_id": tenant_id,
            "reason": reason,
            "supervisor_run_id": report.get("run_id"),
            "stop_reason": report.get("stop_reason"),
            "processed_total": report.get("processed_total", 0),
            "blocked_total": report.get("blocked_total", 0),
            "failed_total": report.get("failed_total", 0),
            "needs_operator": bool(report.get("needs_operator", False)),
            "approval_bypass": False,
        }
        self._save_cycle(cycle)
        return {"ok": True, "mode": "pc_autopilot_loop_cycle", "cycle": cycle, "supervisor": supervisor}

    def start(self) -> Dict[str, Any]:
        self.configure(enabled=True)
        with self._lock:
            if self._thread and self._thread.is_alive():
                return {"ok": True, "mode": "pc_autopilot_loop_start", "status": "already_running", "state": self.get_status()}
            self._stop_event.clear()
            self._thread = threading.Thread(target=self._loop, name="godmode-pc-autopilot-loop", daemon=True)
            self._thread.start()
        self._save_event("start", "pc autopilot loop started")
        return {"ok": True, "mode": "pc_autopilot_loop_start", "status": "started", "state": self.get_status()}

    def stop(self) -> Dict[str, Any]:
        self.configure(enabled=False)
        self._stop_event.set()
        self._save_event("stop", "pc autopilot loop stop requested")
        return {"ok": True, "mode": "pc_autopilot_loop_stop", "status": "stopping", "state": self.get_status()}

    def _loop(self) -> None:
        self._save_event("loop_enter", "daemon thread entered")
        while not self._stop_event.is_set():
            state = self._load()
            settings = state["settings"]
            if not settings.get("enabled", False):
                break
            try:
                self.run_cycle(reason="pc_autopilot_background_loop")
            except Exception as exc:
                self._save_event("cycle_error", exc.__class__.__name__)
            interval = max(5, min(int(settings.get("interval_seconds", 30)), 3600))
            if self._stop_event.wait(interval):
                break
        self._save_event("loop_exit", "daemon thread exited")

    def latest(self) -> Dict[str, Any]:
        state = self._load()
        return {
            "ok": True,
            "mode": "pc_autopilot_loop_latest",
            "cycle": state.get("cycles", [])[-1] if state.get("cycles") else None,
            "event": state.get("events", [])[-1] if state.get("events") else None,
        }

    def build_dashboard(self) -> Dict[str, Any]:
        state = self._load()
        return {
            "ok": True,
            "mode": "pc_autopilot_loop_dashboard",
            "status": self.get_status(),
            "recent_cycles": state.get("cycles", [])[-20:],
            "recent_events": state.get("events", [])[-20:],
            "buttons": [
                {"id": "start", "label": "Ligar loop PC", "endpoint": "/api/pc-autopilot/start", "priority": "critical"},
                {"id": "cycle", "label": "Ciclo agora", "endpoint": "/api/pc-autopilot/cycle", "priority": "high"},
                {"id": "stop", "label": "Parar loop", "endpoint": "/api/pc-autopilot/stop", "priority": "medium"},
                {"id": "approvals", "label": "Aprovações", "route": "/app/mobile-approval-cockpit-v2", "priority": "high"},
            ],
        }

    def get_package(self) -> Dict[str, Any]:
        return {"ok": True, "mode": "pc_autopilot_loop_package", "package": {"status": self.get_status(), "latest": self.latest(), "dashboard": self.build_dashboard()}}


pc_autopilot_loop_service = PcAutopilotLoopService()
