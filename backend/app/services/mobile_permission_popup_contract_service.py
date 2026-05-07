from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any, Dict, List


class MobilePermissionPopupContractService:
    SERVICE_ID = "mobile_permission_popup_contract"
    VERSION = "phase_205_v1"

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def build_contract(
        self,
        *,
        permission_request: Dict[str, Any],
        origin_service: str | None = None,
        action_title: str | None = None,
        action_description: str | None = None,
        data_sharing_fields: List[Dict[str, Any]] | None = None,
    ) -> Dict[str, Any]:
        request_type = str(permission_request.get("request_type") or "approval")
        requires_form = bool(permission_request.get("requires_sensitive_input")) or request_type in {"sensitive_fill", "credential_prompt", "login_manual"}
        form_schema = permission_request.get("form_schema", []) if requires_form else []
        contract = {
            "popup_contract_id": f"popup-contract-{permission_request.get('permission_request_id', 'unknown')}",
            "generated_at": self._now(),
            "origin_service": self._sanitize(origin_service or self._infer_origin(permission_request)),
            "action_title": self._sanitize(action_title or permission_request.get("title") or "Autorizar ação?"),
            "action_description": self._sanitize(action_description or permission_request.get("body") or "O God Mode precisa de uma decisão para continuar."),
            "request_type": request_type,
            "project_id": permission_request.get("project_id", "GOD_MODE"),
            "permission_request_id": permission_request.get("permission_request_id"),
            "data_sharing_title": "A partilha de dados inclui",
            "data_sharing_fields": self._sanitize_fields(data_sharing_fields or self._default_fields(permission_request)),
            "primary_action": "Confirmar",
            "secondary_action": "Recusar",
            "edit_action": "Alterar",
            "requires_form_fill": requires_form,
            "form_schema": self._sanitize_form_schema(form_schema),
            "driver_safe_summary": permission_request.get("driver_safe_summary") or "God Mode precisa de autorização.",
            "offline_behavior": {
                "if_not_delivered": "offline_wait",
                "if_no_ack_after_timeout": "resend_pending",
                "resume_when": ["approved", "acknowledged"],
            },
            "security": {
                "raw_secret_values_stored": False,
                "can_store_raw_secrets": False,
                "sensitive_fields_store_mode": "vault_reference_only",
            },
        }
        return contract

    def example_contracts(self) -> Dict[str, Any]:
        approval_request = {
            "permission_request_id": "permission-request-example-approval",
            "project_id": "GOD_MODE",
            "title": "Create pull request in AndreVazao/devops-god-mode?",
            "body": "This will open a pull request for Phase 205.",
            "request_type": "approval",
            "requires_sensitive_input": False,
            "driver_safe_summary": "God Mode precisa de autorização para criar um PR. Podes dizer aprovar ou rejeitar.",
        }
        sensitive_request = {
            "permission_request_id": "permission-request-example-sensitive",
            "project_id": "GOD_MODE",
            "title": "Login manual necessário",
            "body": "O provider precisa de login ou código. Pára em segurança antes de preencher.",
            "request_type": "credential_prompt",
            "requires_sensitive_input": True,
            "form_schema": [{"name": "credential_value", "label": "Credencial / código", "type": "password", "required": True, "sensitive": True, "store_mode": "vault_reference_only"}],
            "driver_safe_summary": "Precisa de preenchimento manual. Pára em segurança antes de escrever.",
        }
        return {
            "ok": True,
            "examples": {
                "approval_popup": self.build_contract(permission_request=approval_request, origin_service="GitHub"),
                "sensitive_fill_popup": self.build_contract(permission_request=sensitive_request, origin_service="Provider Login"),
            },
        }

    def _infer_origin(self, request: Dict[str, Any]) -> str:
        source = request.get("source_ref") or {}
        source_type = str(source.get("type") or "").lower()
        if "github" in source_type or "pull" in source_type or "repo" in source_type:
            return "GitHub"
        request_type = request.get("request_type")
        if request_type in {"login_manual", "credential_prompt"}:
            return "Provider Login"
        if request_type == "sensitive_fill":
            return "Vault / Sensitive Fill"
        return "God Mode PC"

    def _default_fields(self, request: Dict[str, Any]) -> List[Dict[str, Any]]:
        source = request.get("source_ref") or {}
        fields = [
            {"label": "Name", "value": f"AndreVazao, {request.get('tenant_id', 'owner-andre')}"},
            {"label": "Project", "value": request.get("project_id", "GOD_MODE")},
            {"label": "Request", "value": request.get("permission_request_id", "")},
        ]
        for key in ["repository", "branch", "path", "provider", "url", "type"]:
            if source.get(key):
                fields.append({"label": key.title(), "value": source.get(key)})
        return fields

    def _sanitize_fields(self, fields: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        safe = []
        for field in fields[:25]:
            label = self._sanitize(str(field.get("label", "Campo")))[:80]
            value = self._sanitize(str(field.get("value", "")))[:300]
            safe.append({"label": label, "value": value})
        return safe

    def _sanitize_form_schema(self, schema: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        safe = []
        for field in schema[:20]:
            name = re.sub(r"[^A-Za-z0-9_\-]+", "_", str(field.get("name", "field")))[:80]
            sensitive = bool(field.get("sensitive", False))
            safe.append({
                "name": name,
                "label": self._sanitize(str(field.get("label", "Campo")))[:120],
                "type": str(field.get("type", "text")) if str(field.get("type", "text")) in {"text", "password", "code", "choice", "boolean", "voice_text"} else "text",
                "required": bool(field.get("required", False)),
                "sensitive": sensitive,
                "store_mode": "vault_reference_only" if sensitive else "plain_ok",
                "raw_value_stored": False if sensitive else None,
            })
        return safe

    def _sanitize(self, text: str) -> str:
        lines = []
        for line in (text or "").splitlines():
            lowered = line.lower()
            if any(key in lowered for key in ["api_key=", "token=", "password=", "cookie=", "secret=", "private_key="]):
                lines.append("[REDACTED_SECRET_LINE]")
            else:
                lines.append(line)
        return "\n".join(lines).strip()


mobile_permission_popup_contract_service = MobilePermissionPopupContractService()
