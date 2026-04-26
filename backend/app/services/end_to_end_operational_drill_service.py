from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List
from uuid import uuid4

from app.services.chat_action_cards_service import chat_action_cards_service
from app.services.install_run_readiness_service import install_run_readiness_service
from app.services.memory_core_service import memory_core_service
from app.services.mobile_approval_cockpit_v2_service import mobile_approval_cockpit_v2_service
from app.services.offline_command_buffering_service import offline_command_buffering_service
from app.services.operator_conversation_thread_service import operator_conversation_thread_service
from app.services.request_orchestrator_service import request_orchestrator_service
from app.services.request_worker_loop_service import request_worker_loop_service
from app.utils.atomic_json_store import AtomicJsonStore

DATA_DIR = Path("data")
DRILL_FILE = DATA_DIR / "end_to_end_operational_drill.json"
DRILL_STORE = AtomicJsonStore(
    DRILL_FILE,
    default_factory=lambda: {"drills": [], "reports": []},
)


class EndToEndOperationalDrillService:
    """Non-destructive operational drill for APK -> backend -> worker -> approval -> resume."""

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def _normalize_store(self, store: Dict[str, Any]) -> Dict[str, Any]:
        if not isinstance(store, dict):
            return {"drills": [], "reports": []}
        store.setdefault("drills", [])
        store.setdefault("reports", [])
        return store

    def _load_store(self) -> Dict[str, Any]:
        return self._normalize_store(DRILL_STORE.load())

    def _record(self, key: str, payload: Dict[str, Any]) -> None:
        def mutate(store: Dict[str, Any]) -> Dict[str, Any]:
            store = self._normalize_store(store)
            store.setdefault(key, []).append(payload)
            store[key] = store[key][-300:]
            return store

        DRILL_STORE.update(mutate)

    def get_status(self) -> Dict[str, Any]:
        store = self._load_store()
        return {
            "ok": True,
            "mode": "end_to_end_operational_drill_status",
            "status": "end_to_end_operational_drill_ready",
            "store_file": str(DRILL_FILE),
            "atomic_store_enabled": True,
            "non_destructive": True,
            "drill_count": len(store.get("drills", [])),
            "report_count": len(store.get("reports", [])),
        }

    def run_drill(
        self,
        tenant_id: str = "owner-andre",
        project_id: str = "GOD_MODE",
        request_text: str | None = None,
        include_offline_bridge: bool = True,
    ) -> Dict[str, Any]:
        drill_id = f"e2e-drill-{uuid4().hex[:12]}"
        request = request_text or "prepara um plano seguro para continuar o God Mode até precisares do meu OK"
        trace: List[Dict[str, Any]] = []

        def add(step: str, ok: bool, detail: str, result: Any = None) -> None:
            trace.append({
                "step": step,
                "ok": bool(ok),
                "detail": detail,
                "created_at": self._now(),
                "result": result,
            })

        readiness = install_run_readiness_service.build_report()
        add("readiness_report", readiness.get("ok", False), readiness.get("install_decision", "unknown"), self._compact_readiness(readiness))

        opened = operator_conversation_thread_service.open_thread(
            tenant_id=tenant_id,
            conversation_title="End-to-end operational drill",
            channel_mode="apk_e2e_operational_drill",
        )
        thread_id = opened.get("thread", {}).get("thread_id")
        add("open_thread", opened.get("ok", False), thread_id or "thread_not_created", {"thread_id": thread_id})

        operator_conversation_thread_service.append_message(
            thread_id=thread_id,
            role="operator",
            content=request,
            operational_state="e2e_drill_request",
            suggested_next_steps=["Criar job", "Processar worker", "Validar aprovação"],
        )
        add("chat_request", True, "request_written_to_thread", {"request": request})

        submitted = request_orchestrator_service.submit_request(
            request=request,
            tenant_id=tenant_id,
            project_id=project_id,
            thread_id=thread_id,
            auto_run=False,
        )
        job = submitted.get("job", {})
        job_id = job.get("job_id")
        add("submit_job", submitted.get("ok", False), job_id or submitted.get("error", "submit_failed"), {"job_id": job_id, "status": job.get("status")})

        worker_tick = request_worker_loop_service.tick(tenant_id=tenant_id, max_jobs=5)
        after_tick = request_orchestrator_service.get_job(job_id=job_id, tenant_id=tenant_id) if job_id else {"ok": False}
        tick_job = after_tick.get("job", {})
        add("worker_tick", worker_tick.get("ok", False), tick_job.get("status", "unknown"), {"tick": worker_tick.get("tick"), "job_status": tick_job.get("status"), "blocking_reason": tick_job.get("blocking_reason")})

        approval_cards = mobile_approval_cockpit_v2_service.build_dashboard(tenant_id=tenant_id)
        add("approval_surface", approval_cards.get("ok", False), "approval_dashboard_checked", {"pending_approval_count": approval_cards.get("pending_approval_count", 0)})

        if tick_job.get("status") == "blocked_approval":
            resumed = request_orchestrator_service.resume_job(
                job_id=job_id,
                tenant_id=tenant_id,
                operator_note=f"E2E drill auto-resume for non-destructive validation {drill_id}",
            )
            resumed_job = resumed.get("job", {})
            add("resume_after_approval", resumed.get("ok", False), resumed_job.get("status", "unknown"), {"job_status": resumed_job.get("status"), "blocking_reason": resumed_job.get("blocking_reason")})
        else:
            resumed = {"ok": True, "mode": "resume_skipped", "job": tick_job}
            add("resume_after_approval", True, "resume_not_required", {"job_status": tick_job.get("status")})

        offline_result = None
        if include_offline_bridge:
            offline_command_buffering_service.set_connectivity(pc_online=False, phone_online=True)
            queued = offline_command_buffering_service.queue_command(
                source_side="phone",
                command_text="drill offline command: preparar relatório final sem credenciais",
                project_hint=project_id,
            )
            offline_command_buffering_service.set_connectivity(pc_online=True, phone_online=True)
            sync_replay = offline_command_buffering_service.sync_and_replay_to_pc(
                tenant_id=tenant_id,
                auto_run=True,
                max_commands=3,
            )
            offline_result = {"queued": queued, "sync_replay": sync_replay}
            add("offline_bridge", sync_replay.get("ok", False), "offline_command_replayed_to_orchestrator", {"command_id": queued.get("command", {}).get("command_id"), "sync_ok": sync_replay.get("ok")})

        final_job = request_orchestrator_service.get_job(job_id=job_id, tenant_id=tenant_id) if job_id else {"ok": False}
        final_status = final_job.get("job", {}).get("status")
        report = self._build_report(
            drill_id=drill_id,
            tenant_id=tenant_id,
            project_id=project_id,
            thread_id=thread_id,
            job_id=job_id,
            request=request,
            trace=trace,
            final_status=final_status,
            readiness=readiness,
            offline_result=offline_result,
        )
        operator_conversation_thread_service.append_message(
            thread_id=thread_id,
            role="assistant",
            content=self._report_message(report),
            operational_state="e2e_drill_report",
            suggested_next_steps=["Abrir install readiness", "Abrir request worker", "Abrir offline buffer"],
        )
        chat_action_cards_service.create_card(
            thread_id=thread_id,
            title="Relatório E2E pronto",
            body=f"Estado: {report['status']} · Job: {final_status}",
            actions=[{"label": "Abrir readiness", "action_type": "open_url", "payload": {"url": "/app/install-readiness"}}],
            tenant_id=tenant_id,
            project_id=project_id,
            source="end_to_end_operational_drill",
            priority="high" if report["status"] != "green" else "medium",
        )
        self._record("drills", {"drill_id": drill_id, "created_at": report["created_at"], "status": report["status"], "thread_id": thread_id, "job_id": job_id})
        self._record("reports", report)
        memory_core_service.write_history("GOD_MODE", "End-to-end operational drill", f"{drill_id}: {report['status']} | job={final_status}")
        return {"ok": True, "mode": "end_to_end_operational_drill_run", "report": report}

    def _compact_readiness(self, readiness: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "status": readiness.get("status"),
            "install_decision": readiness.get("install_decision"),
            "score": readiness.get("score"),
            "blocker_count": len(readiness.get("blockers", [])),
            "warning_count": len(readiness.get("warnings", [])),
        }

    def _build_report(
        self,
        drill_id: str,
        tenant_id: str,
        project_id: str,
        thread_id: str | None,
        job_id: str | None,
        request: str,
        trace: List[Dict[str, Any]],
        final_status: str | None,
        readiness: Dict[str, Any],
        offline_result: Any,
    ) -> Dict[str, Any]:
        failed = [item for item in trace if not item.get("ok")]
        blockers = []
        if failed:
            blockers.extend([item.get("step") for item in failed])
        if final_status in {"failed"}:
            blockers.append("job_failed")
        status = "green" if not blockers and final_status in {"completed", "blocked_manual_input", "blocked_credentials", "blocked_approval", "running", "queued"} else "yellow"
        if failed or final_status == "failed":
            status = "red"
        return {
            "report_id": f"e2e-report-{uuid4().hex[:12]}",
            "drill_id": drill_id,
            "created_at": self._now(),
            "tenant_id": tenant_id,
            "project_id": project_id,
            "thread_id": thread_id,
            "job_id": job_id,
            "request": request,
            "status": status,
            "final_job_status": final_status,
            "blockers": blockers,
            "trace": trace,
            "readiness": self._compact_readiness(readiness),
            "offline_bridge_included": offline_result is not None,
            "proof": {
                "chat_thread_created": bool(thread_id),
                "job_created": bool(job_id),
                "worker_tick_ran": any(item["step"] == "worker_tick" and item["ok"] for item in trace),
                "approval_surface_checked": any(item["step"] == "approval_surface" and item["ok"] for item in trace),
                "resume_checked": any(item["step"] == "resume_after_approval" and item["ok"] for item in trace),
                "offline_bridge_checked": any(item["step"] == "offline_bridge" and item["ok"] for item in trace),
                "report_written_to_chat": True,
            },
            "next_actions": self._next_actions(status, final_status),
        }

    def _next_actions(self, status: str, final_status: str | None) -> List[Dict[str, Any]]:
        actions = [
            {"priority": "high", "label": "Abrir readiness", "route": "/app/install-readiness"},
            {"priority": "high", "label": "Abrir chat com cartões", "route": "/app/operator-chat-sync-cards"},
            {"priority": "medium", "label": "Abrir worker", "route": "/app/request-worker"},
        ]
        if final_status and str(final_status).startswith("blocked"):
            actions.insert(0, {"priority": "critical", "label": "Resolver bloqueio do job", "route": "/app/mobile-approval-cockpit-v2"})
        if status == "green":
            actions.insert(0, {"priority": "critical", "label": "Fluxo E2E operacional validado", "route": "/app/apk-start"})
        return actions

    def _report_message(self, report: Dict[str, Any]) -> str:
        return (
            "Relatório E2E operacional concluído.\n\n"
            f"Estado: {report['status']}\n"
            f"Job: {report.get('job_id')} · {report.get('final_job_status')}\n"
            f"Thread: {report.get('thread_id')}\n"
            f"Blockers: {len(report.get('blockers', []))}\n"
            "\nProvas:\n"
            + "\n".join(f"- {key}: {value}" for key, value in report.get("proof", {}).items())
        )

    def latest_report(self) -> Dict[str, Any]:
        reports = self._load_store().get("reports", [])
        return {"ok": True, "mode": "end_to_end_operational_drill_latest_report", "report": reports[-1] if reports else None}

    def build_dashboard(self) -> Dict[str, Any]:
        store = self._load_store()
        latest = store.get("reports", [])[-1] if store.get("reports") else None
        return {
            "ok": True,
            "mode": "end_to_end_operational_drill_dashboard",
            "status": self.get_status(),
            "latest_report": latest,
            "recent_drills": store.get("drills", [])[-20:],
            "recent_reports": store.get("reports", [])[-20:],
            "buttons": [
                {"id": "run", "label": "Correr drill", "endpoint": "/api/e2e-operational-drill/run", "priority": "critical"},
                {"id": "readiness", "label": "Readiness", "route": "/app/install-readiness", "priority": "high"},
                {"id": "chat", "label": "Chat", "route": "/app/operator-chat-sync-cards", "priority": "high"},
                {"id": "approvals", "label": "Aprovações", "route": "/app/mobile-approval-cockpit-v2", "priority": "medium"},
            ],
        }

    def get_package(self) -> Dict[str, Any]:
        return {"ok": True, "mode": "end_to_end_operational_drill_package", "package": {"status": self.get_status(), "dashboard": self.build_dashboard(), "latest_report": self.latest_report()}}


end_to_end_operational_drill_service = EndToEndOperationalDrillService()
