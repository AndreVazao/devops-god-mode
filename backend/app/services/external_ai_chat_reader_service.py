from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List
from uuid import uuid4

from app.services.external_ai_browser_worker_service import external_ai_browser_worker_service
from app.services.external_ai_session_plan_service import external_ai_session_plan_service


class ExternalAiChatReaderService:
    """Safe reader and scroll plan for external AI chat conversations.

    This phase prepares visible-message reading and history scrolling. It does
    not send prompts and does not store credentials/cookies/tokens.
    """

    PROVIDER_READER_HINTS = {
        "chatgpt": {
            "message_selectors": ["[data-message-author-role]", "article", "main [role='article']"],
            "role_hints": ["user", "assistant", "tool", "system"],
            "scroll_container_candidates": ["main", "[role='main']", "body"],
            "input_markers": ["textarea", "[contenteditable='true']"],
        },
        "claude": {
            "message_selectors": ["[data-testid*='message']", "main div", "article"],
            "role_hints": ["human", "assistant"],
            "scroll_container_candidates": ["main", "[role='main']", "body"],
            "input_markers": ["div[contenteditable='true']", "textarea"],
        },
        "gemini": {
            "message_selectors": ["message-content", "model-response", "user-query", "main *"],
            "role_hints": ["user", "model"],
            "scroll_container_candidates": ["main", "body"],
            "input_markers": ["rich-textarea", "textarea", "[contenteditable='true']"],
        },
        "perplexity": {
            "message_selectors": ["[data-testid*='message']", "main div", "article"],
            "role_hints": ["user", "assistant", "answer"],
            "scroll_container_candidates": ["main", "body"],
            "input_markers": ["textarea", "[contenteditable='true']"],
        },
    }

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def capability_report(self) -> Dict[str, Any]:
        browser = external_ai_browser_worker_service.capability_report()
        return {
            "ok": True,
            "mode": "external_ai_chat_reader_capability",
            "status": "reader_plan_ready",
            "browser_worker_status": browser.get("status"),
            "playwright_available": browser.get("playwright_available"),
            "can_plan_visible_read": True,
            "can_plan_scroll_history": True,
            "can_execute_runtime_read": "pc_runner_required",
            "can_send_prompt": False,
            "stores_credentials": False,
            "stores_cookies": False,
            "stores_tokens": False,
        }

    def build_reader_plan(
        self,
        provider_id: str = "chatgpt",
        session_id: str | None = None,
        conversation_url: str | None = None,
        max_visible_messages: int = 30,
    ) -> Dict[str, Any]:
        hints = self._hints(provider_id)
        plan_id = f"external-ai-reader-plan-{uuid4().hex[:12]}"
        plan = {
            "plan_id": plan_id,
            "session_id": session_id,
            "provider_id": provider_id,
            "conversation_url": conversation_url,
            "created_at": self._now(),
            "status": "ready_for_pc_runner",
            "max_visible_messages": max(1, min(max_visible_messages, 80)),
            "reader_hints": hints,
            "runtime_steps": [
                "confirm_browser_context_ready",
                "confirm_login_state_without_reading_credentials",
                "detect_chat_input_or_message_area",
                "collect_visible_message_candidates",
                "normalize_message_text_and_role",
                "deduplicate_visible_messages",
                "save_safe_checkpoint",
                "return_visible_snapshot_to_god_mode",
            ],
            "forbidden_actions": [
                "read_password_fields",
                "store_cookies",
                "store_tokens",
                "send_prompt",
                "click_destructive_buttons",
                "bypass_login",
            ],
            "checkpoint_policy": {
                "checkpoint_step": "read_visible_messages",
                "save_message_text": True,
                "save_credentials": False,
                "save_cookies_or_tokens": False,
                "truncate_each_message_chars": 4000,
            },
        }
        if session_id:
            external_ai_session_plan_service.record_checkpoint(
                session_id=session_id,
                step="read_visible_messages",
                status="reader_plan_created",
                safe_state={
                    "provider_id": provider_id,
                    "plan_id": plan_id,
                    "conversation_url": conversation_url,
                    "max_visible_messages": plan["max_visible_messages"],
                },
            )
        return {"ok": True, "mode": "external_ai_chat_reader_plan", "plan": plan, "operator_next": {"label": "Executar leitura no PC runner", "endpoint": "/api/external-ai-chat-reader/runtime-instructions", "route": "/app/home"}}

    def build_scroll_plan(
        self,
        provider_id: str = "chatgpt",
        session_id: str | None = None,
        direction: str = "up",
        pages: int = 3,
    ) -> Dict[str, Any]:
        hints = self._hints(provider_id)
        safe_pages = max(1, min(pages, 10))
        plan_id = f"external-ai-scroll-plan-{uuid4().hex[:12]}"
        plan = {
            "plan_id": plan_id,
            "session_id": session_id,
            "provider_id": provider_id,
            "created_at": self._now(),
            "status": "ready_for_pc_runner",
            "direction": "up" if direction not in {"down", "bottom"} else direction,
            "pages": safe_pages,
            "scroll_container_candidates": hints["scroll_container_candidates"],
            "runtime_steps": [
                "snapshot_visible_messages_before_scroll",
                "scroll_container_safely",
                "wait_for_lazy_loaded_messages",
                "snapshot_visible_messages_after_scroll",
                "deduplicate_by_text_hash_and_role",
                "save_scroll_checkpoint",
                "stop_if_no_new_messages",
            ],
            "network_loss_resume": {
                "before_scroll": "return_to_latest_visible_snapshot",
                "during_scroll": "reopen_conversation_and_read_visible_before_retry",
                "after_scroll": "compare_before_after_snapshots_before_next_scroll",
            },
            "forbidden_actions": [
                "send_prompt",
                "click_sidebar_delete",
                "click_logout",
                "click_new_chat_without_operator_request",
            ],
        }
        if session_id:
            external_ai_session_plan_service.record_checkpoint(
                session_id=session_id,
                step="scroll_history_if_needed",
                status="scroll_plan_created",
                safe_state={"provider_id": provider_id, "plan_id": plan_id, "direction": plan["direction"], "pages": safe_pages},
            )
        return {"ok": True, "mode": "external_ai_chat_scroll_plan", "plan": plan, "operator_next": {"label": "Executar scroll no PC runner", "endpoint": "/api/external-ai-chat-reader/runtime-instructions", "route": "/app/home"}}

    def runtime_instructions(self, provider_id: str = "chatgpt") -> Dict[str, Any]:
        hints = self._hints(provider_id)
        return {
            "ok": True,
            "mode": "external_ai_chat_reader_runtime_instructions",
            "provider_id": provider_id,
            "instructions": {
                "read_visible_messages": {
                    "selectors": hints["message_selectors"],
                    "max_text_chars_per_message": 4000,
                    "max_messages_per_snapshot": 80,
                    "normalize_fields": ["role", "text", "index", "source_selector", "visible"],
                },
                "scroll_history": {
                    "container_candidates": hints["scroll_container_candidates"],
                    "default_direction": "up",
                    "max_pages_without_operator_ok": 10,
                    "stop_when_no_new_messages": True,
                },
                "safety": {
                    "do_not_send_prompt": True,
                    "do_not_read_password_fields": True,
                    "do_not_store_browser_secrets": True,
                    "checkpoint_every_snapshot": True,
                },
            },
            "pc_runner_contract": self.pc_runner_contract(provider_id=provider_id),
        }

    def normalize_snapshot(
        self,
        provider_id: str = "chatgpt",
        session_id: str | None = None,
        raw_messages: List[Dict[str, Any]] | None = None,
    ) -> Dict[str, Any]:
        messages = [self._normalize_message(item, idx) for idx, item in enumerate(raw_messages or [])]
        messages = self._dedupe(messages)
        snapshot_id = f"external-ai-snapshot-{uuid4().hex[:12]}"
        snapshot = {
            "snapshot_id": snapshot_id,
            "session_id": session_id,
            "provider_id": provider_id,
            "created_at": self._now(),
            "message_count": len(messages),
            "messages": messages[:80],
            "summary": self._snapshot_summary(messages),
        }
        if session_id:
            external_ai_session_plan_service.record_checkpoint(
                session_id=session_id,
                step="read_visible_messages",
                status="visible_snapshot_saved",
                safe_state={"provider_id": provider_id, "snapshot_id": snapshot_id, "message_count": len(messages), "summary": snapshot["summary"]},
            )
        return {"ok": True, "mode": "external_ai_chat_visible_snapshot", "snapshot": snapshot}

    def pc_runner_contract(self, provider_id: str = "chatgpt") -> Dict[str, Any]:
        hints = self._hints(provider_id)
        return {
            "provider_id": provider_id,
            "allowed_browser_actions": [
                "query_visible_text",
                "query_message_candidates",
                "scroll_container",
                "wait_for_visible_messages",
                "return_snapshot",
            ],
            "blocked_browser_actions": [
                "fill_prompt_input",
                "press_enter_to_send",
                "read_password_input",
                "export_cookies",
                "export_tokens",
                "bypass_login",
            ],
            "selectors": hints,
            "resume_rules": external_ai_session_plan_service.resume_contract(),
        }

    def build_panel(self) -> Dict[str, Any]:
        capability = self.capability_report()
        latest = external_ai_session_plan_service.latest()
        return {
            "ok": True,
            "mode": "external_ai_chat_reader_panel",
            "headline": "Leitor e scroll de chats IA",
            "status": capability["status"],
            "capability": capability,
            "latest": latest,
            "quick_buttons": [
                {"label": "Plano leitura ChatGPT", "endpoint": "/api/external-ai-chat-reader/reader-plan", "payload": {"provider_id": "chatgpt"}},
                {"label": "Plano scroll ChatGPT", "endpoint": "/api/external-ai-chat-reader/scroll-plan", "payload": {"provider_id": "chatgpt", "direction": "up"}},
                {"label": "Instruções PC runner", "endpoint": "/api/external-ai-chat-reader/runtime-instructions"},
                {"label": "Retomar sessão", "endpoint": "/api/external-ai-session/resume"},
            ],
            "safety": {
                "no_prompt_send": True,
                "no_credentials_saved": True,
                "scroll_has_checkpoints": True,
                "dedupe_before_resend_future": True,
            },
        }

    def get_status(self) -> Dict[str, Any]:
        capability = self.capability_report()
        return {
            "ok": True,
            "mode": "external_ai_chat_reader_status",
            "status": capability["status"],
            "playwright_available": capability["playwright_available"],
            "can_plan_visible_read": True,
            "can_plan_scroll_history": True,
            "can_send_prompt": False,
        }

    def get_package(self) -> Dict[str, Any]:
        return {"ok": True, "mode": "external_ai_chat_reader_package", "package": {"status": self.get_status(), "panel": self.build_panel()}}

    def _hints(self, provider_id: str) -> Dict[str, Any]:
        return self.PROVIDER_READER_HINTS.get(provider_id, self.PROVIDER_READER_HINTS["chatgpt"])

    def _normalize_message(self, item: Dict[str, Any], index: int) -> Dict[str, Any]:
        role = str(item.get("role") or item.get("author") or "unknown")[:40]
        text = str(item.get("text") or item.get("content") or item.get("inner_text") or "")[:4000]
        return {
            "index": index,
            "role": role,
            "text": text.strip(),
            "source_selector": str(item.get("source_selector") or item.get("selector") or "")[:120],
            "visible": bool(item.get("visible", True)),
            "text_hash": str(abs(hash((role, text.strip())))),
        }

    def _dedupe(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        seen = set()
        out = []
        for message in messages:
            key = message["text_hash"]
            if key in seen or not message.get("text"):
                continue
            seen.add(key)
            out.append(message)
        return out

    def _snapshot_summary(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        roles: Dict[str, int] = {}
        for message in messages:
            roles[message.get("role", "unknown")] = roles.get(message.get("role", "unknown"), 0) + 1
        return {"message_count": len(messages), "roles": roles, "last_message_preview": (messages[-1]["text"][:220] if messages else "")}


external_ai_chat_reader_service = ExternalAiChatReaderService()
