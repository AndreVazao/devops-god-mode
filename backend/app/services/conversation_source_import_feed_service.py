from __future__ import annotations

import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List
from uuid import uuid4

from app.services.conversation_requirement_ledger_service import conversation_requirement_ledger_service
from app.services.mobile_approval_cockpit_v2_service import mobile_approval_cockpit_v2_service
from app.services.real_work_fast_path_service import real_work_fast_path_service
from app.utils.atomic_json_store import AtomicJsonStore

DATA_DIR = Path("data")
IMPORT_FILE = DATA_DIR / "conversation_source_import_feed.json"
IMPORT_STORE = AtomicJsonStore(
    IMPORT_FILE,
    default_factory=lambda: {"version": 1, "imports": [], "work_map_links": [], "review_cards": []},
)

LABEL_RE = re.compile(r"(?im)^\s*(oner|andré|andre|user|utilizador|assistant|assistente|chatgpt|claude|gemini|praison|ruflo|ia|ai|provider)\s*:")


class ConversationSourceImportFeedService:
    """Import pasted/provider conversation sources into ledger + Real Work Map."""

    SERVICE_ID = "conversation_source_import_feed"
    VERSION = "phase_196_v1"

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def status(self) -> Dict[str, Any]:
        state = IMPORT_STORE.load()
        return {
            "ok": True,
            "service": self.SERVICE_ID,
            "version": self.VERSION,
            "generated_at": self._now(),
            "store_file": str(IMPORT_FILE),
            "import_count": len(state.get("imports", [])),
            "work_map_link_count": len(state.get("work_map_links", [])),
            "review_card_count": len(state.get("review_cards", [])),
            "separates_operator_and_ai": True,
            "feeds_requirement_ledger": True,
            "feeds_real_work_map": True,
            "stores_secrets": False,
        }

    def policy(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "policy": {
                "principle": "Operator requests are intent; AI responses are proposals until accepted/implemented/validated.",
                "accepted_sources": ["manual_paste", "provider_export", "chat_summary", "future_browser_capture"],
                "required_labels": ["Oner:", "User:", "Assistant:", "ChatGPT:", "Claude:", "Gemini:"],
                "fallback": "When labels are missing, import still works but creates review cards because separation is uncertain.",
                "blocked": ["store passwords", "store tokens", "store cookies", "treat AI response as decision", "silently discard old operator requests"],
            },
        }

    def import_text(
        self,
        transcript_text: str,
        provider: str = "manual_paste",
        project_hint: str = "GOD_MODE",
        title: str = "Imported conversation",
        source_ref: str | None = None,
        tenant_id: str = "owner-andre",
        create_review_card: bool = True,
    ) -> Dict[str, Any]:
        cleaned = self._sanitize_text(transcript_text)
        classification = real_work_fast_path_service.classify_text(f"{project_hint} {title} {cleaned[:800]}")
        project_group_id = classification.get("project_group_id") or "unclassified"
        project_group_label = classification.get("project_group_label") or "Unclassified"
        front = classification.get("front") or "unknown"
        labels_detected = bool(LABEL_RE.search(cleaned))
        ledger_project_key = project_group_id.upper() if project_group_id != "unclassified" else self._project_key(project_hint)
        ledger = conversation_requirement_ledger_service.analyze_text(
            project_key=ledger_project_key,
            transcript_text=cleaned,
            source_provider=provider,
            source_id=source_ref or title,
            store=True,
        )
        analysis = ledger.get("analysis", {})
        conv_link = real_work_fast_path_service.link_conversation(
            title=title,
            provider=provider,
            project_hint=f"{project_group_label} {front}",
            source_ref=source_ref or analysis.get("analysis_id") or "conversation_source_import",
            summary=self._summary(cleaned, analysis),
        ).get("conversation_link")
        import_item = {
            "import_id": f"conversation-import-{uuid4().hex[:12]}",
            "created_at": self._now(),
            "title": title[:220],
            "provider": provider[:80],
            "project_hint": project_hint[:220],
            "project_group_id": project_group_id,
            "project_group_label": project_group_label,
            "front": front,
            "source_ref": source_ref or analysis.get("analysis_id"),
            "labels_detected": labels_detected,
            "separation_confidence": "high" if labels_detected and analysis.get("operator_message_count", 0) > 0 and analysis.get("ai_message_count", 0) > 0 else "review_required",
            "ledger_analysis_id": analysis.get("analysis_id"),
            "request_count": analysis.get("request_count", 0),
            "decision_count": analysis.get("decision_count", 0),
            "script_count": analysis.get("script_count", 0),
            "realness_gap_count": analysis.get("realness_gap_count", 0),
            "conversation_link_id": conv_link.get("conversation_link_id") if conv_link else None,
            "stores_secrets": False,
        }
        self._store_import(import_item, conv_link)
        card_result = None
        if create_review_card and (import_item["separation_confidence"] != "high" or project_group_id == "unclassified"):
            card_result = self._create_review_card(import_item, tenant_id=tenant_id)
        return {"ok": True, "mode": "conversation_source_import", "import": import_item, "classification": classification, "ledger": ledger, "conversation_link": conv_link, "review_card": card_result}

    def import_messages(
        self,
        messages: List[Dict[str, Any]],
        provider: str = "manual_messages",
        project_hint: str = "GOD_MODE",
        title: str = "Imported message list",
        source_ref: str | None = None,
        tenant_id: str = "owner-andre",
    ) -> Dict[str, Any]:
        lines = []
        for message in messages:
            role = str(message.get("role") or message.get("speaker") or "unknown")
            speaker = "Oner" if role.lower() in {"operator", "user", "oner", "andre", "andré"} else "Assistant" if role.lower() in {"ai", "assistant", "chatgpt", "claude", "gemini"} else role
            content = str(message.get("content") or message.get("body") or "")
            lines.append(f"{speaker}: {content}")
        return self.import_text("\n".join(lines), provider=provider, project_hint=project_hint, title=title, source_ref=source_ref, tenant_id=tenant_id)

    def create_review_cards(self, tenant_id: str = "owner-andre") -> Dict[str, Any]:
        state = IMPORT_STORE.load()
        cards = []
        for item in state.get("imports", []):
            if item.get("separation_confidence") != "high" or item.get("project_group_id") == "unclassified":
                result = self._create_review_card(item, tenant_id=tenant_id)
                if result and result.get("card"):
                    cards.append(result["card"])
        return {"ok": True, "mode": "conversation_import_review_cards", "card_count": len(cards), "cards": cards}

    def dashboard(self) -> Dict[str, Any]:
        state = IMPORT_STORE.load()
        return {
            "ok": True,
            "mode": "conversation_source_import_dashboard",
            "status": self.status(),
            "policy": self.policy(),
            "imports": state.get("imports", [])[-200:],
            "work_map_links": state.get("work_map_links", [])[-200:],
            "review_cards": state.get("review_cards", [])[-100:],
        }

    def package(self) -> Dict[str, Any]:
        return self.dashboard()

    def _create_review_card(self, item: Dict[str, Any], tenant_id: str) -> Dict[str, Any]:
        result = mobile_approval_cockpit_v2_service.create_card(
            title=f"Rever conversa importada: {item.get('title')}",
            body=(
                f"Provider={item.get('provider')} grupo={item.get('project_group_label')} frente={item.get('front')} "
                f"confiança={item.get('separation_confidence')}. Confirma separação Oner vs IA e projeto antes de usar para execução."
            ),
            card_type="conversation_import_review",
            project_id=item.get("project_group_id") or "unclassified",
            tenant_id=tenant_id,
            priority="high" if item.get("separation_confidence") != "high" else "normal",
            requires_approval=False,
            actions=[{"action_id": "review-conversation", "label": "Rever conversa", "decision": "review"}],
            source_ref={"type": "conversation_source_import", "import_id": item.get("import_id"), "ledger_analysis_id": item.get("ledger_analysis_id")},
            metadata={"provider": item.get("provider"), "project_group_id": item.get("project_group_id"), "front": item.get("front"), "separation_confidence": item.get("separation_confidence")},
        )
        card = result.get("card")
        if card:
            self._store_cards([card])
        return result

    def _store_import(self, item: Dict[str, Any], link: Dict[str, Any] | None) -> None:
        def mutate(state: Dict[str, Any]) -> Dict[str, Any]:
            state.setdefault("imports", []).append(item)
            if link:
                state.setdefault("work_map_links", []).append(link)
            state["imports"] = state.get("imports", [])[-2000:]
            state["work_map_links"] = state.get("work_map_links", [])[-2000:]
            return state
        IMPORT_STORE.update(mutate)

    def _store_cards(self, cards: List[Dict[str, Any]]) -> None:
        def mutate(state: Dict[str, Any]) -> Dict[str, Any]:
            state.setdefault("review_cards", []).extend(cards)
            state["review_cards"] = state.get("review_cards", [])[-1000:]
            return state
        IMPORT_STORE.update(mutate)

    def _sanitize_text(self, text: str) -> str:
        # Avoid storing obvious secret assignment lines in imported text previews/ledger inputs.
        lines = []
        for line in (text or "").splitlines():
            lowered = line.lower()
            if any(key in lowered for key in ["api_key=", "token=", "password=", "cookie=", "secret="]):
                lines.append("[REDACTED_SECRET_LINE]")
            else:
                lines.append(line)
        return "\n".join(lines).strip()

    def _summary(self, text: str, analysis: Dict[str, Any]) -> str:
        return (
            f"Imported conversation. requests={analysis.get('request_count', 0)}, "
            f"decisions={analysis.get('decision_count', 0)}, scripts={analysis.get('script_count', 0)}. "
            f"Preview: {text[:360]}"
        )

    def _project_key(self, value: str) -> str:
        return re.sub(r"[^A-Za-z0-9_\-]+", "_", (value or "GOD_MODE").strip().upper()).strip("_") or "GOD_MODE"


conversation_source_import_feed_service = ConversationSourceImportFeedService()
