from __future__ import annotations

import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List
from uuid import uuid4

from app.services.conversation_requirement_ledger_service import conversation_requirement_ledger_service
from app.utils.atomic_json_store import AtomicJsonStore

DATA_DIR = Path("data")
REVIEW_FILE = DATA_DIR / "conversation_ledger_cockpit_reviews.json"
REVIEW_STORE = AtomicJsonStore(
    REVIEW_FILE,
    default_factory=lambda: {"version": 1, "reviews": [], "operator_decisions": [], "card_snapshots": []},
)

VALID_DECISIONS = {"confirmed", "still_open", "migrated", "obsolete", "implemented", "rejected_ai_proposal"}
VALID_PRIORITIES = {"critical", "high", "normal", "low"}


class ConversationLedgerCockpitReviewService:
    """Mobile/PC cockpit cards for request-led requirement review."""

    SERVICE_ID = "conversation_ledger_cockpit_review"
    VERSION = "phase_188_v1"

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def status(self) -> Dict[str, Any]:
        state = REVIEW_STORE.load()
        ledger_status = conversation_requirement_ledger_service.status()
        return {
            "ok": True,
            "service": self.SERVICE_ID,
            "version": self.VERSION,
            "generated_at": self._now(),
            "review_file": str(REVIEW_FILE),
            "review_count": len(state.get("reviews", [])),
            "operator_decision_count": len(state.get("operator_decisions", [])),
            "card_snapshot_count": len(state.get("card_snapshots", [])),
            "ledger_request_count": ledger_status.get("request_count", 0),
            "mobile_cockpit_ready": True,
            "operator_can_mark_requirements": True,
            "request_led_review": True,
        }

    def policy(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "policy": {
                "principle": "Open requirements must be visible to the operator as cockpit cards before they are forgotten or silently overwritten by later AI answers.",
                "card_statuses": sorted(VALID_DECISIONS),
                "operator_actions": ["confirm", "keep_open", "mark_migrated", "mark_obsolete", "mark_implemented", "reject_ai_proposal"],
                "realness_rule": "Implemented/confirmed cards should still prefer real evidence: endpoint, code, PR, merge, CI/build or local proof.",
                "blocked": ["silently close an operator request", "mark AI proposal as accepted without operator review", "hide migration history"],
            },
        }

    def build_cards(self, project_key: str = "GOD_MODE", include_closed: bool = False) -> Dict[str, Any]:
        project = self._safe_project(project_key)
        compare = conversation_requirement_ledger_service.compare_project(project)["report"]
        open_requirements = conversation_requirement_ledger_service.list_open_requirements(project).get("open_requirements", [])
        scorecard = conversation_requirement_ledger_service.realness_scorecard(project)
        reviews_by_request = self._reviews_by_request(project)
        cards: List[Dict[str, Any]] = []

        for req in open_requirements:
            review = reviews_by_request.get(req.get("request_id"))
            if review and not include_closed and review.get("decision") in {"confirmed", "migrated", "obsolete", "implemented", "rejected_ai_proposal"}:
                continue
            cards.append(self._card_from_requirement(req, review, compare))

        # Include partial requirements as attention cards even if not open.
        for req in compare.get("partial_requirements", []):
            review = reviews_by_request.get(req.get("request_id"))
            if review and not include_closed and review.get("decision") in {"confirmed", "migrated", "obsolete", "implemented", "rejected_ai_proposal"}:
                continue
            card = self._card_from_requirement(req, review, compare)
            card["card_type"] = "partial_requirement_review"
            card["attention_reason"] = "partial_match_needs_operator_confirmation"
            cards.append(card)

        cards = self._dedupe_cards(cards)
        snapshot = {
            "snapshot_id": f"ledger-cards-{uuid4().hex[:12]}",
            "project_key": project,
            "created_at": self._now(),
            "card_count": len(cards),
            "realness_score": scorecard.get("realness_score"),
            "cards": cards,
            "summary": self._summary(cards, scorecard),
        }
        self._store_snapshot(snapshot)
        return {"ok": True, "mode": "conversation_ledger_cockpit_cards", "snapshot": snapshot}

    def review_requirement(
        self,
        request_id: str,
        decision: str,
        project_key: str = "GOD_MODE",
        operator_note: str | None = None,
        evidence_ref: str | None = None,
        migration_note: str | None = None,
        priority: str | None = None,
    ) -> Dict[str, Any]:
        decision_clean = decision.strip().lower()
        if decision_clean not in VALID_DECISIONS:
            return {"ok": False, "mode": "conversation_ledger_review", "error": "invalid_decision", "valid_decisions": sorted(VALID_DECISIONS)}
        if priority and priority not in VALID_PRIORITIES:
            return {"ok": False, "mode": "conversation_ledger_review", "error": "invalid_priority", "valid_priorities": sorted(VALID_PRIORITIES)}
        project = self._safe_project(project_key)
        req = self._find_request(project, request_id)
        if req is None:
            return {"ok": False, "mode": "conversation_ledger_review", "error": "request_not_found", "request_id": request_id, "project_key": project}

        review = {
            "review_id": f"review-{uuid4().hex[:12]}",
            "request_id": request_id,
            "project_key": project,
            "decision": decision_clean,
            "operator_note": (operator_note or "")[:1200],
            "evidence_ref": (evidence_ref or "")[:500],
            "migration_note": (migration_note or "")[:1200],
            "priority": priority or req.get("priority", "normal"),
            "request_text_preview": req.get("request_text", "")[:500],
            "created_at": self._now(),
            "requires_follow_up": decision_clean in {"still_open", "migrated"} and not evidence_ref,
            "realness_status": "real_evidence_linked" if evidence_ref else "operator_review_only",
        }

        def mutate(state: Dict[str, Any]) -> Dict[str, Any]:
            reviews = [item for item in state.get("reviews", []) if item.get("request_id") != request_id]
            reviews.append(review)
            state["reviews"] = reviews[-1000:]
            state.setdefault("operator_decisions", []).append(review)
            state["operator_decisions"] = state["operator_decisions"][-1000:]
            return state

        REVIEW_STORE.update(mutate)
        return {"ok": True, "mode": "conversation_ledger_review", "review": review}

    def batch_review(self, project_key: str, reviews: List[Dict[str, Any]]) -> Dict[str, Any]:
        results = []
        for item in reviews:
            results.append(
                self.review_requirement(
                    project_key=project_key,
                    request_id=str(item.get("request_id") or ""),
                    decision=str(item.get("decision") or "still_open"),
                    operator_note=item.get("operator_note"),
                    evidence_ref=item.get("evidence_ref"),
                    migration_note=item.get("migration_note"),
                    priority=item.get("priority"),
                )
            )
        return {"ok": True, "mode": "conversation_ledger_batch_review", "result_count": len(results), "results": results}

    def review_history(self, project_key: str | None = None, limit: int = 50) -> Dict[str, Any]:
        state = REVIEW_STORE.load()
        project = self._safe_project(project_key) if project_key else None
        reviews = list(reversed(state.get("reviews", [])))
        if project:
            reviews = [item for item in reviews if item.get("project_key") == project]
        reviews = reviews[0:max(1, min(limit, 200))]
        return {"ok": True, "mode": "conversation_ledger_review_history", "review_count": len(reviews), "reviews": reviews}

    def summary(self, project_key: str = "GOD_MODE") -> Dict[str, Any]:
        cards = self.build_cards(project_key=project_key, include_closed=False)["snapshot"]
        history = self.review_history(project_key=project_key, limit=200)
        counts: Dict[str, int] = {decision: 0 for decision in sorted(VALID_DECISIONS)}
        for review in history.get("reviews", []):
            decision = review.get("decision")
            if decision in counts:
                counts[decision] += 1
        return {
            "ok": True,
            "mode": "conversation_ledger_review_summary",
            "project_key": self._safe_project(project_key),
            "open_card_count": cards.get("card_count", 0),
            "decision_counts": counts,
            "realness_score": cards.get("realness_score"),
            "next_actions": cards.get("summary", {}).get("next_actions", []),
        }

    def package(self, project_key: str = "GOD_MODE") -> Dict[str, Any]:
        return {
            "status": self.status(),
            "policy": self.policy(),
            "cards": self.build_cards(project_key=project_key, include_closed=False),
            "summary": self.summary(project_key=project_key),
            "history": self.review_history(project_key=project_key, limit=20),
            "routes": {
                "cards": "/api/conversation-ledger-cockpit-review/cards",
                "review": "/api/conversation-ledger-cockpit-review/review",
                "batch_review": "/api/conversation-ledger-cockpit-review/batch-review",
                "summary": "/api/conversation-ledger-cockpit-review/summary",
                "history": "/api/conversation-ledger-cockpit-review/history",
            },
        }

    def _card_from_requirement(self, req: Dict[str, Any], review: Dict[str, Any] | None, compare: Dict[str, Any]) -> Dict[str, Any]:
        request_id = req.get("request_id")
        realness_gaps = [gap for gap in compare.get("realness_gaps", []) if gap.get("request_id") == request_id]
        links = [link for link in compare.get("links", []) if link.get("request_id") == request_id]
        card = {
            "card_id": f"ledger-card-{request_id}",
            "card_type": "open_requirement_review",
            "request_id": request_id,
            "project_key": req.get("project_key"),
            "priority": req.get("priority", "normal"),
            "themes": req.get("themes", []),
            "title": self._title(req.get("request_text", "")),
            "request_text": req.get("request_text"),
            "status": review.get("decision") if review else "needs_operator_review",
            "review": review,
            "linked_decisions": links,
            "realness_gaps": realness_gaps,
            "recommended_actions": self._recommended_actions(req, links, realness_gaps, review),
            "mobile_actions": [
                {"id": "confirm", "label": "Confirmar", "decision": "confirmed"},
                {"id": "keep_open", "label": "Manter aberto", "decision": "still_open"},
                {"id": "mark_migrated", "label": "Migrado", "decision": "migrated"},
                {"id": "mark_obsolete", "label": "Obsoleto", "decision": "obsolete"},
                {"id": "mark_implemented", "label": "Implementado", "decision": "implemented"},
                {"id": "reject_ai_proposal", "label": "Rejeitar proposta IA", "decision": "rejected_ai_proposal"},
            ],
            "requires_evidence_for_real": True,
        }
        return card

    def _recommended_actions(self, req: Dict[str, Any], links: List[Dict[str, Any]], gaps: List[Dict[str, Any]], review: Dict[str, Any] | None) -> List[str]:
        if review and review.get("decision") == "implemented" and review.get("evidence_ref"):
            return ["No immediate action: operator marked implemented with evidence."]
        actions = []
        if not links:
            actions.append("Link this request to a decision or implementation plan.")
        if gaps:
            actions.append("Attach real evidence: endpoint, PR, merge, CI/build or local runtime proof.")
        if "cloud_to_pc_migration" in req.get("themes", []):
            actions.append("Confirm whether old cloud requirement was migrated to PC/local or remains open.")
        if not actions:
            actions.append("Operator should confirm whether current implementation matches the original request.")
        return actions

    def _summary(self, cards: List[Dict[str, Any]], scorecard: Dict[str, Any]) -> Dict[str, Any]:
        critical = [card for card in cards if card.get("priority") == "critical"]
        return {
            "card_count": len(cards),
            "critical_count": len(critical),
            "realness_score": scorecard.get("realness_score"),
            "next_actions": [
                "Review critical open cards first." if critical else "No critical open cards in current snapshot.",
                "Attach evidence before marking features real.",
                "Use migrated/obsolete only with an operator note when architecture changed.",
            ],
        }

    def _store_snapshot(self, snapshot: Dict[str, Any]) -> None:
        def mutate(state: Dict[str, Any]) -> Dict[str, Any]:
            state.setdefault("card_snapshots", []).append(snapshot)
            state["card_snapshots"] = state["card_snapshots"][-200:]
            return state
        REVIEW_STORE.update(mutate)

    def _reviews_by_request(self, project_key: str) -> Dict[str, Dict[str, Any]]:
        state = REVIEW_STORE.load()
        result = {}
        for review in state.get("reviews", []):
            if review.get("project_key") == project_key:
                result[review.get("request_id")] = review
        return result

    def _find_request(self, project_key: str, request_id: str) -> Dict[str, Any] | None:
        open_items = conversation_requirement_ledger_service.list_open_requirements(project_key).get("open_requirements", [])
        compare = conversation_requirement_ledger_service.compare_project(project_key).get("report", {})
        candidates = open_items + compare.get("partial_requirements", [])
        return next((item for item in candidates if item.get("request_id") == request_id), None)

    def _dedupe_cards(self, cards: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        result: Dict[str, Dict[str, Any]] = {}
        for card in cards:
            result[card.get("request_id")] = card
        return list(result.values())

    def _title(self, text: str) -> str:
        compact = re.sub(r"\s+", " ", text or "").strip()
        return compact[:90] + ("..." if len(compact) > 90 else "")

    def _safe_project(self, project_key: str | None) -> str:
        return re.sub(r"[^A-Za-z0-9_\-]+", "_", (project_key or "GOD_MODE").strip().upper()).strip("_") or "GOD_MODE"


conversation_ledger_cockpit_review_service = ConversationLedgerCockpitReviewService()
