from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict
from uuid import uuid4

from app.services.operator_conversation_thread_service import operator_conversation_thread_service
from app.services.real_work_command_pipeline_service import real_work_command_pipeline_service
from app.utils.atomic_json_store import AtomicJsonStore

DATA_DIR = Path("data")
BRIDGE_FILE = DATA_DIR / "operator_chat_real_work_bridge.json"
BRIDGE_STORE = AtomicJsonStore(
    BRIDGE_FILE,
    default_factory=lambda: {"version": 1, "submissions": [], "reports": []},
)


class OperatorChatRealWorkBridgeService:
    """Bridge normal operator chat messages into the real work command pipeline."""

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def _normalize(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        payload.setdefault("version", 1)
        payload.setdefault("submissions", [])
        payload.setdefault("reports", [])
        return payload

    def _record(self, key: str, item: Dict[str, Any]) -> None:
        def mutate(payload: Dict[str, Any]) -> Dict[str, Any]:
            payload = self._normalize(payload)
            payload[key].append(item)
            payload[key] = payload[key][-300:]
            return payload

        BRIDGE_STORE.update(mutate)

    def get_status(self) -> Dict[str, Any]:
        state = self._normalize(BRIDGE_STORE.load())
        return {
            "ok": True,
            "mode": "operator_chat_real_work_bridge_status",
            "status": "chat_to_real_work_ready",
            "primary_chat_route": "/app/operator-chat-sync-cards",
            "real_work_endpoint": "/api/real-work/submit",
            "submission_count": len(state["submissions"]),
            "report_count": len(state["reports"]),
            "money_priority_enabled": False,
        }

    def submit_chat_command(
        self,
        message: str,
        tenant_id: str = "owner-andre",
        thread_id: str | None = None,
        requested_project: str | None = None,
        auto_run: bool = True,
    ) -> Dict[str, Any]:
        clean_message = (message or "").strip()
        if not clean_message:
            raise ValueError("empty_chat_message")
        bridge_id = f"chat-work-{uuid4().hex[:12]}"
        opened_thread = None
        if not thread_id:
            opened_thread = operator_conversation_thread_service.open_thread(
                tenant_id=tenant_id,
                conversation_title="God Mode real work chat",
                channel_mode="operator_chat_real_work",
            )
            thread_id = opened_thread.get("thread", {}).get("thread_id")
        operator_conversation_thread_service.append_message(
            thread_id=thread_id,
            role="user",
            content=clean_message,
            operational_state="real_work_requested",
            suggested_next_steps=["Resolver projeto", "Criar job", "Trabalhar até bloquear"],
        )
        pipeline = real_work_command_pipeline_service.submit_command(
            command_text=clean_message,
            tenant_id=tenant_id,
            requested_project=requested_project,
            auto_run=auto_run,
        )
        report = self._build_chat_report(bridge_id, tenant_id, thread_id, clean_message, requested_project, pipeline)
        operator_conversation_thread_service.append_message(
            thread_id=thread_id,
            role="assistant",
            content=self._assistant_message(report),
            operational_state="real_work_submitted",
            suggested_next_steps=["Ver aprovações", "Ver worker", "Continuar conversa"],
        )
        self._record("submissions", {
            "bridge_id": bridge_id,
            "created_at": report["created_at"],
            "tenant_id": tenant_id,
            "thread_id": thread_id,
            "requested_project": requested_project,
            "message": clean_message,
        })
        self._record("reports", report)
        return {
            "ok": True,
            "mode": "operator_chat_real_work_submit",
            "bridge_id": bridge_id,
            "thread_id": thread_id,
            "opened_thread": opened_thread,
            "pipeline": pipeline,
            "report": report,
        }

    def _build_chat_report(
        self,
        bridge_id: str,
        tenant_id: str,
        thread_id: str | None,
        message: str,
        requested_project: str | None,
        pipeline: Dict[str, Any],
    ) -> Dict[str, Any]:
        package = pipeline.get("package", {})
        work_report = pipeline.get("report", {})
        project = package.get("project", {})
        return {
            "report_id": f"chat-work-report-{uuid4().hex[:12]}",
            "bridge_id": bridge_id,
            "created_at": self._now(),
            "tenant_id": tenant_id,
            "thread_id": thread_id,
            "message": message,
            "requested_project": requested_project,
            "resolved_project_id": project.get("project_id"),
            "intent": package.get("intent"),
            "job_id": work_report.get("job_id"),
            "job_status": work_report.get("job_status"),
            "worker_tick_ran": work_report.get("worker_tick_ran"),
            "operator_priority_obeyed": work_report.get("operator_priority_obeyed") is True,
            "money_priority_enabled": False,
            "next_actions": [
                {"label": "Abrir aprovações", "route": "/app/mobile-approval-cockpit-v2"},
                {"label": "Ver worker", "route": "/app/request-worker"},
                {"label": "Ver prioridades", "route": "/app/operator-priority"},
            ],
        }

    def _assistant_message(self, report: Dict[str, Any]) -> str:
        return (
            "Recebido. Transformei a tua mensagem em trabalho real do backend.\n\n"
            f"Projeto: {report.get('resolved_project_id')}\n"
            f"Intent: {report.get('intent')}\n"
            f"Job: {report.get('job_id')} · {report.get('job_status')}\n"
            f"Worker tick: {'sim' if report.get('worker_tick_ran') else 'não'}\n"
            "Prioridade: ordem do operador. Dinheiro não foi usado como critério.\n\n"
            "Se bloquear, vai aparecer nas aprovações/input."
        )

    def latest(self) -> Dict[str, Any]:
        state = self._normalize(BRIDGE_STORE.load())
        return {
            "ok": True,
            "mode": "operator_chat_real_work_latest",
            "submission": state["submissions"][-1] if state["submissions"] else None,
            "report": state["reports"][-1] if state["reports"] else None,
        }

    def get_package(self) -> Dict[str, Any]:
        return {"ok": True, "mode": "operator_chat_real_work_bridge_package", "package": {"status": self.get_status(), "latest": self.latest()}}


operator_chat_real_work_bridge_service = OperatorChatRealWorkBridgeService()
