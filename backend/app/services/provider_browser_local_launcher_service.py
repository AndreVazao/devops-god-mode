from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List
from uuid import uuid4

from app.services.conversation_source_import_feed_service import conversation_source_import_feed_service
from app.services.mobile_approval_cockpit_v2_service import mobile_approval_cockpit_v2_service
from app.services.provider_browser_proof_link_service import PROVIDER_URLS, provider_browser_proof_link_service
from app.utils.atomic_json_store import AtomicJsonStore

DATA_DIR = Path("data")
LAUNCHER_FILE = DATA_DIR / "provider_browser_local_launcher.json"
LAUNCHER_STORE = AtomicJsonStore(
    LAUNCHER_FILE,
    default_factory=lambda: {"version": 1, "launch_contracts": [], "capture_contracts": [], "attention_cards": [], "imports": []},
)


class ProviderBrowserLocalLauncherService:
    """Local browser launcher/capture contract for provider proof.

    This phase prepares a real local-launch contract that the PC runtime can use.
    It does not store cookies, passwords or tokens and does not execute browser automation.
    """

    SERVICE_ID = "provider_browser_local_launcher"
    VERSION = "phase_197_v1"

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def status(self) -> Dict[str, Any]:
        state = LAUNCHER_STORE.load()
        return {
            "ok": True,
            "service": self.SERVICE_ID,
            "version": self.VERSION,
            "generated_at": self._now(),
            "store_file": str(LAUNCHER_FILE),
            "launch_contract_count": len(state.get("launch_contracts", [])),
            "capture_contract_count": len(state.get("capture_contracts", [])),
            "attention_card_count": len(state.get("attention_cards", [])),
            "import_count": len(state.get("imports", [])),
            "local_launcher_contract_ready": True,
            "executes_browser_automation": False,
            "stores_passwords": False,
            "stores_tokens": False,
            "stores_cookies": False,
        }

    def policy(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "policy": {
                "principle": "Prepare local browser launch/capture contracts without storing credentials or automating sensitive provider actions.",
                "allowed": ["prepare safe open URL", "prepare browser profile label", "create capture contract", "import manually captured transcript", "create login/capture attention cards"],
                "blocked": ["store passwords", "store tokens", "store cookies", "automate login", "send prompts automatically", "scrape private chats without approval"],
                "future_gate_required_for": ["automatic prompt send", "automatic capture", "browser DOM scraping", "provider session reuse automation"],
            },
        }

    def create_launch_contract(
        self,
        provider_id: str,
        project_hint: str = "GOD_MODE",
        plan_id: str | None = None,
        tenant_id: str = "owner-andre",
        purpose: str = "manual provider proof/capture",
    ) -> Dict[str, Any]:
        provider_id = (provider_id or "unknown").strip().lower()
        url = PROVIDER_URLS.get(provider_id, "about:blank")
        contract = {
            "launch_contract_id": f"provider-launch-{uuid4().hex[:12]}",
            "created_at": self._now(),
            "tenant_id": tenant_id,
            "provider_id": provider_id,
            "provider_label": provider_id.replace("_", " ").title(),
            "project_hint": project_hint,
            "plan_id": plan_id,
            "purpose": purpose,
            "safe_open_url": url,
            "browser_profile_label": f"godmode-{tenant_id}-{provider_id}",
            "manual_open_command_hint": self._command_hint(url),
            "requires_manual_login_if_not_authenticated": True,
            "captures_credentials": False,
            "stores_passwords": False,
            "stores_tokens": False,
            "stores_cookies": False,
            "executes_browser_automation": False,
            "next_step": "Open URL locally, login manually if needed, copy final provider answer into capture contract/import page.",
        }
        self._store("launch_contracts", contract)
        return {"ok": True, "mode": "provider_launch_contract", "launch_contract": contract}

    def create_capture_contract(
        self,
        launch_contract_id: str,
        title: str = "Provider captured conversation",
        provider: str | None = None,
        project_hint: str = "GOD_MODE",
        tenant_id: str = "owner-andre",
    ) -> Dict[str, Any]:
        launch = self._find("launch_contracts", "launch_contract_id", launch_contract_id)
        provider_id = provider or (launch or {}).get("provider_id") or "manual_provider"
        contract = {
            "capture_contract_id": f"provider-capture-{uuid4().hex[:12]}",
            "launch_contract_id": launch_contract_id,
            "created_at": self._now(),
            "tenant_id": tenant_id,
            "provider": provider_id,
            "title": title[:220],
            "project_hint": project_hint,
            "capture_mode": "manual_copy_paste",
            "expected_labels": ["Oner:", "User:", "Assistant:", "ChatGPT:", "Claude:", "Gemini:"],
            "import_endpoint": "/api/conversation-source-import-feed/import-text",
            "import_route": "/app/conversation-source-import-feed",
            "stores_passwords": False,
            "stores_tokens": False,
            "stores_cookies": False,
            "executes_browser_automation": False,
            "next_step": "Paste transcript/answer with labels into the conversation import page.",
        }
        self._store("capture_contracts", contract)
        return {"ok": True, "mode": "provider_capture_contract", "capture_contract": contract}

    def import_capture(
        self,
        capture_contract_id: str,
        transcript_text: str,
        tenant_id: str = "owner-andre",
        create_review_card: bool = True,
    ) -> Dict[str, Any]:
        capture = self._find("capture_contracts", "capture_contract_id", capture_contract_id)
        if not capture:
            return {"ok": False, "mode": "provider_capture_import", "error": "capture_contract_not_found", "capture_contract_id": capture_contract_id}
        imported = conversation_source_import_feed_service.import_text(
            transcript_text=transcript_text,
            provider=capture.get("provider", "manual_provider"),
            project_hint=capture.get("project_hint", "GOD_MODE"),
            title=capture.get("title", "Provider captured conversation"),
            source_ref=capture_contract_id,
            tenant_id=tenant_id,
            create_review_card=create_review_card,
        )
        item = {
            "provider_capture_import_id": f"provider-capture-import-{uuid4().hex[:12]}",
            "created_at": self._now(),
            "tenant_id": tenant_id,
            "capture_contract_id": capture_contract_id,
            "conversation_import_id": imported.get("import", {}).get("import_id"),
            "ledger_analysis_id": imported.get("import", {}).get("ledger_analysis_id"),
            "stores_passwords": False,
            "stores_tokens": False,
            "stores_cookies": False,
        }
        self._store("imports", item)
        return {"ok": True, "mode": "provider_capture_import", "provider_capture_import": item, "conversation_import": imported}

    def create_attention_card(self, launch_contract_id: str, tenant_id: str = "owner-andre") -> Dict[str, Any]:
        launch = self._find("launch_contracts", "launch_contract_id", launch_contract_id)
        if not launch:
            return {"ok": False, "mode": "provider_launcher_attention_card", "error": "launch_contract_not_found", "launch_contract_id": launch_contract_id}
        result = mobile_approval_cockpit_v2_service.create_card(
            title=f"Abrir provider no PC: {launch.get('provider_label')}",
            body=(
                f"Abre {launch.get('safe_open_url')} no PC, faz login manual se necessário, "
                "e cola a resposta na captura/importador. O God Mode não guarda passwords, tokens ou cookies."
            ),
            card_type="provider_browser_launch_capture",
            project_id=launch.get("project_hint", "GOD_MODE"),
            tenant_id=tenant_id,
            priority="high",
            requires_approval=False,
            actions=[{"action_id": "open-provider-manual", "label": "Abrir/manual", "decision": "acknowledge"}],
            source_ref={"type": "provider_browser_local_launcher", "launch_contract_id": launch_contract_id},
            metadata={"provider_id": launch.get("provider_id"), "safe_open_url": launch.get("safe_open_url"), "stores_credentials": False},
        )
        card = result.get("card")
        if card:
            self._store("attention_cards", card)
        return result

    def package_for_provider(self, provider_id: str, project_hint: str = "GOD_MODE", tenant_id: str = "owner-andre") -> Dict[str, Any]:
        launch = self.create_launch_contract(provider_id=provider_id, project_hint=project_hint, tenant_id=tenant_id)
        capture = self.create_capture_contract(
            launch_contract_id=launch["launch_contract"]["launch_contract_id"],
            title=f"{provider_id} captured answer",
            provider=provider_id,
            project_hint=project_hint,
            tenant_id=tenant_id,
        )
        card = self.create_attention_card(launch["launch_contract"]["launch_contract_id"], tenant_id=tenant_id)
        return {"ok": True, "mode": "provider_browser_launcher_package", "launch": launch, "capture": capture, "attention_card": card}

    def dashboard(self) -> Dict[str, Any]:
        state = LAUNCHER_STORE.load()
        return {
            "ok": True,
            "mode": "provider_browser_local_launcher_dashboard",
            "status": self.status(),
            "policy": self.policy(),
            "launch_contracts": state.get("launch_contracts", [])[-100:],
            "capture_contracts": state.get("capture_contracts", [])[-100:],
            "attention_cards": state.get("attention_cards", [])[-100:],
            "imports": state.get("imports", [])[-100:],
            "provider_urls": PROVIDER_URLS,
            "proof_link_status": provider_browser_proof_link_service.status(),
        }

    def package(self) -> Dict[str, Any]:
        return self.dashboard()

    def _command_hint(self, url: str) -> str:
        return f"start {url}" if url and url != "about:blank" else "manual open required"

    def _find(self, bucket: str, key: str, value: str) -> Dict[str, Any] | None:
        return next((item for item in LAUNCHER_STORE.load().get(bucket, []) if item.get(key) == value), None)

    def _store(self, bucket: str, item: Dict[str, Any]) -> None:
        def mutate(state: Dict[str, Any]) -> Dict[str, Any]:
            state.setdefault(bucket, []).append(item)
            state[bucket] = state.get(bucket, [])[-1000:]
            return state
        LAUNCHER_STORE.update(mutate)


provider_browser_local_launcher_service = ProviderBrowserLocalLauncherService()
