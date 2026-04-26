from __future__ import annotations

import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List
from uuid import uuid4

from app.services.chat_action_cards_service import chat_action_cards_service
from app.services.memory_core_service import DEFAULT_BLOCKED_KEYWORDS, memory_core_service
from app.services.mobile_approval_cockpit_v2_service import mobile_approval_cockpit_v2_service
from app.services.money_command_center_service import money_command_center_service
from app.services.operator_conversation_thread_service import operator_conversation_thread_service
from app.utils.atomic_json_store import AtomicJsonStore

DATA_DIR = Path("data")
REQUEST_ORCHESTRATOR_FILE = DATA_DIR / "request_orchestrator.json"
REQUEST_ORCHESTRATOR_STORE = AtomicJsonStore(
    REQUEST_ORCHESTRATOR_FILE,
    default_factory=lambda: {"jobs": [], "events": [], "credential_requests": []},
)

SECRET_WORDS = [item.lower() for item in DEFAULT_BLOCKED_KEYWORDS]
PROVIDER_WORDS = {"chatgpt", "openai", "gemini", "claude", "grok", "deepseek", "provider", "login", "entrar"}
MONEY_WORDS = {"dinheiro", "receita", "vender", "monetizar", "cliente", "proposta", "orçamento", "orcamento"}
BUILD_WORDS = {"build", "apk", "exe", "release", "artifact", "artefacto", "publicar", "deploy"}
APPROVAL_WORDS = {"aprov", "ok", "confirm", "aceitar", "executar", "fazer"}


class RequestOrchestratorService:
    """Durable backend request engine: run until blocked by approval or manual input."""

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def _normalize_store(self, store: Dict[str, Any]) -> Dict[str, Any]:
        if not isinstance(store, dict):
            return {"jobs": [], "events": [], "credential_requests": []}
        store.setdefault("jobs", [])
        store.setdefault("events", [])
        store.setdefault("credential_requests", [])
        return store

    def _load_store(self) -> Dict[str, Any]:
        return self._normalize_store(REQUEST_ORCHESTRATOR_STORE.load())

    def get_status(self) -> Dict[str, Any]:
        store = self._load_store()
        active = [job for job in store.get("jobs", []) if job.get("status") in {"queued", "running"}]
        blocked = [job for job in store.get("jobs", []) if str(job.get("status", "")).startswith("blocked")]
        return {
            "ok": True,
            "mode": "request_orchestrator_status",
            "status": "request_orchestrator_ready",
            "store_file": str(REQUEST_ORCHESTRATOR_FILE),
            "atomic_store_enabled": True,
            "durable_jobs": True,
            "apk_disconnect_safe": True,
            "run_until_blocked": True,
            "active_count": len(active),
            "blocked_count": len(blocked),
            "job_count": len(store.get("jobs", [])),
            "credential_request_count": len(store.get("credential_requests", [])),
        }

    def _contains_secret_keyword(self, text: str) -> bool:
        lowered = text.lower()
        return any(re.search(rf"(?<![a-z0-9_]){re.escape(word)}(?![a-z0-9_])", lowered) for word in SECRET_WORDS)

    def _sanitize_request(self, text: str) -> Dict[str, Any]:
        clean = (text or "").strip()
        if not clean:
            return {"ok": False, "error": "empty_request", "safe_text": ""}
        if self._contains_secret_keyword(clean):
            return {
                "ok": False,
                "error": "secret_like_text_blocked",
                "safe_text": "[pedido bloqueado: parece conter valor sensível. Não coloques passwords, tokens, cookies ou keys no chat.]",
            }
        return {"ok": True, "safe_text": clean[:5000]}

    def _intent(self, text: str) -> str:
        lowered = text.lower()
        if any(word in lowered for word in PROVIDER_WORDS):
            return "provider_handoff"
        if any(word in lowered for word in MONEY_WORDS):
            return "money_flow"
        if any(word in lowered for word in BUILD_WORDS):
            return "build_or_publish"
        if any(word in lowered for word in APPROVAL_WORDS):
            return "controlled_execution"
        return "general_backend_request"

    def _plan_steps(self, intent: str, request: str) -> List[Dict[str, Any]]:
        base = [
            self._step("interpret", "Interpretar pedido", "auto", f"Intent: {intent}"),
            self._step("persist_context", "Guardar contexto operacional", "auto", "Registar pedido em memória e thread."),
        ]
        if intent == "provider_handoff":
            return base + [
                self._step("prepare_provider", "Preparar provider/chat externo", "auto", "Criar instruções sem credenciais guardadas."),
                self._step("wait_credentials", "Aguardar login/credenciais manuais", "needs_credentials", "O operador deve introduzir login diretamente no provider. O backend não guarda segredos."),
                self._step("continue_after_login", "Continuar depois do login", "manual_resume", "Retomar quando o operador confirmar que o provider está pronto."),
            ]
        if intent == "money_flow":
            return base + [
                self._step("money_top_project", "Escolher projeto com maior chance de dinheiro", "auto", "Usar Money Command Center."),
                self._step("money_approval", "Pedir aprovação do sprint de receita", "needs_approval", "Criar cartão de aprovação para avançar."),
                self._step("execute_money_sprint", "Executar sprint aprovado", "manual_resume", "Continuar quando aprovado."),
            ]
        if intent == "build_or_publish":
            return base + [
                self._step("prepare_build_plan", "Preparar plano de build/publicação", "auto", "Identificar rota APK/EXE/deploy."),
                self._step("build_approval", "Aguardar OK para build/publicação", "needs_approval", "Ações de build/deploy exigem aprovação."),
                self._step("execute_build", "Executar build/publicação aprovada", "manual_resume", "Continuar quando aprovado."),
            ]
        return base + [
            self._step("safe_plan", "Preparar plano seguro", "auto", "Transformar pedido em próximos passos de backend."),
            self._step("operator_approval", "Aguardar OK do operador", "needs_approval", "Confirmar antes de alterações reais."),
            self._step("execute_after_ok", "Executar depois do OK", "manual_resume", "Continuar quando aprovado."),
        ]

    def _step(self, step_id: str, title: str, step_type: str, detail: str) -> Dict[str, Any]:
        return {
            "step_id": step_id,
            "title": title,
            "step_type": step_type,
            "detail": detail,
            "status": "pending",
            "created_at": self._now(),
            "updated_at": self._now(),
            "result": None,
        }

    def _step_snapshot(self, step: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "step_id": step.get("step_id"),
            "title": step.get("title"),
            "step_type": step.get("step_type"),
            "detail": step.get("detail"),
            "status_at_block": step.get("status"),
        }

    def _open_or_get_thread(self, tenant_id: str, thread_id: str | None) -> str:
        if thread_id:
            existing = operator_conversation_thread_service.get_thread(thread_id)
            if existing.get("ok"):
                return thread_id
        opened = operator_conversation_thread_service.open_thread(
            tenant_id=tenant_id,
            conversation_title="God Mode request orchestration",
            channel_mode="apk_request_orchestrator_chat",
        )
        return opened["thread"]["thread_id"]

    def submit_request(
        self,
        request: str,
        tenant_id: str = "owner-andre",
        project_id: str = "GOD_MODE",
        thread_id: str | None = None,
        auto_run: bool = True,
    ) -> Dict[str, Any]:
        safe = self._sanitize_request(request)
        if not safe.get("ok"):
            return safe
        actual_thread_id = self._open_or_get_thread(tenant_id, thread_id)
        safe_text = safe["safe_text"]
        intent = self._intent(safe_text)
        job = {
            "job_id": f"request-job-{uuid4().hex[:12]}",
            "tenant_id": tenant_id,
            "project_id": project_id,
            "thread_id": actual_thread_id,
            "request": safe_text,
            "intent": intent,
            "status": "queued",
            "blocking_reason": None,
            "created_at": self._now(),
            "updated_at": self._now(),
            "steps": self._plan_steps(intent, safe_text),
            "events": [],
        }
        operator_conversation_thread_service.append_message(
            thread_id=actual_thread_id,
            role="operator",
            content=safe_text,
            operational_state="request_submitted",
            suggested_next_steps=["Aguardar backend", "Ver estado do pedido"],
        )

        def mutate(store: Dict[str, Any]) -> Dict[str, Any]:
            store = self._normalize_store(store)
            store["jobs"].append(job)
            store["jobs"] = store["jobs"][-1000:]
            store["events"].append(self._event(job["job_id"], "submitted", f"Pedido submetido: {intent}"))
            store["events"] = store["events"][-2000:]
            return store

        REQUEST_ORCHESTRATOR_STORE.update(mutate)
        if auto_run:
            return self.run_until_blocked(job["job_id"], tenant_id=tenant_id)
        return {"ok": True, "mode": "request_orchestrator_submit", "job": job}

    def _event(self, job_id: str, event_type: str, message: str) -> Dict[str, Any]:
        return {"event_id": f"request-event-{uuid4().hex[:12]}", "job_id": job_id, "event_type": event_type, "message": message, "created_at": self._now()}

    def _find_job(self, store: Dict[str, Any], job_id: str, tenant_id: str) -> Dict[str, Any] | None:
        return next((job for job in store.get("jobs", []) if job.get("job_id") == job_id and job.get("tenant_id") == tenant_id), None)

    def run_until_blocked(self, job_id: str, tenant_id: str = "owner-andre", max_steps: int = 20) -> Dict[str, Any]:
        processed = 0
        final_job: Dict[str, Any] | None = None
        while processed < max_steps:
            store = self._load_store()
            job = self._find_job(store, job_id, tenant_id)
            if not job:
                return {"ok": False, "error": "job_not_found", "job_id": job_id}
            pending = next((step for step in job.get("steps", []) if step.get("status") == "pending"), None)
            if not pending:
                job["status"] = "completed"
                job["blocking_reason"] = None
                job["updated_at"] = self._now()
                self._persist_job(job, event=self._event(job_id, "completed", "Pedido concluído."))
                final_job = job
                break
            if pending["step_type"] == "auto":
                result = self._execute_auto_step(job, pending)
                pending["status"] = "done" if result.get("ok") else "failed"
                pending["result"] = result
                pending["updated_at"] = self._now()
                job["status"] = "running" if result.get("ok") else "failed"
                job["updated_at"] = self._now()
                self._persist_job(job, event=self._event(job_id, "step_done" if result.get("ok") else "step_failed", pending["title"]))
                processed += 1
                if not result.get("ok"):
                    final_job = job
                    break
                continue
            if pending["step_type"] == "needs_approval":
                result = self._block_for_approval(job, pending)
                pending["status"] = "blocked"
                pending["result"] = result
                pending["updated_at"] = self._now()
                job["status"] = "blocked_approval"
                job["blocking_reason"] = pending["title"]
                job["updated_at"] = self._now()
                self._persist_job(job, event=self._event(job_id, "blocked_approval", pending["title"]))
                final_job = job
                break
            if pending["step_type"] == "needs_credentials":
                result = self._block_for_credentials(job, pending)
                pending["status"] = "blocked"
                pending["result"] = result
                pending["updated_at"] = self._now()
                job["status"] = "blocked_credentials"
                job["blocking_reason"] = pending["title"]
                job["updated_at"] = self._now()
                self._persist_job(job, event=self._event(job_id, "blocked_credentials", pending["title"]))
                final_job = job
                break
            job["status"] = "blocked_manual_input"
            job["blocking_reason"] = pending["title"]
            job["updated_at"] = self._now()
            self._persist_job(job, event=self._event(job_id, "blocked_manual_input", pending["title"]))
            final_job = job
            break
        return {"ok": True, "mode": "request_orchestrator_run_until_blocked", "processed_steps": processed, "job": final_job}

    def _persist_job(self, job: Dict[str, Any], event: Dict[str, Any] | None = None) -> None:
        def mutate(store: Dict[str, Any]) -> Dict[str, Any]:
            store = self._normalize_store(store)
            for index, item in enumerate(store.get("jobs", [])):
                if item.get("job_id") == job.get("job_id") and item.get("tenant_id") == job.get("tenant_id"):
                    store["jobs"][index] = job
                    break
            if event:
                store["events"].append(event)
                store["events"] = store["events"][-2000:]
            return store

        REQUEST_ORCHESTRATOR_STORE.update(mutate)

    def _execute_auto_step(self, job: Dict[str, Any], step: Dict[str, Any]) -> Dict[str, Any]:
        memory_core_service.initialize()
        if step["step_id"] == "persist_context":
            memory_core_service.write_history("GOD_MODE", "Request orchestrator received request", f"{job['intent']}: {job['request']}")
            return {"ok": True, "mode": "persist_context"}
        if step["step_id"] == "money_top_project":
            return money_command_center_service.top_project()
        if step["step_id"] == "prepare_provider":
            return self._append(job, "Preparei o handoff do provider. Vou parar antes de qualquer login. Faz login manual quando o cartão pedir.", ["Abrir provider", "Confirmar quando pronto"])
        if step["step_id"] in {"prepare_build_plan", "safe_plan"}:
            return self._append(job, f"Plano preparado para: {job['request']}. Vou pedir OK antes de alterar algo.", ["Aprovar", "Pedir ajustes"])
        return self._append(job, f"Passo automático concluído: {step['title']}", ["Continuar"])

    def _append(self, job: Dict[str, Any], content: str, suggested: List[str]) -> Dict[str, Any]:
        return operator_conversation_thread_service.append_message(
            thread_id=job["thread_id"],
            role="assistant",
            content=content,
            operational_state="request_orchestrator",
            suggested_next_steps=suggested,
        )

    def _block_for_approval(self, job: Dict[str, Any], step: Dict[str, Any]) -> Dict[str, Any]:
        step_snapshot = self._step_snapshot(step)
        card = mobile_approval_cockpit_v2_service.create_card(
            title=f"OK necessário: {step['title']}",
            body=f"Pedido: {job['request']}\n\nO backend executou tudo o que era seguro e parou aqui para aprovação explícita.",
            card_type="operator_command",
            project_id=job.get("project_id", "GOD_MODE"),
            tenant_id=job.get("tenant_id", "owner-andre"),
            priority="high",
            requires_approval=True,
            actions=[
                {"action_id": "approve-request-job", "label": "Aprovar e continuar", "decision": "approved"},
                {"action_id": "reject-request-job", "label": "Parar", "decision": "rejected"},
                {"action_id": "revise-request-job", "label": "Pedir ajustes", "decision": "needs_changes"},
            ],
            source_ref={"type": "request_orchestrator", "job_id": job["job_id"], "step_id": step["step_id"]},
            metadata={"job_id": job["job_id"], "step_snapshot": step_snapshot},
        )
        chat_card = chat_action_cards_service.create_card(
            thread_id=job["thread_id"],
            title="OK necessário para continuar",
            body="O backend chegou a um passo que precisa da tua aprovação no Mobile Approval Cockpit.",
            actions=[{"label": "Abrir aprovações", "action_type": "open_url", "payload": {"url": "/app/mobile-approval-cockpit-v2"}}],
            tenant_id=job.get("tenant_id", "owner-andre"),
            project_id=job.get("project_id", "GOD_MODE"),
            source="request_orchestrator",
            priority="high",
        )
        self._append(job, "Parei para pedir o teu OK. O backend fica com este job guardado e pode continuar depois da aprovação.", ["Abrir aprovações", "Ver job"])
        return {"ok": True, "mode": "blocked_for_approval", "approval_card": card, "chat_card": chat_card}

    def _block_for_credentials(self, job: Dict[str, Any], step: Dict[str, Any]) -> Dict[str, Any]:
        credential_request = {
            "credential_request_id": f"credential-request-{uuid4().hex[:12]}",
            "job_id": job["job_id"],
            "tenant_id": job.get("tenant_id", "owner-andre"),
            "thread_id": job["thread_id"],
            "status": "waiting_manual_login",
            "created_at": self._now(),
            "provider_hint": self._provider_hint(job["request"]),
            "store_credentials": False,
            "instruction": "Faz login manual no provider. Não escrevas password/token no chat. Depois confirma que o login está pronto.",
        }

        def mutate(store: Dict[str, Any]) -> Dict[str, Any]:
            store = self._normalize_store(store)
            store["credential_requests"].append(credential_request)
            store["credential_requests"] = store["credential_requests"][-300:]
            return store

        REQUEST_ORCHESTRATOR_STORE.update(mutate)
        card = mobile_approval_cockpit_v2_service.create_card(
            title="Login manual necessário",
            body=credential_request["instruction"],
            card_type="provider_login_request",
            project_id=job.get("project_id", "GOD_MODE"),
            tenant_id=job.get("tenant_id", "owner-andre"),
            priority="critical",
            requires_approval=True,
            actions=[
                {"action_id": "provider-ready", "label": "Login feito, continuar", "decision": "approved"},
                {"action_id": "provider-cancel", "label": "Cancelar", "decision": "rejected"},
            ],
            source_ref={"type": "request_orchestrator_credentials", "job_id": job["job_id"]},
            metadata=credential_request,
        )
        chat_card = chat_action_cards_service.create_card(
            thread_id=job["thread_id"],
            title="Login manual necessário",
            body="O backend parou porque precisa que faças login manual no provider. Não escrevas credenciais no chat.",
            actions=[{"label": "Abrir aprovações", "action_type": "open_url", "payload": {"url": "/app/mobile-approval-cockpit-v2"}}],
            tenant_id=job.get("tenant_id", "owner-andre"),
            project_id=job.get("project_id", "GOD_MODE"),
            source="request_orchestrator_credentials",
            priority="critical",
        )
        self._append(job, "Parei para login manual. O backend fica à espera e não guarda credenciais.", ["Fazer login manual", "Confirmar quando pronto"])
        return {"ok": True, "mode": "blocked_for_credentials", "credential_request": credential_request, "approval_card": card, "chat_card": chat_card}

    def _provider_hint(self, request: str) -> str:
        lowered = request.lower()
        for provider in ["chatgpt", "gemini", "claude", "grok", "deepseek", "openai"]:
            if provider in lowered:
                return provider
        return "external_provider"

    def resume_job(self, job_id: str, tenant_id: str = "owner-andre", operator_note: str = "") -> Dict[str, Any]:
        store = self._load_store()
        job = self._find_job(store, job_id, tenant_id)
        if not job:
            return {"ok": False, "error": "job_not_found", "job_id": job_id}
        blocked = next((step for step in job.get("steps", []) if step.get("status") == "blocked"), None)
        if blocked:
            blocked["status"] = "done"
            blocked["updated_at"] = self._now()
            blocked["result"] = {"ok": True, "mode": "operator_resumed", "operator_note": operator_note}
        job["status"] = "queued"
        job["blocking_reason"] = None
        job["updated_at"] = self._now()
        self._persist_job(job, event=self._event(job_id, "resumed", operator_note or "Operador retomou job."))
        self._append(job, "Recebi confirmação. Vou continuar até ao próximo bloqueio ou conclusão.", ["Aguardar backend"])
        return self.run_until_blocked(job_id=job_id, tenant_id=tenant_id)

    def list_jobs(self, tenant_id: str = "owner-andre", status: str | None = None, limit: int = 100) -> Dict[str, Any]:
        jobs = [job for job in self._load_store().get("jobs", []) if job.get("tenant_id") == tenant_id]
        if status:
            jobs = [job for job in jobs if job.get("status") == status]
        return {"ok": True, "mode": "request_orchestrator_jobs", "job_count": len(jobs[-limit:]), "jobs": jobs[-limit:]}

    def get_job(self, job_id: str, tenant_id: str = "owner-andre") -> Dict[str, Any]:
        job = self._find_job(self._load_store(), job_id, tenant_id)
        return {"ok": bool(job), "mode": "request_orchestrator_job", "job": job, "error": None if job else "job_not_found"}

    def build_dashboard(self, tenant_id: str = "owner-andre") -> Dict[str, Any]:
        store = self._load_store()
        jobs = [job for job in store.get("jobs", []) if job.get("tenant_id") == tenant_id]
        blocked = [job for job in jobs if str(job.get("status", "")).startswith("blocked")]
        running = [job for job in jobs if job.get("status") in {"queued", "running"}]
        return {
            "ok": True,
            "mode": "request_orchestrator_dashboard",
            "tenant_id": tenant_id,
            "status": self.get_status(),
            "summary": {"jobs": len(jobs), "running": len(running), "blocked": len(blocked), "completed": len([j for j in jobs if j.get("status") == "completed"])},
            "recent_jobs": jobs[-50:],
            "blocked_jobs": blocked[-50:],
            "recent_events": store.get("events", [])[-80:],
            "credential_requests": store.get("credential_requests", [])[-30:],
        }

    def get_package(self) -> Dict[str, Any]:
        return {"ok": True, "mode": "request_orchestrator_package", "package": {"status": self.get_status(), "dashboard": self.build_dashboard()}}


request_orchestrator_service = RequestOrchestratorService()
