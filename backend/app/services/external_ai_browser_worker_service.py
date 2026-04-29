from __future__ import annotations

import importlib.util
from datetime import datetime, timezone
from typing import Any, Dict, List
from uuid import uuid4

from app.services.external_ai_session_plan_service import external_ai_session_plan_service


class ExternalAiBrowserWorkerService:
    """Safe browser worker contract for external AI chat sessions.

    The worker is intentionally defensive:
    - Playwright is optional.
    - No credentials are stored.
    - Login is manual through operator popup/confirmation.
    - Every step writes safe checkpoints.
    - If the browser/session cannot run, God Mode returns a resumable plan.
    """

    CHAT_READY_MARKERS = {
        "chatgpt": ["textarea", "contenteditable", "prompt", "message"],
        "claude": ["textarea", "contenteditable", "prompt"],
        "gemini": ["textarea", "contenteditable", "prompt"],
        "perplexity": ["textarea", "contenteditable", "ask"],
    }

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def capability_report(self) -> Dict[str, Any]:
        playwright_available = importlib.util.find_spec("playwright") is not None
        return {
            "ok": True,
            "mode": "external_ai_browser_worker_capability",
            "status": "browser_worker_available" if playwright_available else "playwright_not_installed",
            "playwright_available": playwright_available,
            "safe_mode": True,
            "can_open_browser": playwright_available,
            "can_detect_login": "planned_runtime_probe",
            "can_read_visible_messages": "planned_after_page_ready",
            "can_scroll_history": "planned_next_phase",
            "can_send_prompt": "planned_requires_safety_gate",
            "stores_credentials": False,
            "operator_login_required": True,
            "install_hint": "Install playwright and browsers in the PC backend environment when ready.",
        }

    def prepare_session(
        self,
        provider_id: str = "chatgpt",
        conversation_url: str | None = None,
        operator_goal: str | None = None,
        tenant_id: str = "owner-andre",
        open_browser: bool = False,
    ) -> Dict[str, Any]:
        plan_result = external_ai_session_plan_service.create_plan(
            provider_id=provider_id,
            conversation_url=conversation_url,
            operator_goal=operator_goal,
            tenant_id=tenant_id,
        )
        if not plan_result.get("ok"):
            return plan_result
        plan = plan_result["plan"]
        capability = self.capability_report()
        worker = {
            "worker_id": f"external-ai-browser-worker-{uuid4().hex[:12]}",
            "session_id": plan["session_id"],
            "provider_id": provider_id,
            "created_at": self._now(),
            "status": "prepared",
            "open_browser_requested": open_browser,
            "capability": capability,
            "next_step": "manual_login_popup" if plan.get("requires_manual_login") else "open_browser_or_service",
            "browser_action": self._browser_action(plan=plan, capability=capability, open_browser=open_browser),
            "safe_checkpoints": [
                external_ai_session_plan_service.record_checkpoint(
                    session_id=plan["session_id"],
                    step="browser_worker_prepared",
                    status="prepared",
                    safe_state={
                        "provider_id": provider_id,
                        "conversation_url": plan.get("conversation_url"),
                        "open_browser_requested": open_browser,
                        "playwright_available": capability["playwright_available"],
                    },
                )["checkpoint"]
            ],
        }
        login_popup = None
        if plan.get("requires_manual_login"):
            login_popup = external_ai_session_plan_service.request_login_popup(
                provider_id=provider_id,
                session_id=plan["session_id"],
                reason="browser_worker_requires_manual_login",
            )
            worker["safe_checkpoints"].append(
                external_ai_session_plan_service.record_checkpoint(
                    session_id=plan["session_id"],
                    step="request_manual_login_if_needed",
                    status="waiting_operator_login",
                    safe_state={"provider_id": provider_id, "popup_request_id": login_popup.get("request", {}).get("request_id")},
                )["checkpoint"]
            )
        return {
            "ok": True,
            "mode": "external_ai_browser_worker_prepare",
            "plan": plan,
            "worker": worker,
            "login_popup": login_popup,
            "operator_next": self._operator_next(worker=worker, login_popup=login_popup),
        }

    def open_session_probe(
        self,
        provider_id: str = "chatgpt",
        conversation_url: str | None = None,
        session_id: str | None = None,
    ) -> Dict[str, Any]:
        """Return a safe runtime probe plan.

        We do not run an actual browser in CI/server contexts. On a real PC this
        endpoint tells the desktop runner exactly what it is allowed to do.
        """
        capability = self.capability_report()
        provider = next((item for item in external_ai_session_plan_service.DEFAULT_PROVIDERS if item["id"] == provider_id), None)
        if provider is None:
            return {"ok": False, "mode": "external_ai_browser_open_probe", "error": "unknown_provider", "provider_id": provider_id}
        target_url = conversation_url or provider["base_url"]
        probe = {
            "probe_id": f"external-ai-browser-probe-{uuid4().hex[:12]}",
            "session_id": session_id,
            "provider_id": provider_id,
            "target_url": target_url,
            "created_at": self._now(),
            "status": "ready_for_pc_runner" if capability["playwright_available"] else "missing_playwright",
            "allowed_actions": [
                "open_non_persistent_browser_context",
                "navigate_to_target_url",
                "wait_for_operator_login_confirmation",
                "detect_basic_chat_input_presence",
                "save_safe_checkpoint",
            ],
            "forbidden_actions": [
                "read_password_fields",
                "store_cookies",
                "store_tokens",
                "bypass_login",
                "send_prompt_without_safety_gate",
            ],
            "chat_ready_markers": self.CHAT_READY_MARKERS.get(provider_id, ["textarea", "contenteditable"]),
            "capability": capability,
            "resume_contract": external_ai_session_plan_service.resume_contract(),
        }
        if session_id:
            external_ai_session_plan_service.record_checkpoint(
                session_id=session_id,
                step="open_browser_or_service",
                status=probe["status"],
                safe_state={"provider_id": provider_id, "target_url": target_url, "playwright_available": capability["playwright_available"]},
            )
        return {"ok": True, "mode": "external_ai_browser_open_probe", "probe": probe}

    def confirm_manual_login(self, session_id: str, provider_id: str = "chatgpt", operator_confirmed: bool = True) -> Dict[str, Any]:
        status = "operator_confirmed_login" if operator_confirmed else "operator_login_not_confirmed"
        checkpoint = external_ai_session_plan_service.record_checkpoint(
            session_id=session_id,
            step="check_login_state",
            status=status,
            safe_state={"provider_id": provider_id, "operator_confirmed": operator_confirmed},
        )
        return {
            "ok": operator_confirmed,
            "mode": "external_ai_browser_login_confirmation",
            "session_id": session_id,
            "provider_id": provider_id,
            "status": status,
            "checkpoint": checkpoint.get("checkpoint"),
            "operator_next": {
                "label": "Preparar leitura da conversa" if operator_confirmed else "Reabrir popup de login",
                "endpoint": "/api/external-ai-browser/probe" if operator_confirmed else "/api/external-ai-session/login-popup",
                "route": "/app/home",
            },
        }

    def build_panel(self) -> Dict[str, Any]:
        capability = self.capability_report()
        latest = external_ai_session_plan_service.latest()
        return {
            "ok": True,
            "mode": "external_ai_browser_worker_panel",
            "headline": "Browser Worker para IAs externas",
            "status": capability["status"],
            "capability": capability,
            "latest": latest,
            "quick_buttons": [
                {"label": "Criar plano ChatGPT", "endpoint": "/api/external-ai-session/plan", "payload": {"provider_id": "chatgpt"}},
                {"label": "Preparar browser ChatGPT", "endpoint": "/api/external-ai-browser/prepare", "payload": {"provider_id": "chatgpt", "open_browser": False}},
                {"label": "Pedir login manual", "endpoint": "/api/external-ai-session/login-popup", "payload": {"provider_id": "chatgpt"}},
                {"label": "Retomar sessão", "endpoint": "/api/external-ai-session/resume"},
            ],
            "safety": {
                "no_credentials_saved": True,
                "manual_login_only": True,
                "resume_with_checkpoints": True,
                "no_prompt_send_in_this_phase": True,
            },
        }

    def _browser_action(self, plan: Dict[str, Any], capability: Dict[str, Any], open_browser: bool) -> Dict[str, Any]:
        if not open_browser:
            return {
                "status": "not_requested",
                "label": "Browser não aberto nesta chamada",
                "next": "Usar /api/external-ai-browser/probe no PC runner quando estiver pronto.",
            }
        if not capability["playwright_available"]:
            return {
                "status": "blocked_missing_playwright",
                "label": "Playwright não está instalado no ambiente do backend",
                "next": "Instalar dependência no PC antes de abrir browser controlado.",
            }
        return {
            "status": "ready_for_pc_runner",
            "label": "Ambiente preparado para abrir browser controlado",
            "target_url": plan.get("conversation_url"),
            "next": "Desktop runner deve abrir contexto não persistente e aguardar login manual.",
        }

    def _operator_next(self, worker: Dict[str, Any], login_popup: Dict[str, Any] | None) -> Dict[str, Any]:
        if login_popup:
            return {"label": "Fazer login manual", "endpoint": "/api/external-ai-session/login-popup", "route": "/app/home"}
        if worker["capability"].get("playwright_available"):
            return {"label": "Abrir probe browser", "endpoint": "/api/external-ai-browser/probe", "route": "/app/home"}
        return {"label": "Instalar/ativar Playwright no PC", "endpoint": "/api/external-ai-browser/capability", "route": "/app/home"}

    def get_status(self) -> Dict[str, Any]:
        capability = self.capability_report()
        return {
            "ok": True,
            "mode": "external_ai_browser_worker_status",
            "status": capability["status"],
            "playwright_available": capability["playwright_available"],
            "safe_mode": True,
            "stores_credentials": False,
        }

    def get_package(self) -> Dict[str, Any]:
        return {"ok": True, "mode": "external_ai_browser_worker_package", "package": {"status": self.get_status(), "panel": self.build_panel()}}


external_ai_browser_worker_service = ExternalAiBrowserWorkerService()
