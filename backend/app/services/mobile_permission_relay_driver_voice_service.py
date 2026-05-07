from __future__ import annotations

import re
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List
from uuid import uuid4

from app.services.mobile_approval_cockpit_v2_service import mobile_approval_cockpit_v2_service
from app.utils.atomic_json_store import AtomicJsonStore

DATA_DIR = Path("data")
PERMISSION_RELAY_FILE = DATA_DIR / "mobile_permission_relay_driver_voice.json"
PERMISSION_RELAY_STORE = AtomicJsonStore(
    PERMISSION_RELAY_FILE,
    default_factory=lambda: {
        "version": 1,
        "permission_requests": [],
        "delivery_attempts": [],
        "voice_events": [],
        "wait_locks": [],
        "decision_log": [],
    },
)

REQUEST_STATUSES = {
    "queued",
    "sent",
    "delivered",
    "acknowledged",
    "approved",
    "rejected",
    "expired",
    "resend_pending",
    "offline_wait",
}

REQUEST_TYPES = {
    "approval",
    "login_manual",
    "sensitive_fill",
    "pause_continue",
    "blocking_decision",
    "voice_confirm",
    "credential_prompt",
}

SAFE_ACTIONS = {"approve", "reject", "acknowledge", "needs_changes", "pause", "continue", "filled", "offline_retry"}


class MobilePermissionRelayDriverVoiceService:
    SERVICE_ID = "mobile_permission_relay_driver_voice"
    VERSION = "phase_205_v1"

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def status(self) -> Dict[str, Any]:
        state = PERMISSION_RELAY_STORE.load()
        pending = [item for item in state.get("permission_requests", []) if item.get("status") in {"queued", "sent", "delivered", "resend_pending", "offline_wait"}]
        return {
            "ok": True,
            "service": self.SERVICE_ID,
            "version": self.VERSION,
            "generated_at": self._now(),
            "store_file": str(PERMISSION_RELAY_FILE),
            "permission_request_count": len(state.get("permission_requests", [])),
            "pending_request_count": len(pending),
            "delivery_attempt_count": len(state.get("delivery_attempts", [])),
            "voice_event_count": len(state.get("voice_events", [])),
            "can_resend_after_offline": True,
            "supports_driver_voice_mode": True,
            "can_store_raw_secrets": False,
            "can_unlock_sensitive_action_without_oner": False,
        }

    def policy(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "policy": {
                "principle": "PC brain may wait for mobile permission, resend if the phone is offline, and use driver-safe voice prompts without storing raw secrets.",
                "allowed": [
                    "create permission requests for mobile approval cockpit",
                    "create login/manual fill/sensitive fill prompts",
                    "enter wait mode on PC until decision arrives",
                    "track delivery attempts and offline resend state",
                    "accept short voice intents such as approve/reject/pause/continue",
                    "speak short summaries for driver mode",
                ],
                "blocked": [
                    "store raw passwords/tokens/cookies/API keys",
                    "force interaction while Oner is driving",
                    "auto-fill secrets without Oner/vault gate",
                    "merge/release/deploy/pay without explicit approval",
                    "private provider login automation without gate",
                ],
                "request_statuses": sorted(REQUEST_STATUSES),
                "request_types": sorted(REQUEST_TYPES),
                "safe_actions": sorted(SAFE_ACTIONS),
            },
        }

    def create_permission_request(
        self,
        title: str,
        body: str,
        request_type: str = "approval",
        project_id: str = "GOD_MODE",
        source_ref: Dict[str, Any] | None = None,
        priority: str = "medium",
        requires_sensitive_input: bool = False,
        form_schema: List[Dict[str, Any]] | None = None,
        wait_for_response: bool = True,
        ttl_minutes: int = 60,
        tenant_id: str = "owner-andre",
    ) -> Dict[str, Any]:
        request_type = request_type if request_type in REQUEST_TYPES else "approval"
        request_id = f"permission-request-{uuid4().hex[:12]}"
        expires_at = (datetime.now(timezone.utc) + timedelta(minutes=max(5, min(ttl_minutes, 1440)))).isoformat()
        safe_form_schema = self._sanitize_form_schema(form_schema or [])
        request = {
            "permission_request_id": request_id,
            "created_at": self._now(),
            "updated_at": self._now(),
            "tenant_id": tenant_id,
            "project_id": project_id,
            "title": self._sanitize(title)[:220],
            "body": self._sanitize(body)[:2000],
            "request_type": request_type,
            "priority": priority if priority in {"low", "medium", "high", "critical"} else "medium",
            "status": "queued",
            "source_ref": source_ref or {},
            "requires_sensitive_input": bool(requires_sensitive_input),
            "form_schema": safe_form_schema,
            "wait_for_response": bool(wait_for_response),
            "expires_at": expires_at,
            "resend_count": 0,
            "last_delivery_status": "not_sent",
            "driver_safe_summary": self._driver_summary(title, body, requires_sensitive_input),
            "can_store_raw_secrets": False,
            "can_continue_without_decision": False if wait_for_response else True,
        }
        self._store("permission_requests", request)
        mobile_card = self._create_mobile_card(request)
        wait_lock = self._create_wait_lock(request) if wait_for_response else None
        return {"ok": True, "mode": "create_permission_request", "permission_request": request, "mobile_card": mobile_card, "wait_lock": wait_lock}

    def mark_sent(self, permission_request_id: str, delivery_channel: str = "mobile_cockpit", device_hint: str = "android_phone", tenant_id: str = "owner-andre") -> Dict[str, Any]:
        return self._delivery_transition(permission_request_id, "sent", delivery_channel, device_hint, tenant_id)

    def mark_delivered(self, permission_request_id: str, delivery_channel: str = "mobile_cockpit", device_hint: str = "android_phone", tenant_id: str = "owner-andre") -> Dict[str, Any]:
        return self._delivery_transition(permission_request_id, "delivered", delivery_channel, device_hint, tenant_id)

    def mark_offline_wait(self, permission_request_id: str, reason: str = "phone_offline_or_no_network", tenant_id: str = "owner-andre") -> Dict[str, Any]:
        request = self._find_request(permission_request_id)
        if not request:
            return {"ok": False, "mode": "offline_wait", "error": "permission_request_not_found", "permission_request_id": permission_request_id}
        self._update_request(permission_request_id, {"status": "offline_wait", "last_delivery_status": reason, "updated_at": self._now()})
        self._log("offline_wait", permission_request_id, reason, tenant_id)
        return {"ok": True, "mode": "offline_wait", "permission_request": self._find_request(permission_request_id)}

    def mark_resend_pending(self, permission_request_id: str, reason: str = "no_ack_after_timeout", tenant_id: str = "owner-andre") -> Dict[str, Any]:
        request = self._find_request(permission_request_id)
        if not request:
            return {"ok": False, "mode": "resend_pending", "error": "permission_request_not_found", "permission_request_id": permission_request_id}
        resend_count = int(request.get("resend_count") or 0) + 1
        self._update_request(permission_request_id, {"status": "resend_pending", "resend_count": resend_count, "last_delivery_status": reason, "updated_at": self._now()})
        self._log("resend_pending", permission_request_id, reason, tenant_id)
        return {"ok": True, "mode": "resend_pending", "permission_request": self._find_request(permission_request_id)}

    def decide_permission(
        self,
        permission_request_id: str,
        decision: str,
        operator_note: str = "",
        form_values: Dict[str, Any] | None = None,
        via: str = "mobile_popup",
        tenant_id: str = "owner-andre",
    ) -> Dict[str, Any]:
        request = self._find_request(permission_request_id)
        if not request:
            return {"ok": False, "mode": "permission_decision", "error": "permission_request_not_found", "permission_request_id": permission_request_id}
        normalized = self._normalize_decision(decision)
        if normalized not in {"approved", "rejected", "acknowledged", "needs_changes"}:
            return {"ok": False, "mode": "permission_decision", "error": "invalid_decision", "allowed": ["approved", "rejected", "acknowledged", "needs_changes"]}
        safe_values = self._sanitize_form_values(form_values or {}, request.get("form_schema", []))
        new_status = "approved" if normalized == "approved" else "rejected" if normalized == "rejected" else "acknowledged"
        decision_payload = {
            "decision": normalized,
            "operator_note": self._sanitize(operator_note)[:1000],
            "form_values": safe_values,
            "via": via,
            "decided_at": self._now(),
            "raw_secret_values_stored": False,
        }
        self._update_request(permission_request_id, {"status": new_status, "decision": decision_payload, "updated_at": self._now()})
        self._release_wait_lock(permission_request_id, new_status)
        self._log("permission_decision", permission_request_id, normalized, tenant_id)
        return {"ok": True, "mode": "permission_decision", "permission_request": self._find_request(permission_request_id)}

    def register_voice_event(
        self,
        transcript: str,
        intent: str = "unknown",
        permission_request_id: str | None = None,
        driving_mode: bool = True,
        tenant_id: str = "owner-andre",
    ) -> Dict[str, Any]:
        normalized_intent = self._voice_intent(intent or transcript)
        event = {
            "voice_event_id": f"voice-event-{uuid4().hex[:12]}",
            "created_at": self._now(),
            "tenant_id": tenant_id,
            "permission_request_id": permission_request_id,
            "transcript": self._sanitize(transcript)[:1000],
            "intent": normalized_intent,
            "driving_mode": bool(driving_mode),
            "touch_required": normalized_intent in {"needs_manual_fill", "unknown"},
            "spoken_reply": self._spoken_reply(normalized_intent),
        }
        self._store("voice_events", event)
        result: Dict[str, Any] | None = None
        if permission_request_id and normalized_intent in {"approve", "reject", "acknowledge", "pause", "continue"}:
            decision = "approved" if normalized_intent in {"approve", "continue"} else "rejected" if normalized_intent in {"reject", "pause"} else "acknowledged"
            result = self.decide_permission(permission_request_id, decision=decision, operator_note=f"Voice: {event['transcript']}", via="driver_voice", tenant_id=tenant_id)
        return {"ok": True, "mode": "register_voice_event", "voice_event": event, "decision_result": result}

    def poll_pending_for_mobile(self, tenant_id: str = "owner-andre", limit: int = 50) -> Dict[str, Any]:
        now = datetime.now(timezone.utc)
        pending = []
        for item in PERMISSION_RELAY_STORE.load().get("permission_requests", []):
            if item.get("tenant_id") != tenant_id:
                continue
            if item.get("status") in {"queued", "sent", "delivered", "resend_pending", "offline_wait"}:
                expired = self._parse_dt(item.get("expires_at")) < now if item.get("expires_at") else False
                if expired:
                    self._update_request(item.get("permission_request_id"), {"status": "expired", "updated_at": self._now()})
                else:
                    pending.append(item)
        pending = pending[-max(1, min(limit, 200)):]
        return {"ok": True, "mode": "mobile_permission_poll", "pending_count": len(pending), "permission_requests": pending}

    def wait_status(self, permission_request_id: str) -> Dict[str, Any]:
        request = self._find_request(permission_request_id)
        locks = [item for item in PERMISSION_RELAY_STORE.load().get("wait_locks", []) if item.get("permission_request_id") == permission_request_id]
        return {"ok": bool(request), "mode": "permission_wait_status", "permission_request": request, "wait_locks": locks, "can_continue": request and request.get("status") in {"approved", "acknowledged"}}

    def dashboard(self, tenant_id: str = "owner-andre") -> Dict[str, Any]:
        state = PERMISSION_RELAY_STORE.load()
        return {
            "ok": True,
            "mode": "mobile_permission_relay_dashboard",
            "status": self.status(),
            "policy": self.policy(),
            "pending": self.poll_pending_for_mobile(tenant_id=tenant_id, limit=100).get("permission_requests", []),
            "recent_requests": state.get("permission_requests", [])[-200:],
            "recent_voice_events": state.get("voice_events", [])[-100:],
            "wait_locks": state.get("wait_locks", [])[-100:],
            "delivery_attempts": state.get("delivery_attempts", [])[-100:],
        }

    def package(self) -> Dict[str, Any]:
        return self.dashboard()

    def _create_mobile_card(self, request: Dict[str, Any]) -> Dict[str, Any]:
        actions = [
            {"action_id": "approve", "label": "OK / Aprovar", "decision": "approved"},
            {"action_id": "reject", "label": "Rejeitar", "decision": "rejected"},
            {"action_id": "needs_changes", "label": "Alterar", "decision": "needs_changes"},
        ]
        card_type = "provider_login_request" if request.get("request_type") in {"login_manual", "credential_prompt"} else "secret_binding_approval" if request.get("requires_sensitive_input") else "operator_command"
        return mobile_approval_cockpit_v2_service.create_card(
            title=request.get("title", "Permission request"),
            body=request.get("body", ""),
            card_type=card_type,
            project_id=request.get("project_id", "GOD_MODE"),
            tenant_id=request.get("tenant_id", "owner-andre"),
            priority=request.get("priority", "medium"),
            requires_approval=True,
            actions=actions,
            source_ref={"type": "mobile_permission_relay", "permission_request_id": request.get("permission_request_id")},
            metadata={
                "request_type": request.get("request_type"),
                "requires_sensitive_input": request.get("requires_sensitive_input"),
                "form_schema": request.get("form_schema", []),
                "driver_safe_summary": request.get("driver_safe_summary"),
                "can_store_raw_secrets": False,
            },
        )

    def _delivery_transition(self, permission_request_id: str, status: str, delivery_channel: str, device_hint: str, tenant_id: str) -> Dict[str, Any]:
        request = self._find_request(permission_request_id)
        if not request:
            return {"ok": False, "mode": "delivery_transition", "error": "permission_request_not_found", "permission_request_id": permission_request_id}
        attempt = {
            "delivery_attempt_id": f"delivery-attempt-{uuid4().hex[:12]}",
            "permission_request_id": permission_request_id,
            "created_at": self._now(),
            "tenant_id": tenant_id,
            "delivery_channel": delivery_channel,
            "device_hint": device_hint,
            "status": status,
        }
        self._store("delivery_attempts", attempt)
        self._update_request(permission_request_id, {"status": status, "last_delivery_status": status, "updated_at": self._now()})
        return {"ok": True, "mode": "delivery_transition", "permission_request": self._find_request(permission_request_id), "delivery_attempt": attempt}

    def _create_wait_lock(self, request: Dict[str, Any]) -> Dict[str, Any]:
        lock = {
            "wait_lock_id": f"wait-lock-{uuid4().hex[:12]}",
            "permission_request_id": request.get("permission_request_id"),
            "created_at": self._now(),
            "status": "waiting",
            "reason": request.get("request_type"),
            "pc_should_wait": True,
            "resume_when_status_in": ["approved", "acknowledged"],
        }
        self._store("wait_locks", lock)
        return lock

    def _release_wait_lock(self, permission_request_id: str, final_status: str) -> None:
        def mutate(state: Dict[str, Any]) -> Dict[str, Any]:
            for lock in state.get("wait_locks", []):
                if lock.get("permission_request_id") == permission_request_id and lock.get("status") == "waiting":
                    lock["status"] = "released" if final_status in {"approved", "acknowledged"} else "blocked"
                    lock["released_at"] = self._now()
                    lock["final_status"] = final_status
                    lock["pc_should_wait"] = False
            return state
        PERMISSION_RELAY_STORE.update(mutate)

    def _find_request(self, permission_request_id: str) -> Dict[str, Any] | None:
        return next((item for item in PERMISSION_RELAY_STORE.load().get("permission_requests", []) if item.get("permission_request_id") == permission_request_id), None)

    def _update_request(self, permission_request_id: str, patch: Dict[str, Any]) -> None:
        def mutate(state: Dict[str, Any]) -> Dict[str, Any]:
            for item in state.get("permission_requests", []):
                if item.get("permission_request_id") == permission_request_id:
                    item.update(patch)
            return state
        PERMISSION_RELAY_STORE.update(mutate)

    def _store(self, bucket: str, item: Dict[str, Any]) -> None:
        def mutate(state: Dict[str, Any]) -> Dict[str, Any]:
            state.setdefault(bucket, []).append(item)
            state[bucket] = state.get(bucket, [])[-2000:]
            return state
        PERMISSION_RELAY_STORE.update(mutate)

    def _log(self, action: str, request_id: str, detail: str, tenant_id: str) -> None:
        self._store("decision_log", {"created_at": self._now(), "tenant_id": tenant_id, "action": action, "permission_request_id": request_id, "detail": self._sanitize(detail)[:1000]})

    def _sanitize(self, text: str) -> str:
        lines = []
        for line in (text or "").splitlines():
            lowered = line.lower()
            if any(key in lowered for key in ["api_key=", "token=", "password=", "cookie=", "secret=", "private_key="]):
                lines.append("[REDACTED_SECRET_LINE]")
            else:
                lines.append(line)
        return "\n".join(lines).strip()

    def _sanitize_form_schema(self, schema: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        safe = []
        for field in schema[:20]:
            safe.append({
                "name": re.sub(r"[^A-Za-z0-9_\-]+", "_", str(field.get("name", "field")))[:80],
                "label": self._sanitize(str(field.get("label", "Campo")))[:120],
                "type": str(field.get("type", "text")) if str(field.get("type", "text")) in {"text", "password", "code", "choice", "boolean", "voice_text"} else "text",
                "required": bool(field.get("required", False)),
                "sensitive": bool(field.get("sensitive", False)),
                "store_mode": "vault_reference_only" if field.get("sensitive") else "plain_ok",
            })
        return safe

    def _sanitize_form_values(self, values: Dict[str, Any], schema: List[Dict[str, Any]]) -> Dict[str, Any]:
        sensitive = {item.get("name") for item in schema if item.get("sensitive")}
        safe: Dict[str, Any] = {}
        for key, value in values.items():
            clean_key = re.sub(r"[^A-Za-z0-9_\-]+", "_", str(key))[:80]
            if clean_key in sensitive:
                safe[clean_key] = {"provided": bool(value), "store_mode": "vault_reference_only", "raw_value_stored": False}
            else:
                safe[clean_key] = self._sanitize(str(value))[:1000]
        return safe

    def _driver_summary(self, title: str, body: str, sensitive: bool) -> str:
        base = f"God Mode precisa de autorização: {title}."
        if sensitive:
            base += " Tem dados sensíveis; para preencher, pára em segurança."
        else:
            base += " Podes dizer aprovar, rejeitar ou pausar."
        return base[:300]

    def _normalize_decision(self, decision: str) -> str:
        lower = (decision or "").lower().strip()
        return {"approve": "approved", "approved": "approved", "ok": "approved", "sim": "approved", "yes": "approved", "reject": "rejected", "rejected": "rejected", "não": "rejected", "nao": "rejected", "no": "rejected", "ack": "acknowledged", "acknowledge": "acknowledged", "acknowledged": "acknowledged", "needs_changes": "needs_changes", "alterar": "needs_changes"}.get(lower, lower)

    def _voice_intent(self, text: str) -> str:
        lower = (text or "").lower()
        if any(word in lower for word in ["aprova", "aprovar", "ok", "sim", "continua", "continue"]):
            return "approve" if "contin" not in lower else "continue"
        if any(word in lower for word in ["rejeita", "rejeitar", "não", "nao", "no"]):
            return "reject"
        if any(word in lower for word in ["pausa", "para", "espera"]):
            return "pause"
        if any(word in lower for word in ["preencher", "password", "senha", "login", "credencial"]):
            return "needs_manual_fill"
        if any(word in lower for word in ["ouvi", "recebido", "entendi"]):
            return "acknowledge"
        return "unknown"

    def _spoken_reply(self, intent: str) -> str:
        return {
            "approve": "Aprovado. O God Mode continua quando sincronizar.",
            "continue": "Continua autorizado. O PC vai retomar a tarefa.",
            "reject": "Rejeitado. O God Mode bloqueia essa ação.",
            "pause": "Pausado. O God Mode fica em espera.",
            "acknowledge": "Recebido.",
            "needs_manual_fill": "Precisa de preenchimento manual. Pára em segurança antes de escrever.",
            "unknown": "Não percebi a decisão. Vou manter em espera.",
        }.get(intent, "Recebido.")

    def _parse_dt(self, value: str) -> datetime:
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        except Exception:
            return datetime.now(timezone.utc) + timedelta(minutes=5)


mobile_permission_relay_driver_voice_service = MobilePermissionRelayDriverVoiceService()
