from __future__ import annotations

import os
import platform
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List
from uuid import uuid4

from app.services.artifacts_center_service import artifacts_center_service
from app.services.final_install_use_pack_service import final_install_use_pack_service
from app.services.god_mode_global_state_service import god_mode_global_state_service
from app.services.mobile_pc_pairing_remote_access_service import mobile_pc_pairing_remote_access_service
from app.services.mobile_permission_relay_driver_voice_service import mobile_permission_relay_driver_voice_service
from app.utils.atomic_json_store import AtomicJsonStore

DATA_DIR = Path("data")
SUPPORT_FILE = DATA_DIR / "support_session_connector.json"
SUPPORT_STORE = AtomicJsonStore(
    SUPPORT_FILE,
    default_factory=lambda: {"version": 1, "support_sessions": [], "proposed_actions": [], "audit_log": []},
)

SAFE_ACTION_TYPES = {
    "read_diagnostics",
    "export_redacted_bundle",
    "create_github_issue_plan",
    "prepare_pr_plan",
    "request_screenshot",
    "run_safe_check_request",
}

BLOCKED_ACTION_TYPES = {
    "write_file",
    "apply_patch",
    "run_command",
    "change_vault",
    "deploy",
    "release",
    "merge",
    "browser_automation",
    "read_raw_secret",
}

SECRET_PATTERNS = [
    re.compile(r"(?i)(api[_-]?key|token|secret|password|passwd|cookie|private[_-]?key)\s*[:=]\s*[^\s]+"),
    re.compile(r"(?i)(bearer)\s+[a-z0-9._\-]+"),
]


class SupportSessionConnectorService:
    SERVICE_ID = "support_session_connector"
    VERSION = "phase_211_v1"

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def status(self) -> Dict[str, Any]:
        state = SUPPORT_STORE.load()
        active = [s for s in state.get("support_sessions", []) if s.get("status") == "active" and not self._is_expired(s)]
        return {
            "ok": True,
            "service": self.SERVICE_ID,
            "version": self.VERSION,
            "generated_at": self._now(),
            "store_file": str(SUPPORT_FILE),
            "active_session_count": len(active),
            "total_session_count": len(state.get("support_sessions", [])),
            "proposed_action_count": len(state.get("proposed_actions", [])),
            "assisted_action_mode": True,
            "read_only_by_default": True,
            "can_execute_without_mobile_gate": False,
            "raw_secret_exposure_allowed": False,
        }

    def create_session(
        self,
        ttl_minutes: int = 60,
        mode: str = "assisted_action",
        reason: str = "Temporary support/test session for installed God Mode.",
        tenant_id: str = "owner-andre",
    ) -> Dict[str, Any]:
        ttl_minutes = max(5, min(int(ttl_minutes), 240))
        session = {
            "support_session_id": f"support-session-{uuid4().hex[:12]}",
            "created_at": self._now(),
            "expires_at": (datetime.now(timezone.utc) + timedelta(minutes=ttl_minutes)).isoformat(),
            "tenant_id": tenant_id,
            "mode": mode if mode in {"diagnostic", "read_only", "assisted_action"} else "assisted_action",
            "reason": self._sanitize(reason)[:600],
            "status": "active",
            "one_time_approval_code": uuid4().hex[:8].upper(),
            "read_only_by_default": True,
            "all_actions_require_mobile_gate": True,
            "raw_secret_exposure_allowed": False,
            "allowed_action_types": sorted(SAFE_ACTION_TYPES),
            "blocked_action_types": sorted(BLOCKED_ACTION_TYPES),
        }
        self._store("support_sessions", session)
        self._audit("create_session", session["support_session_id"], "temporary support session created", tenant_id)
        return {"ok": True, "mode": "create_support_session", "support_session": session, "diagnostics": self.redacted_diagnostics(session["support_session_id"])}

    def redacted_diagnostics(self, support_session_id: str | None = None) -> Dict[str, Any]:
        session = self._get_active_session_or_none(support_session_id)
        if support_session_id and not session:
            return {"ok": False, "mode": "redacted_diagnostics", "error": "support_session_not_active_or_not_found"}
        diagnostics = {
            "ok": True,
            "mode": "redacted_diagnostics",
            "generated_at": self._now(),
            "support_session_id": support_session_id,
            "system": {
                "platform": platform.platform(),
                "python_version": platform.python_version(),
                "hostname_hash": self._hash(platform.node()),
                "cwd": self._safe_path(Path.cwd()),
            },
            "environment_summary": self._safe_environment_summary(),
            "global_state": self._safe_call(god_mode_global_state_service.package),
            "final_install_use": self._safe_call(final_install_use_pack_service.package),
            "pairing": self._safe_call(mobile_pc_pairing_remote_access_service.package),
            "artifacts": self._safe_call(artifacts_center_service.status),
            "support_status": self.status(),
            "recent_audit": SUPPORT_STORE.load().get("audit_log", [])[-50:],
            "redaction": {
                "raw_secrets_included": False,
                "vault_raw_values_included": False,
                "env_raw_values_included": False,
                "logs_are_summarized": True,
            },
        }
        return self._sanitize_payload(diagnostics)

    def propose_action(
        self,
        *,
        support_session_id: str,
        title: str,
        action_type: str,
        reason: str,
        proposed_payload: Dict[str, Any] | None = None,
        risk_level: str = "low",
        rollback_hint: str = "No automatic rollback required.",
        tenant_id: str = "owner-andre",
    ) -> Dict[str, Any]:
        session = self._get_active_session_or_none(support_session_id)
        if not session:
            return {"ok": False, "mode": "propose_support_action", "error": "support_session_not_active_or_expired"}
        blocked = action_type in BLOCKED_ACTION_TYPES
        action = {
            "support_action_id": f"support-action-{uuid4().hex[:12]}",
            "support_session_id": support_session_id,
            "created_at": self._now(),
            "tenant_id": tenant_id,
            "title": self._sanitize(title)[:200],
            "action_type": self._sanitize(action_type)[:80],
            "reason": self._sanitize(reason)[:1000],
            "risk_level": risk_level if risk_level in {"low", "medium", "high"} else "medium",
            "rollback_hint": self._sanitize(rollback_hint)[:1000],
            "proposed_payload": self._sanitize_payload(proposed_payload or {}),
            "status": "blocked_requires_explicit_design" if blocked else "pending_mobile_gate",
            "blocked_by_policy": blocked,
            "permission_request_id": None,
            "result_summary": None,
        }
        permission = None
        if not blocked:
            permission = mobile_permission_relay_driver_voice_service.create_permission_request(
                title=f"Support action: {action['title']}",
                body=f"Temporary support session requests approval. Risk: {action['risk_level']}. Reason: {action['reason']}",
                request_type="blocking_decision",
                project_id="GOD_MODE",
                source_ref={"type": "support_session_action", "support_session_id": support_session_id, "support_action_id": action["support_action_id"], "action_type": action_type},
                priority="high" if action["risk_level"] == "high" else "medium",
                requires_sensitive_input=False,
                form_schema=[],
                wait_for_response=True,
                tenant_id=tenant_id,
            )
            action["permission_request_id"] = permission.get("permission_request", {}).get("permission_request_id")
        self._store("proposed_actions", action)
        self._audit("propose_action", action["support_action_id"], f"type={action_type} status={action['status']}", tenant_id)
        return {"ok": True, "mode": "propose_support_action", "support_action": action, "permission_request": permission}

    def record_action_result(
        self,
        support_action_id: str,
        result_summary: str,
        status: str = "completed",
        tenant_id: str = "owner-andre",
    ) -> Dict[str, Any]:
        allowed = {"completed", "failed", "cancelled", "skipped"}
        final_status = status if status in allowed else "completed"
        patch = {"status": final_status, "completed_at": self._now(), "result_summary": self._sanitize(result_summary)[:1200]}
        updated = self._patch_item("proposed_actions", "support_action_id", support_action_id, patch)
        self._audit("record_action_result", support_action_id, final_status, tenant_id)
        return {"ok": updated, "mode": "record_support_action_result", "support_action_id": support_action_id, "status": final_status}

    def revoke_session(self, support_session_id: str, tenant_id: str = "owner-andre") -> Dict[str, Any]:
        updated = self._patch_item("support_sessions", "support_session_id", support_session_id, {"status": "revoked", "revoked_at": self._now()})
        self._audit("revoke_session", support_session_id, "session revoked", tenant_id)
        return {"ok": updated, "mode": "revoke_support_session", "support_session_id": support_session_id, "status": "revoked" if updated else "not_found"}

    def dashboard(self) -> Dict[str, Any]:
        state = SUPPORT_STORE.load()
        sessions = state.get("support_sessions", [])[-50:]
        actions = state.get("proposed_actions", [])[-100:]
        return {
            "ok": True,
            "mode": "support_session_dashboard",
            "status": self.status(),
            "support_sessions": sessions,
            "proposed_actions": actions,
            "audit_log": state.get("audit_log", [])[-100:],
        }

    def package(self) -> Dict[str, Any]:
        return {"status": self.status(), "dashboard": self.dashboard(), "policy": self.policy()}

    def policy(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "policy": {
                "default_mode": "read_only",
                "assisted_action_mode": True,
                "all_actions_require_mobile_gate": True,
                "session_has_ttl": True,
                "session_is_revocable": True,
                "raw_secret_exposure_allowed": False,
                "safe_action_types": sorted(SAFE_ACTION_TYPES),
                "blocked_action_types": sorted(BLOCKED_ACTION_TYPES),
            },
        }

    def _safe_environment_summary(self) -> Dict[str, Any]:
        keys = sorted(os.environ.keys())
        return {
            "env_key_count": len(keys),
            "safe_keys_present": [k for k in keys if k.upper() in {"PATH", "PYTHONPATH", "OS", "USERNAME", "USER", "COMPUTERNAME"}],
            "secret_like_key_count": sum(1 for k in keys if self._looks_sensitive(k)),
            "raw_values_included": False,
        }

    def _safe_call(self, fn: Any) -> Dict[str, Any]:
        try:
            return self._sanitize_payload(fn())
        except Exception as exc:
            return {"ok": False, "error": self._sanitize(str(exc))[:300]}

    def _sanitize_payload(self, payload: Any) -> Any:
        if isinstance(payload, dict):
            return {self._sanitize(str(k))[:120]: self._sanitize_payload(v) for k, v in payload.items() if not self._looks_sensitive(str(k))}
        if isinstance(payload, list):
            return [self._sanitize_payload(v) for v in payload[:300]]
        if isinstance(payload, str):
            return self._sanitize(payload)
        return payload

    def _sanitize(self, text: str) -> str:
        value = text or ""
        for pattern in SECRET_PATTERNS:
            value = pattern.sub("[REDACTED]", value)
        return value.replace(".env", "env-file")

    def _looks_sensitive(self, key: str) -> bool:
        return any(word in key.lower() for word in ["token", "secret", "password", "cookie", "private", "credential", "authorization"])

    def _safe_path(self, path: Path) -> str:
        try:
            return str(path).replace(str(Path.home()), "~")
        except Exception:
            return str(path)

    def _hash(self, value: str) -> str:
        import hashlib
        return hashlib.sha256((value or "").encode("utf-8")).hexdigest()[:16]

    def _is_expired(self, session: Dict[str, Any]) -> bool:
        try:
            return datetime.fromisoformat(str(session.get("expires_at"))) < datetime.now(timezone.utc)
        except Exception:
            return True

    def _get_active_session_or_none(self, support_session_id: str | None) -> Dict[str, Any] | None:
        if not support_session_id:
            active = [s for s in SUPPORT_STORE.load().get("support_sessions", []) if s.get("status") == "active" and not self._is_expired(s)]
            return active[-1] if active else None
        session = self._find("support_sessions", "support_session_id", support_session_id)
        if not session or session.get("status") != "active" or self._is_expired(session):
            return None
        return session

    def _find(self, bucket: str, key: str, value: str) -> Dict[str, Any] | None:
        return next((item for item in SUPPORT_STORE.load().get(bucket, []) if item.get(key) == value), None)

    def _patch_item(self, bucket: str, key: str, value: str, patch: Dict[str, Any]) -> bool:
        found = False
        def mutate(state: Dict[str, Any]) -> Dict[str, Any]:
            nonlocal found
            for item in state.get(bucket, []):
                if item.get(key) == value:
                    item.update(patch)
                    found = True
            return state
        SUPPORT_STORE.update(mutate)
        return found

    def _store(self, bucket: str, item: Dict[str, Any]) -> None:
        def mutate(state: Dict[str, Any]) -> Dict[str, Any]:
            state.setdefault(bucket, []).append(item)
            state[bucket] = state.get(bucket, [])[-1500:]
            return state
        SUPPORT_STORE.update(mutate)

    def _audit(self, action: str, item_id: str, detail: str, tenant_id: str) -> None:
        self._store("audit_log", {"created_at": self._now(), "tenant_id": tenant_id, "action": action, "item_id": item_id, "detail": self._sanitize(detail)[:700]})


support_session_connector_service = SupportSessionConnectorService()
