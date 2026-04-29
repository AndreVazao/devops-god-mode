from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional
from uuid import uuid4

from app.utils.atomic_json_store import AtomicJsonStore

DATA_DIR = Path("data")
HUB_FILE = DATA_DIR / "browser_provider_execution_hub.json"
HUB_STORE = AtomicJsonStore(
    HUB_FILE,
    default_factory=lambda: {
        "version": 1,
        "policy": "orchestrate_existing_browser_provider_modules_without_duplication",
        "plans": [],
        "sessions": [],
        "handoffs": [],
    },
)


class BrowserProviderExecutionHubService:
    """Orchestrates existing browser/provider modules into one execution hub.

    This service intentionally does not duplicate the lower-level browser workers.
    It composes the existing modules already present in the repository:
    - external_ai_browser_worker
    - external_ai_chat_reader
    - external_ai_session_plan
    - browser_control_real
    - browser_conversation_intake
    - browser_continuation_execution
    - browser_response_reconciliation
    - provider_real_execution_guard
    - provider_session_partition
    - operator_popup_delivery
    - operator_resumable_action
    """

    PROVIDERS = [
        {"id": "chatgpt", "label": "ChatGPT", "rank": 1, "role": "primary"},
        {"id": "deepseek", "label": "DeepSeek", "rank": 2, "role": "code_fallback"},
        {"id": "claude", "label": "Claude", "rank": 3, "role": "large_context_review"},
        {"id": "gemini", "label": "Gemini", "rank": 4, "role": "multimodal_research"},
        {"id": "google_web", "label": "Google/Web", "rank": 5, "role": "public_research"},
        {"id": "local_ai", "label": "Local AI", "rank": 6, "role": "offline_draft"},
    ]

    STOP_REASONS = [
        "needs_operator_login",
        "needs_operator_ok",
        "provider_rate_limited",
        "provider_refused_or_blocked",
        "unsafe_or_sensitive_request",
        "browser_session_lost",
        "network_offline",
        "work_completed",
    ]

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def _safe_status(self, label: str, import_path: str, attr: str = "get_status") -> Dict[str, Any]:
        try:
            module_name, service_name = import_path.rsplit(".", 1)
            service = getattr(__import__(module_name, fromlist=[service_name]), service_name)
            fn: Callable[[], Dict[str, Any]] = getattr(service, attr)
            value = fn()
            return value if isinstance(value, dict) else {"ok": True, "value": value}
        except Exception as exc:
            return {"ok": False, "mode": label, "error": exc.__class__.__name__, "detail": str(exc)[:300]}

    def module_matrix(self) -> Dict[str, Any]:
        modules = [
            {"id": "external_ai_browser_worker", "service": "app.services.external_ai_browser_worker_service.external_ai_browser_worker_service"},
            {"id": "external_ai_chat_reader", "service": "app.services.external_ai_chat_reader_service.external_ai_chat_reader_service"},
            {"id": "external_ai_session_plan", "service": "app.services.external_ai_session_plan_service.external_ai_session_plan_service"},
            {"id": "browser_control_real", "service": "app.services.browser_control_real_service.browser_control_real_service"},
            {"id": "browser_conversation_intake", "service": "app.services.browser_conversation_intake_service.browser_conversation_intake_service"},
            {"id": "browser_continuation_execution", "service": "app.services.browser_continuation_execution_service.browser_continuation_execution_service"},
            {"id": "browser_response_reconciliation", "service": "app.services.browser_response_reconciliation_service.browser_response_reconciliation_service"},
            {"id": "provider_real_execution_guard", "service": "app.services.provider_real_execution_guard_service.provider_real_execution_guard_service"},
            {"id": "provider_session_partition", "service": "app.services.provider_session_partition_service.provider_session_partition_service"},
            {"id": "operator_popup_delivery", "service": "app.services.operator_popup_delivery_service.operator_popup_delivery_service"},
            {"id": "operator_resumable_action", "service": "app.services.operator_resumable_action_service.operator_resumable_action_service"},
        ]
        matrix = []
        for item in modules:
            status = self._safe_status(item["id"], item["service"])
            matrix.append({**item, "status": status, "available": bool(status.get("ok", False))})
        return {
            "ok": True,
            "mode": "browser_provider_module_matrix",
            "available_count": len([m for m in matrix if m["available"]]),
            "missing_or_error_count": len([m for m in matrix if not m["available"]]),
            "modules": matrix,
        }

    def policy(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "mode": "browser_provider_execution_policy",
            "rule": "orquestrar módulos existentes; não duplicar workers browser/provider",
            "can_continue_without_apk": True,
            "stops_only_for": self.STOP_REASONS,
            "login_policy": {
                "operator_logs_in_manually": True,
                "reuse_browser_session_after_login": True,
                "do_not_store_passwords_tokens_cookies": True,
                "credentials_go_to_browser_or_os_secure_store": True,
            },
            "research_policy": {
                "google_web_allowed": True,
                "provider_chats_allowed": True,
                "store_summaries_not_secret_material": True,
                "save_project_notes_to_memory": True,
            },
            "fallback_policy": {
                "primary_provider": "chatgpt",
                "code_fallback": "deepseek",
                "switch_provider_on_refusal_or_limit": True,
                "record_provider_score": True,
            },
        }

    def plan(
        self,
        project_id: str = "GOD_MODE",
        objective: str = "continue project with provider/browser execution",
        provider_preference: Optional[List[str]] = None,
        allow_google_web: bool = True,
        allow_provider_fallback: bool = True,
    ) -> Dict[str, Any]:
        providers = self._provider_sequence(provider_preference, allow_google_web, allow_provider_fallback)
        matrix = self.module_matrix()
        plan = {
            "plan_id": f"browser-provider-plan-{uuid4().hex[:12]}",
            "created_at": self._now(),
            "project_id": self._normalize_project(project_id),
            "objective": objective,
            "provider_sequence": providers,
            "module_matrix": matrix,
            "flow": self._flow(providers),
            "operator_stops": [
                {"reason": "needs_operator_login", "popup": True, "resume_after": "browser_session_ready"},
                {"reason": "needs_operator_ok", "popup": True, "resume_after": "approval_received"},
                {"reason": "provider_refused_or_blocked", "resume_after": "fallback_provider_selected"},
                {"reason": "network_offline", "resume_after": "network_back_or_checkpoint_retry"},
            ],
            "checkpoint_policy": {
                "write_session_after_each_step": True,
                "resume_from_last_safe_step": True,
                "rollback_to_previous_prompt_on_bad_response": True,
            },
            "status": "planned",
        }
        self._store("plans", plan)
        return {"ok": True, "mode": "browser_provider_execution_plan", "plan": plan}

    def _provider_sequence(self, preference: Optional[List[str]], allow_google: bool, allow_fallback: bool) -> List[Dict[str, Any]]:
        preferred = [p.strip().lower() for p in (preference or []) if p.strip()]
        ordered = []
        seen = set()
        for provider_id in preferred:
            provider = next((p for p in self.PROVIDERS if p["id"] == provider_id), None)
            if provider and provider_id not in seen:
                ordered.append(provider)
                seen.add(provider_id)
        for provider in self.PROVIDERS:
            if provider["id"] == "google_web" and not allow_google:
                continue
            if provider["rank"] > 1 and not allow_fallback and provider["id"] not in seen:
                continue
            if provider["id"] not in seen:
                ordered.append(provider)
                seen.add(provider["id"])
        return ordered

    def _flow(self, providers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        return [
            {"step": 1, "label": "validar guard provider", "module": "provider_real_execution_guard"},
            {"step": 2, "label": "abrir/reutilizar sessão browser", "module": "external_ai_browser_worker"},
            {"step": 3, "label": "se precisar login, pedir popup ao operador", "module": "operator_popup_delivery"},
            {"step": 4, "label": "ler/scrollar conversa quando aplicável", "module": "external_ai_chat_reader"},
            {"step": 5, "label": "injetar prompt/objetivo no provider", "module": "browser_control_real"},
            {"step": 6, "label": "capturar resposta e reconciliar", "module": "browser_response_reconciliation"},
            {"step": 7, "label": "se falhar/recusar/limitar, tentar próximo provider", "providers": [p["id"] for p in providers]},
            {"step": 8, "label": "guardar resumo/checkpoint e próxima ação", "module": "operator_resumable_action"},
        ]

    def start_session(
        self,
        project_id: str = "GOD_MODE",
        objective: str = "continue provider/browser work",
        provider_preference: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        plan = self.plan(project_id=project_id, objective=objective, provider_preference=provider_preference).get("plan", {})
        session = {
            "session_id": f"browser-provider-session-{uuid4().hex[:12]}",
            "created_at": self._now(),
            "plan_id": plan.get("plan_id"),
            "project_id": plan.get("project_id"),
            "objective": objective,
            "status": "waiting_for_runtime_executor",
            "current_step": plan.get("flow", [])[0] if plan.get("flow") else None,
            "provider_sequence": plan.get("provider_sequence", []),
            "checkpoints": [
                {"created_at": self._now(), "event": "session_planned", "safe_to_resume": True}
            ],
            "next": {
                "label": "executar com worker/browser real existente",
                "modules": ["external_ai_browser_worker", "browser_control_real", "external_ai_chat_reader"],
            },
        }
        self._store("sessions", session)
        return {"ok": True, "mode": "browser_provider_execution_session", "session": session}

    def record_handoff(
        self,
        session_id: str,
        provider_id: str,
        result: str,
        stop_reason: str = "work_completed",
        next_provider_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        handoff = {
            "handoff_id": f"browser-provider-handoff-{uuid4().hex[:12]}",
            "created_at": self._now(),
            "session_id": session_id,
            "provider_id": provider_id,
            "result": result[:5000],
            "stop_reason": stop_reason if stop_reason in self.STOP_REASONS else "needs_operator_ok",
            "next_provider_id": next_provider_id,
            "safe_to_resume": stop_reason not in {"unsafe_or_sensitive_request"},
        }
        self._store("handoffs", handoff)
        return {"ok": True, "mode": "browser_provider_execution_handoff", "handoff": handoff}

    def _normalize_project(self, project_id: str) -> str:
        return (project_id or "GOD_MODE").strip().upper().replace("-", "_").replace(" ", "_")

    def _store(self, key: str, item: Dict[str, Any]) -> None:
        def mutate(state: Dict[str, Any]) -> Dict[str, Any]:
            state.setdefault(key, [])
            state[key].append(item)
            state[key] = state[key][-100:]
            return state
        HUB_STORE.update(mutate)

    def latest(self) -> Dict[str, Any]:
        state = HUB_STORE.load()
        return {
            "ok": True,
            "mode": "browser_provider_execution_latest",
            "latest_plan": (state.get("plans") or [None])[-1],
            "latest_session": (state.get("sessions") or [None])[-1],
            "latest_handoff": (state.get("handoffs") or [None])[-1],
            "plan_count": len(state.get("plans") or []),
            "session_count": len(state.get("sessions") or []),
            "handoff_count": len(state.get("handoffs") or []),
        }

    def panel(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "mode": "browser_provider_execution_panel",
            "headline": "Execução real browser/providers",
            "policy": self.policy(),
            "module_matrix": self.module_matrix(),
            "latest": self.latest(),
            "safe_buttons": [
                {"id": "plan", "label": "Plano browser/providers", "endpoint": "/api/browser-provider-execution/plan", "priority": "critical"},
                {"id": "session", "label": "Criar sessão", "endpoint": "/api/browser-provider-execution/session", "priority": "critical"},
                {"id": "matrix", "label": "Ver módulos", "endpoint": "/api/browser-provider-execution/modules", "priority": "high"},
                {"id": "latest", "label": "Último estado", "endpoint": "/api/browser-provider-execution/latest", "priority": "high"},
            ],
        }

    def get_status(self) -> Dict[str, Any]:
        latest = self.latest()
        matrix = self.module_matrix()
        return {
            "ok": True,
            "mode": "browser_provider_execution_status",
            "available_module_count": matrix.get("available_count", 0),
            "missing_or_error_count": matrix.get("missing_or_error_count", 0),
            "plan_count": latest.get("plan_count", 0),
            "session_count": latest.get("session_count", 0),
            "can_continue_without_apk": True,
            "stops_only_for": self.STOP_REASONS,
        }

    def get_package(self) -> Dict[str, Any]:
        return {"ok": True, "mode": "browser_provider_execution_package", "package": {"status": self.get_status(), "panel": self.panel(), "latest": self.latest()}}


browser_provider_execution_hub_service = BrowserProviderExecutionHubService()
