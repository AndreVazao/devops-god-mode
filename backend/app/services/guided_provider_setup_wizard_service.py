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
    default_factory=lambda: {"version": 1, "setup_sessions": [], "captured_results": [], "audit_log": []},
)

PROVIDERS = {
    "tailscale": {
        "display_name": "Tailscale",
        "official_url": "https://login.tailscale.com/start",
        "download_pc_url": "https://tailscale.com/download/windows",
        "download_mobile_url": "https://tailscale.com/download/android",
        "recommended_for": "Quick private phone-to-home-PC access without router port forwarding.",
        "safe_steps": [
            "Open official Tailscale page.",
            "Create/sign in to Tailscale using the official browser/app.",
            "Install Tailscale on the home PC and Android phone.",
            "Approve both devices in the same tailnet.",
            "Copy the PC Tailscale IP or MagicDNS name into God Mode.",
            "God Mode stores the resulting endpoint/profile, not the login password.",
        ],
        "fields_to_collect": ["pc_tailscale_ip_or_magicdns", "tailnet_label"],
        "blocked": ["auto type password", "bypass MFA", "scrape private account pages", "store account password"],
    },
    "cloudflare_tunnel": {
        "display_name": "Cloudflare Tunnel",
        "official_url": "https://dash.cloudflare.com/",
        "download_pc_url": "https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads/",
        "download_mobile_url": "",
        "recommended_for": "Stable HTTPS URL/domain for future remote access.",
        "safe_steps": [
            "Open official Cloudflare dashboard.",
            "Sign in manually.",
            "Create a tunnel for the home PC.",
            "Map public hostname to local port 8000.",
            "Paste the final HTTPS URL into God Mode.",
            "Store tunnel material only in the local vault if needed.",
        ],
        "fields_to_collect": ["public_https_url", "tunnel_name", "hostname"],
        "blocked": ["auto type password", "bypass MFA", "change DNS without approval", "store account password"],
    },
    "ngrok": {
        "display_name": "Ngrok",
        "official_url": "https://dashboard.ngrok.com/signup",
        "download_pc_url": "https://ngrok.com/download",
        "download_mobile_url": "",
        "recommended_for": "Temporary remote HTTPS tests.",
        "safe_steps": [
            "Open official ngrok page.",
            "Sign in manually.",
            "Create a tunnel for local port 8000.",
            "Paste generated HTTPS URL into God Mode.",
            "Store auth material in local vault only if explicitly provided.",
        ],
        "fields_to_collect": ["public_https_url", "tunnel_label"],
        "blocked": ["auto type password", "bypass MFA", "store account password"],
    },
    "manual_https": {
        "display_name": "Manual HTTPS URL",
        "official_url": "",
        "download_pc_url": "",
        "download_mobile_url": "",
        "recommended_for": "When the Oner already has a secure HTTPS endpoint reaching the God Mode PC.",
        "safe_steps": ["Paste final HTTPS URL.", "God Mode saves it as remote profile."],
        "fields_to_collect": ["public_https_url", "label"],
        "blocked": ["store account password", "publish unsafe HTTP endpoint"],
    },
}


class GuidedProviderSetupWizardService:
    SERVICE_ID = "guided_provider_setup_wizard"
    VERSION = "phase_212_v1"

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
            "captured_result_count": len(state.get("captured_results", [])),
            "supported_providers": list(PROVIDERS.keys()),
            "can_open_official_pages": True,
            "can_mask_steps_with_guidance": True,
            "can_store_result_in_vault_or_remote_profile": True,
            "can_auto_type_credentials": False,
            "can_bypass_mfa": False,
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
            "status": "guided_manual_login_required",
            "official_url": spec["official_url"],
            "download_pc_url": spec["download_pc_url"],
            "download_mobile_url": spec["download_mobile_url"],
            "recommended_for": spec["recommended_for"],
            "safe_steps": spec["safe_steps"],
            "fields_to_collect": spec["fields_to_collect"],
            "blocked": spec["blocked"],
            "browser_contract": {
                "open_official_url": spec["official_url"],
                "show_guidance_overlay": True,
                "user_enters_login_directly_on_provider": True,
                "god_mode_stores_password": False,
                "god_mode_reads_private_provider_pages": False,
                "after_login_capture_only_final_endpoint": True,
            },
        }
        self._store("setup_sessions", session)
        self._audit("start_setup", session["setup_session_id"], provider, tenant_id)
        permission = mobile_permission_relay_driver_voice_service.create_permission_request(
            title=f"Guided setup: {spec['display_name']}",
            body=f"God Mode vai guiar o setup oficial de {spec['display_name']}. O login fica no browser/app oficial. Depois só guardamos endpoint/resultados aprovados.",
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

    def _sanitize_values(self, values: Dict[str, Any]) -> Dict[str, Any]:
        sanitized = {}
        for key, value in (values or {}).items():
            key_text = str(key)[:120]
            if any(word in key_text.lower() for word in ["password", "token", "secret", "cookie", "private"]):
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
