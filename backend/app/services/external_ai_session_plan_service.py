from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List
from uuid import uuid4

from app.utils.atomic_json_store import AtomicJsonStore

DATA_DIR = Path("data")
SESSION_FILE = DATA_DIR / "external_ai_session_plans.json"
SESSION_STORE = AtomicJsonStore(
    SESSION_FILE,
    default_factory=lambda: {"version": 1, "sessions": [], "credential_requests": [], "checkpoints": []},
)


class ExternalAiSessionPlanService:
    """Registry and resumable session planning for external AI chat control.

    This service does not automate a browser yet and never stores secrets. It
    defines the safe contract needed before implementing browser/web-service
    control: registry, manual login popup requests, resumable checkpoints, and
    network interruption recovery.
    """

    DEFAULT_PROVIDERS = [
        {
            "id": "chatgpt",
            "label": "ChatGPT",
            "base_url": "https://chatgpt.com/",
            "access_mode": "browser_session_manual_login",
            "supports_existing_conversation": True,
            "supports_scroll_history": "planned",
            "supports_prompt_send": "planned",
        },
        {
            "id": "claude",
            "label": "Claude",
            "base_url": "https://claude.ai/",
            "access_mode": "browser_session_manual_login",
            "supports_existing_conversation": True,
            "supports_scroll_history": "planned",
            "supports_prompt_send": "planned",
        },
        {
            "id": "gemini",
            "label": "Gemini",
            "base_url": "https://gemini.google.com/",
            "access_mode": "browser_session_manual_login",
            "supports_existing_conversation": True,
            "supports_scroll_history": "planned",
            "supports_prompt_send": "planned",
        },
        {
            "id": "perplexity",
            "label": "Perplexity",
            "base_url": "https://www.perplexity.ai/",
            "access_mode": "browser_session_manual_login",
            "supports_existing_conversation": True,
            "supports_scroll_history": "planned",
            "supports_prompt_send": "planned",
        },
        {
            "id": "local_ollama",
            "label": "Ollama local",
            "base_url": "http://127.0.0.1:11434",
            "access_mode": "local_http_no_browser",
            "supports_existing_conversation": False,
            "supports_scroll_history": False,
            "supports_prompt_send": "available_via_local_ai_adapter",
        },
    ]

    SESSION_STEPS = [
        "create_session",
        "open_browser_or_service",
        "check_network",
        "check_login_state",
        "request_manual_login_if_needed",
        "confirm_chat_ready",
        "read_visible_messages",
        "scroll_history_if_needed",
        "prepare_prompt_safely",
        "request_operator_approval_if_sensitive",
        "send_prompt",
        "wait_for_response",
        "extract_response",
        "save_checkpoint",
        "return_to_god_mode",
    ]

    SENSITIVE_MARKERS = [
        "token",
        "password",
        "senha",
        "cookie",
        "bearer",
        "authorization",
        "secret",
        "api key",
        "private key",
        "credential",
    ]

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def _normalize(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        payload.setdefault("version", 1)
        payload.setdefault("sessions", [])
        payload.setdefault("credential_requests", [])
        payload.setdefault("checkpoints", [])
        return payload

    def providers(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "mode": "external_ai_providers",
            "provider_count": len(self.DEFAULT_PROVIDERS),
            "providers": self.DEFAULT_PROVIDERS,
            "policy": self.security_policy(),
        }

    def security_policy(self) -> Dict[str, Any]:
        return {
            "store_credentials": False,
            "store_tokens": False,
            "store_cookies": False,
            "manual_login_allowed": True,
            "credential_popup_ephemeral": True,
            "operator_approval_for_sensitive_prompt": True,
            "checkpoint_without_secrets": True,
            "resume_after_network_loss": True,
        }

    def create_plan(
        self,
        provider_id: str = "chatgpt",
        conversation_url: str | None = None,
        operator_goal: str | None = None,
        tenant_id: str = "owner-andre",
    ) -> Dict[str, Any]:
        provider = self._provider(provider_id)
        if provider is None:
            return {
                "ok": False,
                "mode": "external_ai_session_plan",
                "error": "unknown_provider",
                "provider_id": provider_id,
                "available_provider_ids": [item["id"] for item in self.DEFAULT_PROVIDERS],
            }
        session_id = f"external-ai-session-{uuid4().hex[:12]}"
        sensitive = self._contains_sensitive_text(operator_goal or "")
        plan = {
            "session_id": session_id,
            "tenant_id": tenant_id,
            "provider": provider,
            "conversation_url": conversation_url or provider["base_url"],
            "operator_goal": (operator_goal or "Abrir conversa externa e preparar pedido seguro.")[:1200],
            "created_at": self._now(),
            "updated_at": self._now(),
            "status": "planned",
            "current_step": "create_session",
            "next_step": "open_browser_or_service",
            "requires_manual_login": provider["access_mode"] == "browser_session_manual_login",
            "credential_popup": self._credential_popup(provider) if provider["access_mode"] == "browser_session_manual_login" else None,
            "resume_contract": self.resume_contract(),
            "safety": {
                "sensitive_prompt_detected": sensitive,
                "approval_required_before_send": sensitive,
                "store_credentials": False,
                "store_browser_session_secret": False,
            },
            "steps": self._step_cards(provider=provider, sensitive=sensitive),
        }
        self._record_session(plan)
        self._record_checkpoint(
            session_id=session_id,
            provider_id=provider_id,
            step="create_session",
            status="planned",
            safe_state={
                "conversation_url": plan["conversation_url"],
                "operator_goal_preview": plan["operator_goal"][:180],
                "requires_manual_login": plan["requires_manual_login"],
            },
        )
        return {
            "ok": True,
            "mode": "external_ai_session_plan",
            "plan": plan,
            "operator_next": {
                "label": "Abrir sessão externa",
                "endpoint": "/api/external-ai-session/next-step",
                "route": "/app/home",
            },
        }

    def request_login_popup(
        self,
        provider_id: str = "chatgpt",
        session_id: str | None = None,
        reason: str = "login_required",
    ) -> Dict[str, Any]:
        provider = self._provider(provider_id)
        if provider is None:
            return {"ok": False, "mode": "external_ai_login_popup", "error": "unknown_provider", "provider_id": provider_id}
        request_id = f"external-ai-login-{uuid4().hex[:12]}"
        popup = self._credential_popup(provider)
        request = {
            "request_id": request_id,
            "session_id": session_id,
            "provider_id": provider_id,
            "provider_label": provider["label"],
            "reason": reason,
            "created_at": self._now(),
            "status": "waiting_operator_input",
            "popup": popup,
            "security_notice": "Preencher manualmente no browser/popup. O God Mode não deve guardar passwords, tokens, cookies ou códigos 2FA.",
        }
        def mutate(payload: Dict[str, Any]) -> Dict[str, Any]:
            payload = self._normalize(payload)
            payload["credential_requests"].append(request)
            payload["credential_requests"] = payload["credential_requests"][-100:]
            return payload
        SESSION_STORE.update(mutate)
        return {
            "ok": True,
            "mode": "external_ai_login_popup",
            "request": request,
            "operator_next": {"label": "Preencher login manual", "route": "/app/home"},
        }

    def record_checkpoint(
        self,
        session_id: str,
        step: str,
        status: str = "checkpoint_saved",
        safe_state: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        clean_state = self._clean_safe_state(safe_state or {})
        checkpoint = self._record_checkpoint(
            session_id=session_id,
            provider_id=None,
            step=step,
            status=status,
            safe_state=clean_state,
        )
        self._update_session_step(session_id=session_id, step=step, status=status)
        return {"ok": True, "mode": "external_ai_checkpoint", "checkpoint": checkpoint}

    def resume_plan(self, session_id: str | None = None) -> Dict[str, Any]:
        state = self._normalize(SESSION_STORE.load())
        sessions = state["sessions"]
        if not sessions:
            return {
                "ok": False,
                "mode": "external_ai_resume_plan",
                "error": "no_sessions",
                "operator_next": {"label": "Criar plano de sessão", "endpoint": "/api/external-ai-session/plan"},
            }
        session = next((item for item in sessions if item.get("session_id") == session_id), None) if session_id else sessions[-1]
        if session is None:
            return {"ok": False, "mode": "external_ai_resume_plan", "error": "session_not_found", "session_id": session_id}
        checkpoints = [item for item in state["checkpoints"] if item.get("session_id") == session["session_id"]]
        latest = checkpoints[-1] if checkpoints else None
        resume = {
            "session_id": session["session_id"],
            "provider": session.get("provider"),
            "status": "resume_ready",
            "latest_checkpoint": latest,
            "safe_resume_step": self._safe_resume_step(latest),
            "resume_strategy": self.resume_contract(),
            "operator_next": self._resume_next(latest, session),
        }
        return {"ok": True, "mode": "external_ai_resume_plan", "resume": resume}

    def resume_contract(self) -> Dict[str, Any]:
        return {
            "network_loss_before_send": "resume_from_last_safe_checkpoint_and_recheck_login",
            "network_loss_after_send_before_response": "return_to_conversation_and_scan_recent_messages_before_resending",
            "browser_closed": "reopen_provider_url_then_recheck_login_and_conversation",
            "backend_restarted": "load_last_checkpoint_without_credentials",
            "do_not_duplicate_prompt": True,
            "safe_backtrack_steps": 2,
            "requires_operator_if_uncertain": True,
        }

    def latest(self) -> Dict[str, Any]:
        state = self._normalize(SESSION_STORE.load())
        return {
            "ok": True,
            "mode": "external_ai_session_latest",
            "session": state["sessions"][-1] if state["sessions"] else None,
            "credential_request": state["credential_requests"][-1] if state["credential_requests"] else None,
            "checkpoint": state["checkpoints"][-1] if state["checkpoints"] else None,
        }

    def get_status(self) -> Dict[str, Any]:
        state = self._normalize(SESSION_STORE.load())
        return {
            "ok": True,
            "mode": "external_ai_session_status",
            "status": "session_planning_ready",
            "provider_count": len(self.DEFAULT_PROVIDERS),
            "session_count": len(state["sessions"]),
            "credential_request_count": len(state["credential_requests"]),
            "checkpoint_count": len(state["checkpoints"]),
            "policy": self.security_policy(),
        }

    def get_package(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "mode": "external_ai_session_package",
            "package": {
                "status": self.get_status(),
                "providers": self.providers(),
                "latest": self.latest(),
                "resume_contract": self.resume_contract(),
            },
        }

    def _provider(self, provider_id: str) -> Dict[str, Any] | None:
        return next((item for item in self.DEFAULT_PROVIDERS if item["id"] == provider_id), None)

    def _credential_popup(self, provider: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "type": "manual_browser_login_popup",
            "provider_id": provider["id"],
            "title": f"Login manual: {provider['label']}",
            "target_url": provider["base_url"],
            "fields": [
                {"id": "open_browser", "label": "Abrir browser", "kind": "action"},
                {"id": "operator_confirms_logged_in", "label": "Já fiz login", "kind": "confirm_button"},
            ],
            "do_not_store_fields": ["password", "token", "cookie", "2fa_code", "authorization", "api_key"],
            "note": "O operador faz login manualmente. O God Mode só recebe confirmação/estado, não a password.",
        }

    def _step_cards(self, provider: Dict[str, Any], sensitive: bool) -> List[Dict[str, Any]]:
        cards = []
        for index, step in enumerate(self.SESSION_STEPS, start=1):
            cards.append({
                "step": index,
                "id": step,
                "label": step.replace("_", " ").title(),
                "status": "planned",
                "requires_operator": step in {"request_manual_login_if_needed", "request_operator_approval_if_sensitive"} and (provider["access_mode"] == "browser_session_manual_login" or sensitive),
                "checkpoint_after": step in {"check_login_state", "read_visible_messages", "scroll_history_if_needed", "send_prompt", "extract_response"},
            })
        return cards

    def _contains_sensitive_text(self, text: str) -> bool:
        low = text.lower()
        return any(marker in low for marker in self.SENSITIVE_MARKERS)

    def _record_session(self, plan: Dict[str, Any]) -> None:
        safe_plan = json.loads(json.dumps(plan))
        def mutate(payload: Dict[str, Any]) -> Dict[str, Any]:
            payload = self._normalize(payload)
            payload["sessions"].append(safe_plan)
            payload["sessions"] = payload["sessions"][-100:]
            return payload
        SESSION_STORE.update(mutate)

    def _record_checkpoint(self, session_id: str, provider_id: str | None, step: str, status: str, safe_state: Dict[str, Any]) -> Dict[str, Any]:
        checkpoint = {
            "checkpoint_id": f"external-ai-checkpoint-{uuid4().hex[:12]}",
            "session_id": session_id,
            "provider_id": provider_id,
            "step": step,
            "status": status,
            "created_at": self._now(),
            "safe_state": self._clean_safe_state(safe_state),
        }
        def mutate(payload: Dict[str, Any]) -> Dict[str, Any]:
            payload = self._normalize(payload)
            payload["checkpoints"].append(checkpoint)
            payload["checkpoints"] = payload["checkpoints"][-300:]
            return payload
        SESSION_STORE.update(mutate)
        return checkpoint

    def _clean_safe_state(self, safe_state: Dict[str, Any]) -> Dict[str, Any]:
        cleaned: Dict[str, Any] = {}
        for key, value in safe_state.items():
            low = key.lower()
            if any(marker.replace(" ", "_") in low or marker in low for marker in self.SENSITIVE_MARKERS):
                cleaned[key] = "[redacted]"
            elif isinstance(value, str) and self._contains_sensitive_text(value):
                cleaned[key] = "[redacted]"
            else:
                cleaned[key] = value
        return cleaned

    def _update_session_step(self, session_id: str, step: str, status: str) -> None:
        def mutate(payload: Dict[str, Any]) -> Dict[str, Any]:
            payload = self._normalize(payload)
            for session in payload["sessions"]:
                if session.get("session_id") == session_id:
                    session["current_step"] = step
                    session["status"] = status
                    session["updated_at"] = self._now()
                    break
            return payload
        SESSION_STORE.update(mutate)

    def _safe_resume_step(self, checkpoint: Dict[str, Any] | None) -> str:
        if not checkpoint:
            return "open_browser_or_service"
        step = checkpoint.get("step")
        if step == "send_prompt":
            return "wait_for_response_or_scan_before_resend"
        if step == "extract_response":
            return "return_to_god_mode"
        try:
            idx = self.SESSION_STEPS.index(step)
            return self.SESSION_STEPS[max(0, idx - 1)]
        except Exception:
            return "open_browser_or_service"

    def _resume_next(self, checkpoint: Dict[str, Any] | None, session: Dict[str, Any]) -> Dict[str, Any]:
        if session.get("requires_manual_login"):
            return {"label": "Reconfirmar login se necessário", "endpoint": "/api/external-ai-session/login-popup", "route": "/app/home"}
        return {"label": "Retomar sessão externa", "endpoint": "/api/external-ai-session/resume", "route": "/app/home"}


external_ai_session_plan_service = ExternalAiSessionPlanService()
