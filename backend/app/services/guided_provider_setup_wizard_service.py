from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List
from uuid import uuid4

from app.services.god_mode_local_vault_service import god_mode_local_vault_service
from app.services.mobile_pc_pairing_remote_access_service import mobile_pc_pairing_remote_access_service
from app.services.mobile_permission_relay_driver_voice_service import mobile_permission_relay_driver_voice_service
from app.utils.atomic_json_store import AtomicJsonStore

DATA_DIR = Path("data")
SETUP_FILE = DATA_DIR / "guided_provider_setup_wizard.json"
SETUP_STORE = AtomicJsonStore(
    SETUP_FILE,
    default_factory=lambda: {"version": 1, "setup_sessions": [], "browser_assist_contracts": [], "human_resume_events": [], "captured_results": [], "audit_log": []},
)

PROVIDERS = {
    "tailscale": {
        "display_name": "Tailscale",
        "official_url": "https://login.tailscale.com/start",
        "download_pc_url": "https://tailscale.com/download/windows",
        "download_mobile_url": "https://tailscale.com/download/android",
        "recommended_for": "Quick private phone-to-home-PC access without router port forwarding.",
        "safe_steps": [
            "Open official Tailscale page in controlled local browser.",
            "Show God Mode popup with only required fields.",
            "Store approved access fields in the local vault.",
            "Fill provider page from vault reference after Oner gate.",
            "If MFA/captcha/device approval appears, reveal the original provider page to Oner.",
            "After Oner resolves the original page, resume browser assist from the same session.",
            "Capture the final PC Tailscale IP or MagicDNS name.",
        ],
        "fields_to_collect": ["account_email", "account_secret", "pc_tailscale_ip_or_magicdns", "tailnet_label"],
        "browser_assist_supported": True,
    },
    "cloudflare_tunnel": {
        "display_name": "Cloudflare Tunnel",
        "official_url": "https://dash.cloudflare.com/",
        "download_pc_url": "https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads/",
        "download_mobile_url": "",
        "recommended_for": "Stable HTTPS URL/domain for future remote access.",
        "safe_steps": [
            "Open official Cloudflare dashboard in controlled local browser.",
            "Show God Mode popup with required account/setup fields.",
            "Store approved access fields in the local vault.",
            "Fill provider page from vault reference after Oner gate.",
            "If MFA/captcha/billing/DNS/consent appears, reveal the original provider page to Oner.",
            "After Oner resolves the original page, resume browser assist from the same session.",
            "Capture the final public HTTPS URL.",
        ],
        "fields_to_collect": ["account_email", "account_secret", "public_https_url", "tunnel_name", "hostname"],
        "browser_assist_supported": True,
    },
    "ngrok": {
        "display_name": "Ngrok",
        "official_url": "https://dashboard.ngrok.com/signup",
        "download_pc_url": "https://ngrok.com/download",
        "download_mobile_url": "",
        "recommended_for": "Temporary remote HTTPS tests.",
        "safe_steps": [
            "Open official ngrok page in controlled local browser.",
            "Show God Mode popup with required fields.",
            "Store approved access fields in the local vault.",
            "Fill provider page from vault reference after Oner gate.",
            "If MFA/captcha/plan choice/consent appears, reveal the original provider page to Oner.",
            "After Oner resolves the original page, resume browser assist from the same session.",
            "Capture generated HTTPS URL.",
        ],
        "fields_to_collect": ["account_email", "account_secret", "public_https_url", "tunnel_label"],
        "browser_assist_supported": True,
    },
    "manual_https": {
        "display_name": "Manual HTTPS URL",
        "official_url": "",
        "download_pc_url": "",
        "download_mobile_url": "",
        "recommended_for": "When the Oner already has a secure HTTPS endpoint reaching the God Mode PC.",
        "safe_steps": ["Paste final HTTPS URL.", "God Mode saves it as remote profile."],
        "fields_to_collect": ["public_https_url", "label"],
        "browser_assist_supported": False,
    },
}

SENSITIVE_FIELD_HINTS = {"account_secret", "secret", "token", "cookie", "private", "mfa_code", "recovery_code"}
HARD_STOPS = ["mfa", "captcha", "device_approval", "billing", "provider_terms", "unexpected_page", "security_warning"]


class GuidedProviderSetupWizardService:
    SERVICE_ID = "guided_provider_setup_wizard"
    VERSION = "phase_212_v3"

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def status(self) -> Dict[str, Any]:
        state = SETUP_STORE.load()
        return {
            "ok": True,
            "service": self.SERVICE_ID,
            "version": self.VERSION,
            "generated_at": self._now(),
            "setup_session_count": len(state.get("setup_sessions", [])),
            "browser_assist_contract_count": len(state.get("browser_assist_contracts", [])),
            "human_resume_event_count": len(state.get("human_resume_events", [])),
            "captured_result_count": len(state.get("captured_results", [])),
            "supported_providers": list(PROVIDERS.keys()),
            "can_open_official_pages": True,
            "can_mask_steps_with_popup": True,
            "can_fill_provider_forms_after_user_gate": True,
            "can_reveal_original_page_on_hard_stop": True,
            "can_resume_after_human_resolution": True,
            "can_store_account_fields_in_local_vault": True,
            "can_store_result_in_vault_or_remote_profile": True,
            "can_bypass_mfa_or_captcha": False,
            "can_run_without_oner_gate": False,
        }

    def providers(self) -> Dict[str, Any]:
        return {"ok": True, "providers": PROVIDERS}

    def start_setup(self, provider: str = "tailscale", tenant_id: str = "owner-andre") -> Dict[str, Any]:
        provider = provider if provider in PROVIDERS else "tailscale"
        spec = PROVIDERS[provider]
        session = {
            "setup_session_id": f"provider-setup-{uuid4().hex[:12]}",
            "created_at": self._now(),
            "tenant_id": tenant_id,
            "provider": provider,
            "display_name": spec["display_name"],
            "status": "browser_assist_ready" if spec.get("browser_assist_supported") else "manual_capture_ready",
            "official_url": spec["official_url"],
            "download_pc_url": spec["download_pc_url"],
            "download_mobile_url": spec["download_mobile_url"],
            "recommended_for": spec["recommended_for"],
            "safe_steps": spec["safe_steps"],
            "fields_to_collect": spec["fields_to_collect"],
            "browser_assist_supported": spec.get("browser_assist_supported", False),
            "operator_contract": {
                "open_official_url": spec["official_url"],
                "official_page_can_be_minimized_or_side_panel": True,
                "god_mode_popup_collects_required_fields": True,
                "store_sensitive_fields_in_local_vault": True,
                "fill_official_form_from_vault_reference_after_gate": True,
                "on_hard_stop_show_original_provider_page": True,
                "after_human_resolution_continue_from_same_session": True,
                "capture_only_final_endpoint_and_profile": True,
                "do_not_store_raw_values_in_repo_or_normal_memory": True,
            },
        }
        self._store("setup_sessions", session)
        self._audit("start_setup", session["setup_session_id"], provider, tenant_id)
        permission = mobile_permission_relay_driver_voice_service.create_permission_request(
            title=f"Guided setup: {spec['display_name']}",
            body=f"God Mode vai abrir o provider oficial, mostrar popup só com campos necessários, guardar no Vault e preencher localmente depois do teu gate. Se aparecer MFA/captcha/consentimento, mostra a página original e depois continua.",
            request_type="approval",
            project_id="GOD_MODE",
            source_ref={"type": "guided_provider_setup", "setup_session_id": session["setup_session_id"], "provider": provider},
            priority="medium",
            requires_sensitive_input=False,
            form_schema=[],
            wait_for_response=False,
            tenant_id=tenant_id,
        )
        return {"ok": True, "mode": "start_guided_provider_setup", "setup_session": session, "permission_request": permission}

    def create_browser_assist_contract(
        self,
        setup_session_id: str,
        form_values: Dict[str, Any],
        operation: str = "signup_or_login",
        tenant_id: str = "owner-andre",
    ) -> Dict[str, Any]:
        session = self._find("setup_sessions", "setup_session_id", setup_session_id)
        if not session:
            return {"ok": False, "error": "setup_session_not_found", "setup_session_id": setup_session_id}
        provider = str(session.get("provider") or "tailscale")
        vault_refs = []
        public_values: Dict[str, Any] = {}
        for key, value in (form_values or {}).items():
            key_text = str(key)[:120]
            if self._is_sensitive_field(key_text):
                if str(value or "").strip():
                    stored = god_mode_local_vault_service.store_secret(
                        raw_secret=str(value),
                        label=f"{provider}:{key_text}:browser-assist",
                        purpose=f"Provider browser assist field for {provider}",
                        secret_kind="provider_browser_assist_field",
                        provider=provider,
                        project_id="GOD_MODE",
                        scope="provider_setup_browser_assist",
                        source_ref={"type": "guided_provider_setup_browser_assist", "setup_session_id": setup_session_id, "field": key_text},
                        reuse_policy="reuse_for_same_provider_after_oner_gate",
                        tenant_id=tenant_id,
                    )
                    vault_refs.append({"field": key_text, "vault_reference": stored.get("vault_reference")})
                public_values[key_text] = "[VAULT_REFERENCE]"
            else:
                public_values[key_text] = str(value)[:1000]
        contract = {
            "browser_assist_contract_id": f"browser-assist-{uuid4().hex[:12]}",
            "setup_session_id": setup_session_id,
            "created_at": self._now(),
            "tenant_id": tenant_id,
            "provider": provider,
            "operation": operation,
            "status": "pending_mobile_gate",
            "official_url": session.get("official_url"),
            "browser_window_strategy": "open_official_page_local_and_keep_god_mode_popup_visible",
            "popup_fields": public_values,
            "vault_references": vault_refs,
            "operator_steps": [
                "Open official provider URL locally.",
                "Keep God Mode popup visible with only required fields/status.",
                "Fill normal fields from popup values.",
                "Fill sensitive fields from local vault references after approval.",
                "Click safe next/continue controls only for this provider setup flow.",
                "When hard stop appears, reveal original provider page to Oner.",
                "After Oner resolves the original provider page, resume browser assist from same session.",
                "Capture final endpoint/profile and store it in God Mode.",
            ],
            "hard_stops": HARD_STOPS,
            "hard_stop_behavior": {
                "show_original_provider_page": True,
                "hide_mask_until_resolved": True,
                "oner_clicks_continue_after_resolution": True,
                "resume_same_contract_after_resolution": True,
                "record_resume_event": True,
            },
            "can_execute_without_oner_gate": False,
            "can_read_raw_vault_values_in_response": False,
        }
        self._store("browser_assist_contracts", contract)
        self._patch_item("setup_sessions", "setup_session_id", setup_session_id, {"status": "browser_assist_contract_created", "last_browser_assist_contract_id": contract["browser_assist_contract_id"]})
        self._audit("create_browser_assist_contract", contract["browser_assist_contract_id"], provider, tenant_id)
        permission = mobile_permission_relay_driver_voice_service.create_permission_request(
            title=f"Executar browser assist: {session.get('display_name')}",
            body="God Mode recebeu os campos no popup, guardou campos sensíveis no Vault e pede aprovação para preencher/avançar no provider oficial localmente. Em hard stop mostra a página original e retoma quando resolveres.",
            request_type="blocking_decision",
            project_id="GOD_MODE",
            source_ref={"type": "guided_provider_browser_assist", "setup_session_id": setup_session_id, "browser_assist_contract_id": contract["browser_assist_contract_id"], "provider": provider},
            priority="high",
            requires_sensitive_input=False,
            form_schema=[],
            wait_for_response=True,
            tenant_id=tenant_id,
        )
        contract["permission_request_id"] = permission.get("permission_request", {}).get("permission_request_id")
        return {"ok": True, "mode": "create_browser_assist_contract", "browser_assist_contract": contract, "permission_request": permission}

    def resume_after_human_step(
        self,
        browser_assist_contract_id: str,
        hard_stop_type: str,
        note: str = "Oner resolved original provider page and asked God Mode to continue.",
        tenant_id: str = "owner-andre",
    ) -> Dict[str, Any]:
        contract = self._find("browser_assist_contracts", "browser_assist_contract_id", browser_assist_contract_id)
        if not contract:
            return {"ok": False, "error": "browser_assist_contract_not_found", "browser_assist_contract_id": browser_assist_contract_id}
        event = {
            "human_resume_event_id": f"human-resume-{uuid4().hex[:12]}",
            "browser_assist_contract_id": browser_assist_contract_id,
            "setup_session_id": contract.get("setup_session_id"),
            "provider": contract.get("provider"),
            "hard_stop_type": hard_stop_type if hard_stop_type in HARD_STOPS else "other",
            "note": str(note)[:1000],
            "created_at": self._now(),
            "tenant_id": tenant_id,
            "status": "resume_requested_after_original_page_resolution",
            "next_behavior": "continue_browser_assist_from_same_contract",
        }
        self._store("human_resume_events", event)
        self._patch_item("browser_assist_contracts", "browser_assist_contract_id", browser_assist_contract_id, {"status": "resume_requested", "last_human_resume_event_id": event["human_resume_event_id"], "updated_at": self._now()})
        self._audit("resume_after_human_step", browser_assist_contract_id, hard_stop_type, tenant_id)
        permission = mobile_permission_relay_driver_voice_service.create_permission_request(
            title="Continuar browser assist",
            body=f"Confirmaste que resolveste {event['hard_stop_type']} na página original. God Mode pede gate para continuar o mesmo fluxo assistido.",
            request_type="blocking_decision",
            project_id="GOD_MODE",
            source_ref={"type": "guided_provider_resume_after_human_step", "browser_assist_contract_id": browser_assist_contract_id, "human_resume_event_id": event["human_resume_event_id"]},
            priority="high",
            requires_sensitive_input=False,
            form_schema=[],
            wait_for_response=True,
            tenant_id=tenant_id,
        )
        event["permission_request_id"] = permission.get("permission_request", {}).get("permission_request_id")
        return {"ok": True, "mode": "resume_after_human_step", "human_resume_event": event, "permission_request": permission}

    def capture_result(
        self,
        setup_session_id: str,
        values: Dict[str, Any],
        store_remote_profile: bool = True,
        store_sensitive_material_in_vault: bool = False,
        tenant_id: str = "owner-andre",
    ) -> Dict[str, Any]:
        session = self._find("setup_sessions", "setup_session_id", setup_session_id)
        if not session:
            return {"ok": False, "error": "setup_session_not_found", "setup_session_id": setup_session_id}
        provider = session.get("provider", "manual_https")
        sanitized_values = self._sanitize_values(values)
        public_url = self._extract_public_url(provider, sanitized_values)
        result = {
            "captured_result_id": f"provider-result-{uuid4().hex[:12]}",
            "setup_session_id": setup_session_id,
            "created_at": self._now(),
            "tenant_id": tenant_id,
            "provider": provider,
            "values": sanitized_values,
            "public_url": public_url,
            "stored_remote_profile": False,
            "remote_profile": None,
            "vault_reference": None,
        }
        if store_remote_profile:
            remote = mobile_pc_pairing_remote_access_service.create_remote_access_plan(
                provider="tailscale" if provider == "tailscale" else ("cloudflare_tunnel" if provider == "cloudflare_tunnel" else ("ngrok" if provider == "ngrok" else "manual_public_url")),
                public_url=public_url,
                project_id="GOD_MODE",
                tenant_id=tenant_id,
            )
            result["stored_remote_profile"] = bool(remote.get("ok"))
            result["remote_profile"] = remote.get("remote_profile")
        if store_sensitive_material_in_vault and values.get("sensitive_material"):
            stored = god_mode_local_vault_service.store_secret(
                raw_secret=str(values.get("sensitive_material")),
                label=f"{provider}:guided-provider-setup",
                purpose=f"Guided setup material for {provider}",
                secret_kind="provider_setup_material",
                provider=str(provider),
                project_id="GOD_MODE",
                scope="remote_access_setup",
                source_ref={"type": "guided_provider_setup", "setup_session_id": setup_session_id},
                reuse_policy="manual_review_before_reuse",
                tenant_id=tenant_id,
            )
            result["vault_reference"] = stored.get("vault_reference")
        self._store("captured_results", result)
        self._patch_item("setup_sessions", "setup_session_id", setup_session_id, {"status": "captured", "captured_at": self._now()})
        self._audit("capture_result", setup_session_id, provider, tenant_id)
        return {"ok": True, "mode": "capture_guided_provider_result", "result": result}

    def dashboard(self) -> Dict[str, Any]:
        state = SETUP_STORE.load()
        return {
            "ok": True,
            "status": self.status(),
            "providers": PROVIDERS,
            "setup_sessions": state.get("setup_sessions", [])[-100:],
            "browser_assist_contracts": state.get("browser_assist_contracts", [])[-100:],
            "human_resume_events": state.get("human_resume_events", [])[-100:],
            "captured_results": state.get("captured_results", [])[-100:],
            "audit_log": state.get("audit_log", [])[-100:],
        }

    def package(self) -> Dict[str, Any]:
        return self.dashboard()

    def _extract_public_url(self, provider: str, values: Dict[str, Any]) -> str:
        if provider == "tailscale":
            value = str(values.get("pc_tailscale_ip_or_magicdns") or "").strip()
            if value.startswith("http://") or value.startswith("https://"):
                return value.rstrip("/")
            return f"http://{value}:8000" if value else ""
        return str(values.get("public_https_url") or values.get("url") or "").strip().rstrip("/")

    def _is_sensitive_field(self, key: str) -> bool:
        lowered = key.lower()
        return any(hint in lowered for hint in SENSITIVE_FIELD_HINTS)

    def _sanitize_values(self, values: Dict[str, Any]) -> Dict[str, Any]:
        sanitized = {}
        for key, value in (values or {}).items():
            key_text = str(key)[:120]
            if self._is_sensitive_field(key_text):
                sanitized[key_text] = "[REDACTED_STORED_ONLY_IF_EXPLICIT]"
            else:
                sanitized[key_text] = str(value)[:1000]
        return sanitized

    def _find(self, bucket: str, key: str, value: str) -> Dict[str, Any] | None:
        return next((item for item in SETUP_STORE.load().get(bucket, []) if item.get(key) == value), None)

    def _patch_item(self, bucket: str, key: str, value: str, patch: Dict[str, Any]) -> bool:
        found = False
        def mutate(state: Dict[str, Any]) -> Dict[str, Any]:
            nonlocal found
            for item in state.get(bucket, []):
                if item.get(key) == value:
                    item.update(patch)
                    found = True
            return state
        SETUP_STORE.update(mutate)
        return found

    def _store(self, bucket: str, item: Dict[str, Any]) -> None:
        def mutate(state: Dict[str, Any]) -> Dict[str, Any]:
            state.setdefault(bucket, []).append(item)
            state[bucket] = state.get(bucket, [])[-1000:]
            return state
        SETUP_STORE.update(mutate)

    def _audit(self, action: str, item_id: str, detail: str, tenant_id: str) -> None:
        self._store("audit_log", {"created_at": self._now(), "tenant_id": tenant_id, "action": action, "item_id": item_id, "detail": str(detail)[:600]})


guided_provider_setup_wizard_service = GuidedProviderSetupWizardService()
