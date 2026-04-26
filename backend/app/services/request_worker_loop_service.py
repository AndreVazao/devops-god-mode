from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List
from uuid import uuid4

from app.services.request_orchestrator_service import request_orchestrator_service
from app.utils.atomic_json_store import AtomicJsonStore

DATA_DIR = Path("data")
REQUEST_WORKER_FILE = DATA_DIR / "request_worker_loop.json"
REQUEST_WORKER_STORE = AtomicJsonStore(
    REQUEST_WORKER_FILE,
    default_factory=lambda: {"ticks": [], "runs": [], "settings": {"enabled": True, "max_jobs_per_tick": 5}},
)

RUNNABLE_STATUSES = {"queued", "running"}
BLOCKED_PREFIX = "blocked"


class RequestWorkerLoopService:
    """Durable worker tick loop for request orchestrator jobs.

    This service is intentionally tick-based and explicit. It can be called by the API,
    future startup hooks, a scheduler, or a desktop local watchdog without depending on
    the APK staying connected.
    """

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def _normalize_store(self, store: Dict[str, Any]) -> Dict[str, Any]:
        if not isinstance(store, dict):
            return {"ticks": [], "runs": [], "settings": {"enabled": True, "max_jobs_per_tick": 5}}
        store.setdefault("ticks", [])
        store.setdefault("runs", [])
        store.setdefault("settings", {})
        store["settings"].setdefault("enabled", True)
        store["settings"].setdefault("max_jobs_per_tick", 5)
        return store

    def _load_store(self) -> Dict[str, Any]:
        return self._normalize_store(REQUEST_WORKER_STORE.load())

    def get_status(self) -> Dict[str, Any]:
        store = self._load_store()
        jobs = request_orchestrator_service.list_jobs(limit=1000).get("jobs", [])
        runnable = [job for job in jobs if job.get("status") in RUNNABLE_STATUSES]
        blocked = [job for job in jobs if str(job.get("status", "")).startswith(BLOCKED_PREFIX)]
        completed = [job for job in jobs if job.get("status") == "completed"]
        return {
            "ok": True,
            "mode": "request_worker_loop_status",
            "status": "request_worker_loop_ready",
            "store_file": str(REQUEST_WORKER_FILE),
            "atomic_store_enabled": True,
            "apk_disconnect_safe": True,
            "tick_based": True,
            "settings": store.get("settings", {}),
            "runnable_count": len(runnable),
            "blocked_count": len(blocked),
            "completed_count": len(completed),
            "tick_count": len(store.get("ticks", [])),
            "run_count": len(store.get("runs", [])),
        }

    def configure(self, enabled: bool | None = None, max_jobs_per_tick: int | None = None) -> Dict[str, Any]:
        def mutate(store: Dict[str, Any]) -> Dict[str, Any]:
            store = self._normalize_store(store)
            if enabled is not None:
                store["settings"]["enabled"] = bool(enabled)
            if max_jobs_per_tick is not None:
                store["settings"]["max_jobs_per_tick"] = max(1, min(int(max_jobs_per_tick), 50))
            return store

        updated = REQUEST_WORKER_STORE.update(mutate)
        payload = self._normalize_store(updated.get("payload", {}))
        return {"ok": True, "mode": "request_worker_loop_configure", "settings": payload.get("settings", {})}

    def _runnable_jobs(self, tenant_id: str = "owner-andre", limit: int = 1000) -> List[Dict[str, Any]]:
        jobs = request_orchestrator_service.list_jobs(tenant_id=tenant_id, limit=limit).get("jobs", [])
        return [job for job in jobs if job.get("status") in RUNNABLE_STATUSES]

    def tick(self, tenant_id: str = "owner-andre", max_jobs: int | None = None) -> Dict[str, Any]:
        store = self._load_store()
        settings = store.get("settings", {})
        if not settings.get("enabled", True):
            tick = {
                "tick_id": f"request-worker-tick-{uuid4().hex[:12]}",
                "created_at": self._now(),
                "tenant_id": tenant_id,
                "status": "disabled",
                "processed_count": 0,
                "blocked_count": 0,
                "completed_count": 0,
                "results": [],
            }
            self._record_tick(tick)
            return {"ok": True, "mode": "request_worker_loop_tick", "tick": tick}

        effective_max = int(max_jobs or settings.get("max_jobs_per_tick", 5))
        runnable = self._runnable_jobs(tenant_id=tenant_id)[:effective_max]
        results: List[Dict[str, Any]] = []
        for job in runnable:
            result = request_orchestrator_service.run_until_blocked(job_id=job["job_id"], tenant_id=tenant_id)
            final_job = result.get("job") or {}
            results.append(
                {
                    "job_id": job["job_id"],
                    "ok": bool(result.get("ok")),
                    "from_status": job.get("status"),
                    "to_status": final_job.get("status"),
                    "blocking_reason": final_job.get("blocking_reason"),
                    "processed_steps": result.get("processed_steps", 0),
                }
            )
        tick = {
            "tick_id": f"request-worker-tick-{uuid4().hex[:12]}",
            "created_at": self._now(),
            "tenant_id": tenant_id,
            "status": "completed",
            "processed_count": len(results),
            "blocked_count": len([item for item in results if str(item.get("to_status", "")).startswith(BLOCKED_PREFIX)]),
            "completed_count": len([item for item in results if item.get("to_status") == "completed"]),
            "results": results,
        }
        self._record_tick(tick)
        return {"ok": True, "mode": "request_worker_loop_tick", "tick": tick}

    def _record_tick(self, tick: Dict[str, Any]) -> None:
        def mutate(store: Dict[str, Any]) -> Dict[str, Any]:
            store = self._normalize_store(store)
            store["ticks"].append(tick)
            store["ticks"] = store["ticks"][-500:]
            return store

        REQUEST_WORKER_STORE.update(mutate)

    def run_for_ticks(self, tenant_id: str = "owner-andre", ticks: int = 3, max_jobs_per_tick: int | None = None) -> Dict[str, Any]:
        run = {
            "run_id": f"request-worker-run-{uuid4().hex[:12]}",
            "created_at": self._now(),
            "tenant_id": tenant_id,
            "requested_ticks": max(1, min(int(ticks), 25)),
            "tick_ids": [],
            "processed_count": 0,
            "blocked_count": 0,
            "completed_count": 0,
            "status": "running",
        }
        tick_results: List[Dict[str, Any]] = []
        for _ in range(run["requested_ticks"]):
            tick_result = self.tick(tenant_id=tenant_id, max_jobs=max_jobs_per_tick)
            tick = tick_result.get("tick", {})
            tick_results.append(tick)
            run["tick_ids"].append(tick.get("tick_id"))
            run["processed_count"] += int(tick.get("processed_count", 0))
            run["blocked_count"] += int(tick.get("blocked_count", 0))
            run["completed_count"] += int(tick.get("completed_count", 0))
            if tick.get("processed_count", 0) == 0:
                break
        run["finished_at"] = self._now()
        run["status"] = "completed"
        self._record_run(run)
        return {"ok": True, "mode": "request_worker_loop_run", "run": run, "ticks": tick_results}

    def _record_run(self, run: Dict[str, Any]) -> None:
        def mutate(store: Dict[str, Any]) -> Dict[str, Any]:
            store = self._normalize_store(store)
            store["runs"].append(run)
            store["runs"] = store["runs"][-300:]
            return store

        REQUEST_WORKER_STORE.update(mutate)

    def build_dashboard(self, tenant_id: str = "owner-andre") -> Dict[str, Any]:
        store = self._load_store()
        orchestrator = request_orchestrator_service.build_dashboard(tenant_id=tenant_id)
        return {
            "ok": True,
            "mode": "request_worker_loop_dashboard",
            "tenant_id": tenant_id,
            "status": self.get_status(),
            "orchestrator_summary": orchestrator.get("summary", {}),
            "recent_ticks": store.get("ticks", [])[-30:],
            "recent_runs": store.get("runs", [])[-20:],
            "buttons": [
                {"id": "tick", "label": "Processar agora", "endpoint": "/api/request-worker/tick", "priority": "high"},
                {"id": "run", "label": "Correr ciclos", "endpoint": "/api/request-worker/run", "priority": "medium"},
                {"id": "orchestrator", "label": "Ver jobs", "route": "/app/request-orchestrator", "priority": "medium"},
            ],
        }

    def get_package(self) -> Dict[str, Any]:
        return {"ok": True, "mode": "request_worker_loop_package", "package": {"status": self.get_status(), "dashboard": self.build_dashboard()}}


request_worker_loop_service = RequestWorkerLoopService()
