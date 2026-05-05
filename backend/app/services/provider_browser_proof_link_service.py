from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List
from uuid import uuid4

from app.services.mobile_approval_cockpit_v2_service import mobile_approval_cockpit_v2_service
from app.services.operator_approval_gate_service import operator_approval_gate_service
from app.services.provider_prompt_broadcast_runtime_service import provider_prompt_broadcast_runtime_service
from app.utils.atomic_json_store import AtomicJsonStore

DATA_DIR = Path("data")
PROOF_FILE = DATA_DIR / "provider_browser_proof_links.json"
PROOF_STORE = AtomicJsonStore(
    PROOF_FILE,
    default_factory=lambda: {"version": 1, "proof_links": [], "login_cards": [], "launch_gates": []},
)

PROVIDER_URLS = {
    "chatgpt": "https://chatgpt.com/",
    "claude": "https://claude.ai/",
    "gemini": "https://gemini.google.com/",
    "perplexity": "https://www.perplexity.ai/",
    "bing_copilot": "https://copilot.microsoft.com/",
    "openrouter": "https://openrouter.ai/",
    "local_ollama": "http://localhost:11434/",
    "local_webui": "http://localhost:7860/",
}


class ProviderBrowserProofLinkService:
    """Provider browser proof links and login attention cards.

    This phase prepares controlled local-open instructions and attention cards.
    It does not automate browser input and it never stores credentials/cookies.
    """

    SERVICE_ID = "provider_browser_proof_link"
    VERSION = "phase_192_v1"

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def status(self) -> Dict[str, Any]:
        state = PROOF_STORE.load()
        return {
            "ok": True,
            "service": self.SERVICE_ID,
            "version": self.VERSION,
            "generated_at": self._now(),
            "store_file": str(PROOF_FILE),
            "proof_link_count": len(state.get("proof_links", [])),
            "login_card_count": len(state.get("login_cards", [])),
            "launch_gate_count": len(state.get("launch_gates", [])),
            "browser_automation_enabled": False,
            "manual_open_enabled": True,
            "stores_credentials": False,
            "stores_cookies": False,
            "requires_gate_for_real_browser_automation": True,
        }

    def policy(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "policy": {
                "principle": "Provider pages may be opened locally for operator login/proof, but God Mode must not store credentials or automate sensitive browser input in this phase.",
                "allowed": ["build provider open links", "create login attention cards", "create future automation approval gate", "record proof status metadata"],
                "blocked": ["store credentials", "store cookies", "read passwords", "automate login", "send prompts automatically", "scrape private chats without operator-approved proof"],
                "future_gate_required_for": ["browser automation", "prompt send", "chat scrape", "file upload", "provider session reuse beyond manual proof"],
            },
        }

    def build_links_for_plan(self, plan_id: str, tenant_id: str = "owner-andre") -> Dict[str, Any]:
        plan = provider_prompt_broadcast_runtime_service._get_plan(plan_id)  # existing internal lookup; read-only use.
        if plan is None:
            return {"ok": False, "mode": "provider_browser_proof_links", "error": "plan_not_found", "plan_id": plan_id}
        links = []
        for job in plan.get("jobs", []):
            provider_id = job.get("provider_id")
            links.append(self._link_for_provider(plan, provider_id, job, tenant_id))
        self._store_links(links)
        return {"ok": True, "mode": "provider_browser_proof_links", "plan_id": plan_id, "link_count": len(links), "links": links}

    def create_login_attention_cards(self, plan_id: str, tenant_id: str = "owner-andre") -> Dict[str, Any]:
        links_result = self.build_links_for_plan(plan_id=plan_id, tenant_id=tenant_id)
        if not links_result.get("ok"):
            return links_result
        cards = []
        for link in links_result.get("links", []):
            if not link.get("requires_login_attention"):
                continue
            card_result = mobile_approval_cockpit_v2_service.create_card(
                title=f"Login/proof necessário: {link.get('provider_label')}",
                body=(
                    "Abre o provider no PC/local browser, confirma login manualmente e volta ao Broadcast Cockpit. "
                    "O God Mode não guarda password, cookies ou tokens. "
                    f"URL: {link.get('safe_open_url')}"
                ),
                card_type="provider_login_request",
                project_id=link.get("project_key", "GOD_MODE"),
                tenant_id=tenant_id,
                priority="high",
                requires_approval=False,
                actions=[{"action_id": "ack-login-needed", "label": "Ok, vou fazer login manual", "decision": "acknowledged"}],
                source_ref={"type": "provider_browser_proof_link", "proof_link_id": link.get("proof_link_id"), "plan_id": plan_id},
                metadata={"provider_id": link.get("provider_id"), "safe_open_url": link.get("safe_open_url"), "stores_credentials": False},
            )
            card = card_result.get("card")
            if card:
                cards.append(card)
        self._store_cards(cards)
        return {"ok": True, "mode": "provider_login_attention_cards", "plan_id": plan_id, "card_count": len(cards), "cards": cards}

    def create_browser_automation_gate(self, plan_id: str, provider_id: str, tenant_id: str = "owner-andre", purpose: str = "future browser proof automation") -> Dict[str, Any]:
        gate = operator_approval_gate_service.create_gate(
            tenant_id=tenant_id,
            thread_id="provider-browser-proof-link",
            action_label="Approve provider browser automation proof",
            action_scope="provider_browser_automation_proof",
            action_payload_summary=(
                f"Plan {plan_id}, provider {provider_id}, purpose={purpose}. "
                "This gate is for a future phase; Phase 192 still does not execute browser automation."
            ),
            risk_level="high",
        )
        item = {"gate_id": gate.get("gate", {}).get("gate_id"), "plan_id": plan_id, "provider_id": provider_id, "created_at": self._now(), "phase192_executes_automation": False}
        self._store_gate(item)
        return {"ok": True, "mode": "provider_browser_automation_gate", "gate": gate.get("gate"), "phase192_executes_automation": False}

    def dashboard(self, plan_id: str | None = None) -> Dict[str, Any]:
        state = PROOF_STORE.load()
        links = state.get("proof_links", [])
        cards = state.get("login_cards", [])
        if plan_id:
            links = [item for item in links if item.get("plan_id") == plan_id]
            cards = [item for item in cards if item.get("source_ref", {}).get("plan_id") == plan_id]
        return {
            "ok": True,
            "mode": "provider_browser_proof_dashboard",
            "plan_id": plan_id,
            "link_count": len(links),
            "login_card_count": len(cards),
            "links": links[-50:],
            "cards": cards[-50:],
            "browser_automation_enabled": False,
            "manual_open_enabled": True,
        }

    def package(self) -> Dict[str, Any]:
        return {"status": self.status(), "policy": self.policy(), "dashboard": self.dashboard(), "provider_urls": PROVIDER_URLS}

    def _link_for_provider(self, plan: Dict[str, Any], provider_id: str, job: Dict[str, Any], tenant_id: str) -> Dict[str, Any]:
        provider_id = provider_id or "unknown"
        return {
            "proof_link_id": f"proof-link-{uuid4().hex[:12]}",
            "plan_id": plan.get("plan_id"),
            "project_key": plan.get("project_key", "GOD_MODE"),
            "tenant_id": tenant_id,
            "provider_id": provider_id,
            "provider_label": job.get("provider_label") or provider_id,
            "provider_kind": job.get("provider_kind"),
            "safe_open_url": PROVIDER_URLS.get(provider_id, "about:blank"),
            "requires_login_attention": bool(job.get("requires_login_attention")) or job.get("provider_kind") in {"full_webapp", "local_webapp"},
            "browser_automation_enabled": False,
            "manual_open_instruction": "Open this URL locally, complete login manually if needed, then return to the cockpit and import the response manually.",
            "stores_credentials": False,
            "stores_cookies": False,
            "created_at": self._now(),
        }

    def _store_links(self, links: List[Dict[str, Any]]) -> None:
        def mutate(state: Dict[str, Any]) -> Dict[str, Any]:
            state.setdefault("proof_links", []).extend(links)
            state["proof_links"] = state["proof_links"][-1000:]
            return state
        PROOF_STORE.update(mutate)

    def _store_cards(self, cards: List[Dict[str, Any]]) -> None:
        def mutate(state: Dict[str, Any]) -> Dict[str, Any]:
            state.setdefault("login_cards", []).extend(cards)
            state["login_cards"] = state["login_cards"][-1000:]
            return state
        PROOF_STORE.update(mutate)

    def _store_gate(self, item: Dict[str, Any]) -> None:
        def mutate(state: Dict[str, Any]) -> Dict[str, Any]:
            state.setdefault("launch_gates", []).append(item)
            state["launch_gates"] = state["launch_gates"][-500:]
            return state
        PROOF_STORE.update(mutate)


provider_browser_proof_link_service = ProviderBrowserProofLinkService()
