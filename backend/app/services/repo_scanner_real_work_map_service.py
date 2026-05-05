from __future__ import annotations

import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List
from uuid import uuid4

from app.services.mobile_approval_cockpit_v2_service import mobile_approval_cockpit_v2_service
from app.services.real_work_fast_path_service import real_work_fast_path_service
from app.utils.atomic_json_store import AtomicJsonStore

DATA_DIR = Path("data")
SCAN_FILE = DATA_DIR / "repo_scanner_real_work_map.json"
SCAN_STORE = AtomicJsonStore(
    SCAN_FILE,
    default_factory=lambda: {"version": 1, "scans": [], "suggestions": [], "review_cards": [], "applied_links": []},
)

DEFAULT_REPOS = [
    "AndreVazao/devops-god-mode",
    "AndreVazao/andreos-memory",
    "AndreVazao/godmode-ruflo-lab",
    "AndreVazao/godmode-praison-lab",
    "AndreVazao/godmode-smol-ai-lab",
]


class RepoScannerRealWorkMapService:
    """Suggest repo -> project group/front links for the Real Work Map."""

    SERVICE_ID = "repo_scanner_real_work_map"
    VERSION = "phase_194_v1"

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def status(self) -> Dict[str, Any]:
        state = SCAN_STORE.load()
        return {
            "ok": True,
            "service": self.SERVICE_ID,
            "version": self.VERSION,
            "generated_at": self._now(),
            "store_file": str(SCAN_FILE),
            "scan_count": len(state.get("scans", [])),
            "suggestion_count": len(state.get("suggestions", [])),
            "review_card_count": len(state.get("review_cards", [])),
            "applied_link_count": len(state.get("applied_links", [])),
            "auto_destructive_actions": False,
            "review_required_for_low_confidence": True,
        }

    def policy(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "policy": {
                "principle": "Repo scanning suggests links; it does not silently merge or modify project ownership.",
                "allowed": ["scan repo names", "classify group/front", "suggest website/studio pairs", "apply high-confidence links", "create review cards"],
                "blocked": ["delete repos", "merge repos", "change repo settings", "store secrets", "apply low-confidence link without operator review"],
                "high_confidence_threshold": "high",
                "review_confidences": ["medium", "low"],
            },
        }

    def scan_repos(self, repo_full_names: List[str] | None = None, tenant_id: str = "owner-andre", auto_apply_high_confidence: bool = False) -> Dict[str, Any]:
        repos = self._clean_repos(repo_full_names or DEFAULT_REPOS)
        suggestions = [self._suggest_for_repo(repo) for repo in repos]
        pairs = self._detect_pairs(suggestions)
        scan = {
            "scan_id": f"repo-scan-{uuid4().hex[:12]}",
            "created_at": self._now(),
            "repo_count": len(repos),
            "suggestion_count": len(suggestions),
            "pair_count": len(pairs),
            "auto_apply_high_confidence": auto_apply_high_confidence,
            "tenant_id": tenant_id,
        }
        self._store_scan(scan, suggestions, pairs)
        applied = []
        if auto_apply_high_confidence:
            for suggestion in suggestions:
                if suggestion.get("confidence") == "high":
                    applied.append(self.apply_suggestion(suggestion["suggestion_id"], tenant_id=tenant_id).get("repo_link"))
        cards = self.create_review_cards(scan_id=scan["scan_id"], tenant_id=tenant_id)
        return {"ok": True, "mode": "repo_scan_real_work_map", "scan": scan, "suggestions": suggestions, "pairs": pairs, "applied_high_confidence": [x for x in applied if x], "review_cards": cards}

    def suggest_repo(self, repo_full_name: str) -> Dict[str, Any]:
        suggestion = self._suggest_for_repo(repo_full_name)
        self._store_suggestions([suggestion])
        return {"ok": True, "mode": "repo_scan_single_suggestion", "suggestion": suggestion}

    def apply_suggestion(self, suggestion_id: str, tenant_id: str = "owner-andre") -> Dict[str, Any]:
        suggestion = self._find_suggestion(suggestion_id)
        if suggestion is None:
            return {"ok": False, "mode": "repo_scan_apply_suggestion", "error": "suggestion_not_found", "suggestion_id": suggestion_id}
        if suggestion.get("confidence") != "high":
            return {"ok": False, "mode": "repo_scan_apply_suggestion", "error": "operator_review_required", "suggestion": suggestion}
        repo_link = real_work_fast_path_service.link_repo(
            repo_full_name=suggestion["repo_full_name"],
            project_hint=suggestion.get("project_group_label") or suggestion.get("repo_name"),
            front=suggestion.get("front"),
            evidence=f"repo_scanner_suggestion:{suggestion_id}",
        ).get("repo_link")
        applied = {"applied_link_id": f"applied-repo-link-{uuid4().hex[:12]}", "suggestion_id": suggestion_id, "tenant_id": tenant_id, "repo_link": repo_link, "created_at": self._now()}
        self._store_applied(applied)
        return {"ok": True, "mode": "repo_scan_apply_suggestion", "repo_link": repo_link, "applied": applied}

    def create_review_cards(self, scan_id: str | None = None, tenant_id: str = "owner-andre") -> Dict[str, Any]:
        state = SCAN_STORE.load()
        suggestions = state.get("suggestions", [])
        if scan_id:
            suggestions = [item for item in suggestions if item.get("scan_id") == scan_id]
        reviewable = [item for item in suggestions if item.get("confidence") in {"medium", "low"} or item.get("needs_operator_review")]
        cards = []
        for suggestion in reviewable:
            result = mobile_approval_cockpit_v2_service.create_card(
                title=f"Confirmar repo: {suggestion.get('repo_full_name')}",
                body=(
                    f"Sugestão: grupo={suggestion.get('project_group_label')} / frente={suggestion.get('front')} / confiança={suggestion.get('confidence')}. "
                    "Confirma antes de ligar ao Real Work Map."
                ),
                card_type="repo_link_review",
                project_id=suggestion.get("project_group_id", "unclassified"),
                tenant_id=tenant_id,
                priority="normal" if suggestion.get("confidence") == "medium" else "high",
                requires_approval=False,
                actions=[{"action_id": "confirm-repo-link", "label": "Confirmar ligação", "decision": "confirm"}, {"action_id": "reject-repo-link", "label": "Rejeitar", "decision": "reject"}],
                source_ref={"type": "repo_scanner_suggestion", "suggestion_id": suggestion.get("suggestion_id"), "scan_id": suggestion.get("scan_id")},
                metadata={"repo_full_name": suggestion.get("repo_full_name"), "front": suggestion.get("front"), "confidence": suggestion.get("confidence")},
            )
            card = result.get("card")
            if card:
                cards.append(card)
        self._store_cards(cards)
        return {"ok": True, "mode": "repo_scan_review_cards", "scan_id": scan_id, "card_count": len(cards), "cards": cards}

    def dashboard(self) -> Dict[str, Any]:
        state = SCAN_STORE.load()
        return {
            "ok": True,
            "mode": "repo_scanner_real_work_map_dashboard",
            "status": self.status(),
            "policy": self.policy(),
            "recent_scans": state.get("scans", [])[-20:],
            "suggestions": state.get("suggestions", [])[-200:],
            "review_cards": state.get("review_cards", [])[-100:],
            "applied_links": state.get("applied_links", [])[-100:],
            "default_repos": DEFAULT_REPOS,
        }

    def package(self) -> Dict[str, Any]:
        return self.dashboard()

    def _suggest_for_repo(self, repo_full_name: str) -> Dict[str, Any]:
        owner, repo_name = self._split_repo(repo_full_name)
        text = f"{repo_full_name} {repo_name.replace('-', ' ').replace('_', ' ')}"
        classification = real_work_fast_path_service.classify_text(text)
        project_group_id = classification.get("project_group_id")
        front = classification.get("front")
        confidence = classification.get("confidence")
        # Known lab/core patterns increase confidence.
        n = text.lower()
        reasons = []
        if "godmode" in n or "god-mode" in n or "andreos" in n:
            project_group_id = "god_mode"
            front = "labs" if "lab" in n else front if front != "unknown" else "backend"
            confidence = "high"
            reasons.append("godmode/andreos naming")
        if any(x in n for x in ["baribudos", "barbudo", "very beach", "beybus"]):
            project_group_id = "baribudos_platform"
            if front == "unknown":
                front = "studio" if "studio" in n else "website" if any(x in n for x in ["website", "web", "site"]) else "unknown"
            confidence = "high" if front != "unknown" else "medium"
            reasons.append("baribudos alias")
        if "proventil" in n:
            project_group_id = "proventil"
            confidence = "high"
            reasons.append("proventil naming")
        label_map = {"god_mode": "DevOps God Mode", "baribudos_platform": "Baribudos Platform", "proventil": "ProVentil", "unclassified": "Unclassified"}
        suggestion = {
            "suggestion_id": f"repo-suggestion-{uuid4().hex[:12]}",
            "created_at": self._now(),
            "scan_id": None,
            "repo_full_name": repo_full_name,
            "owner": owner,
            "repo_name": repo_name,
            "project_group_id": project_group_id,
            "project_group_label": label_map.get(project_group_id, project_group_id),
            "front": front,
            "confidence": confidence,
            "needs_operator_review": confidence != "high" or front == "unknown",
            "reasons": reasons or ["real_work_fast_path_classification"],
            "safe_to_auto_apply": confidence == "high" and front != "unknown",
        }
        return suggestion

    def _detect_pairs(self, suggestions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        pairs = []
        by_group: Dict[str, List[Dict[str, Any]]] = {}
        for item in suggestions:
            by_group.setdefault(item.get("project_group_id", "unclassified"), []).append(item)
        for group_id, items in by_group.items():
            fronts = {item.get("front") for item in items}
            if "website" in fronts and "studio" in fronts:
                pairs.append({"pair_id": f"repo-pair-{uuid4().hex[:12]}", "project_group_id": group_id, "pair_type": "website_studio", "repos": [item["repo_full_name"] for item in items if item.get("front") in {"website", "studio"}], "created_at": self._now(), "needs_operator_confirmation": False})
        return pairs

    def _clean_repos(self, repos: List[str]) -> List[str]:
        cleaned = []
        for repo in repos:
            repo = (repo or "").strip()
            if not repo or "/" not in repo:
                continue
            if repo not in cleaned:
                cleaned.append(repo)
        return cleaned[:500]

    def _split_repo(self, repo_full_name: str) -> tuple[str, str]:
        parts = repo_full_name.split("/", 1)
        return (parts[0], parts[1]) if len(parts) == 2 else ("unknown", repo_full_name)

    def _store_scan(self, scan: Dict[str, Any], suggestions: List[Dict[str, Any]], pairs: List[Dict[str, Any]]) -> None:
        for suggestion in suggestions:
            suggestion["scan_id"] = scan["scan_id"]
        scan["pairs"] = pairs
        def mutate(state: Dict[str, Any]) -> Dict[str, Any]:
            state.setdefault("scans", []).append(scan)
            state.setdefault("suggestions", []).extend(suggestions)
            state["scans"] = state["scans"][-300:]
            state["suggestions"] = state["suggestions"][-3000:]
            return state
        SCAN_STORE.update(mutate)

    def _store_suggestions(self, suggestions: List[Dict[str, Any]]) -> None:
        def mutate(state: Dict[str, Any]) -> Dict[str, Any]:
            state.setdefault("suggestions", []).extend(suggestions)
            state["suggestions"] = state["suggestions"][-3000:]
            return state
        SCAN_STORE.update(mutate)

    def _find_suggestion(self, suggestion_id: str) -> Dict[str, Any] | None:
        return next((item for item in SCAN_STORE.load().get("suggestions", []) if item.get("suggestion_id") == suggestion_id), None)

    def _store_cards(self, cards: List[Dict[str, Any]]) -> None:
        def mutate(state: Dict[str, Any]) -> Dict[str, Any]:
            state.setdefault("review_cards", []).extend(cards)
            state["review_cards"] = state["review_cards"][-1000:]
            return state
        SCAN_STORE.update(mutate)

    def _store_applied(self, item: Dict[str, Any]) -> None:
        def mutate(state: Dict[str, Any]) -> Dict[str, Any]:
            state.setdefault("applied_links", []).append(item)
            state["applied_links"] = state["applied_links"][-1000:]
            return state
        SCAN_STORE.update(mutate)


repo_scanner_real_work_map_service = RepoScannerRealWorkMapService()
