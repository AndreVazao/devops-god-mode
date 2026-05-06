from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List
from uuid import uuid4

from app.services.mobile_approval_cockpit_v2_service import mobile_approval_cockpit_v2_service
from app.services.repo_scanner_real_work_map_service import repo_scanner_real_work_map_service
from app.utils.atomic_json_store import AtomicJsonStore

DATA_DIR = Path("data")
INVENTORY_FILE = DATA_DIR / "github_repo_inventory_feed.json"
INVENTORY_STORE = AtomicJsonStore(
    INVENTORY_FILE,
    default_factory=lambda: {"version": 1, "snapshots": [], "repo_inventory": [], "scanner_feeds": [], "new_repo_cards": []},
)

CONNECTOR_SEED_REPOS = [
    "AndreVazao/universal-build-platform",
    "AndreVazao/build-control-panel",
    "AndreVazao/Bot_Factory",
    "AndreVazao/build-control-center",
    "AndreVazao/Project-Organizer-AI",
    "AndreVazao/proventil",
    "AndreVazao/SheetProPrivate",
    "AndreVazao/baribudos-studio-primary",
    "AndreVazao/baribudos-studio-home-edition",
    "AndreVazao/baribudos-studio",
    "AndreVazao/baribudos-studio-website",
    "AndreVazao/GitHub-auto-builder",
    "AndreVazao/ai-devops-control-center",
    "AndreVazao/ecu-pro-tune",
    "AndreVazao/script-reviewer-mobile",
    "AndreVazao/devops-god-mode",
    "AndreVazao/Vortexa-core",
    "AndreVazao/ENV-editor",
    "AndreVazao/andreos-memory",
    "AndreVazao/godmode-ruflo-lab",
    "AndreVazao/godmode-praison-lab",
    "AndreVazao/VazaoSovereignTrader",
    "AndreVazao/godmode-smol-ai-lab",
]


class GithubRepoInventoryFeedService:
    """Persist GitHub connector repo inventory and feed the Real Work scanner."""

    SERVICE_ID = "github_repo_inventory_feed"
    VERSION = "phase_195_v1"

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def status(self) -> Dict[str, Any]:
        state = INVENTORY_STORE.load()
        return {
            "ok": True,
            "service": self.SERVICE_ID,
            "version": self.VERSION,
            "generated_at": self._now(),
            "store_file": str(INVENTORY_FILE),
            "snapshot_count": len(state.get("snapshots", [])),
            "repo_inventory_count": len(state.get("repo_inventory", [])),
            "scanner_feed_count": len(state.get("scanner_feeds", [])),
            "new_repo_card_count": len(state.get("new_repo_cards", [])),
            "connector_runtime_inside_backend": False,
            "supports_external_connector_snapshot": True,
            "supports_manual_paste_fallback": True,
            "destructive_actions": False,
        }

    def policy(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "policy": {
                "principle": "The GitHub connector/API can provide repo inventory outside the backend; God Mode stores a sanitized snapshot and feeds the scanner.",
                "allowed": ["store repo names", "store repo metadata", "feed scanner", "create review cards", "apply high-confidence map links"],
                "blocked": ["store secrets", "clone repos automatically", "delete repos", "change repo settings", "merge repos"],
                "fallback": "If connector access is unavailable inside runtime, paste repo names into /app/github-repo-inventory-feed.",
            },
        }

    def import_connector_snapshot(self, repositories: List[Dict[str, Any]], source: str = "github_connector", tenant_id: str = "owner-andre", feed_scanner: bool = True, auto_apply_high_confidence: bool = False) -> Dict[str, Any]:
        sanitized = [self._sanitize_repo(item) for item in repositories if self._sanitize_repo(item).get("repository_full_name")]
        snapshot = {
            "snapshot_id": f"repo-inventory-snapshot-{uuid4().hex[:12]}",
            "source": source,
            "tenant_id": tenant_id,
            "created_at": self._now(),
            "repo_count": len(sanitized),
            "feed_scanner": feed_scanner,
            "auto_apply_high_confidence": auto_apply_high_confidence,
        }
        self._store_snapshot(snapshot, sanitized)
        scanner_result = None
        if feed_scanner:
            scanner_result = repo_scanner_real_work_map_service.scan_repos(
                repo_full_names=[item["repository_full_name"] for item in sanitized],
                tenant_id=tenant_id,
                auto_apply_high_confidence=auto_apply_high_confidence,
            )
            self._store_scanner_feed(snapshot, scanner_result)
        cards = self.create_new_repo_cards(snapshot_id=snapshot["snapshot_id"], tenant_id=tenant_id)
        return {"ok": True, "mode": "github_repo_inventory_import", "snapshot": snapshot, "repositories": sanitized, "scanner_result": scanner_result, "new_repo_cards": cards}

    def import_repo_names(self, repo_full_names: List[str], source: str = "manual_paste", tenant_id: str = "owner-andre", feed_scanner: bool = True, auto_apply_high_confidence: bool = False) -> Dict[str, Any]:
        repos = [{"repository_full_name": name.strip(), "name": name.strip().split("/")[-1], "owner": name.strip().split("/")[0] if "/" in name else "unknown", "visibility": "unknown", "default_branch": "unknown", "archived": False} for name in repo_full_names if name and "/" in name]
        return self.import_connector_snapshot(repositories=repos, source=source, tenant_id=tenant_id, feed_scanner=feed_scanner, auto_apply_high_confidence=auto_apply_high_confidence)

    def seed_from_connector_sample(self, tenant_id: str = "owner-andre", feed_scanner: bool = True, auto_apply_high_confidence: bool = True) -> Dict[str, Any]:
        repos = [{"repository_full_name": full_name, "name": full_name.split("/", 1)[1], "owner": full_name.split("/", 1)[0], "visibility": "connector_seen", "default_branch": "main", "archived": False} for full_name in CONNECTOR_SEED_REPOS]
        return self.import_connector_snapshot(repositories=repos, source="phase195_connector_seen_seed", tenant_id=tenant_id, feed_scanner=feed_scanner, auto_apply_high_confidence=auto_apply_high_confidence)

    def create_new_repo_cards(self, snapshot_id: str | None = None, tenant_id: str = "owner-andre") -> Dict[str, Any]:
        state = INVENTORY_STORE.load()
        inventory = state.get("repo_inventory", [])
        if snapshot_id:
            inventory = [item for item in inventory if item.get("snapshot_id") == snapshot_id]
        cards = []
        for repo in inventory:
            if repo.get("classification_hint") in {"unknown", "unclassified"}:
                result = mobile_approval_cockpit_v2_service.create_card(
                    title=f"Repo novo/desconhecido: {repo.get('repository_full_name')}",
                    body="Confirma a que projeto/grupo pertence este repo antes de deixar o God Mode trabalhar nele automaticamente.",
                    card_type="repo_inventory_review",
                    project_id="unclassified",
                    tenant_id=tenant_id,
                    priority="normal",
                    requires_approval=False,
                    actions=[{"action_id": "classify-repo", "label": "Classificar repo", "decision": "review"}],
                    source_ref={"type": "github_repo_inventory", "snapshot_id": repo.get("snapshot_id"), "repo": repo.get("repository_full_name")},
                    metadata={"repository_full_name": repo.get("repository_full_name"), "visibility": repo.get("visibility"), "archived": repo.get("archived")},
                )
                card = result.get("card")
                if card:
                    cards.append(card)
        self._store_cards(cards)
        return {"ok": True, "mode": "github_repo_inventory_review_cards", "snapshot_id": snapshot_id, "card_count": len(cards), "cards": cards}

    def dashboard(self) -> Dict[str, Any]:
        state = INVENTORY_STORE.load()
        return {
            "ok": True,
            "mode": "github_repo_inventory_dashboard",
            "status": self.status(),
            "policy": self.policy(),
            "recent_snapshots": state.get("snapshots", [])[-20:],
            "repo_inventory": state.get("repo_inventory", [])[-300:],
            "scanner_feeds": state.get("scanner_feeds", [])[-50:],
            "new_repo_cards": state.get("new_repo_cards", [])[-100:],
            "connector_seen_seed_count": len(CONNECTOR_SEED_REPOS),
        }

    def package(self) -> Dict[str, Any]:
        return self.dashboard()

    def _sanitize_repo(self, item: Dict[str, Any]) -> Dict[str, Any]:
        full_name = item.get("repository_full_name") or item.get("full_name") or item.get("display_title") or ""
        full_name = str(full_name).strip()
        if "/" not in full_name:
            return {}
        owner, name = full_name.split("/", 1)
        return {
            "repo_inventory_id": f"repo-inventory-{uuid4().hex[:12]}",
            "repository_full_name": full_name,
            "owner": owner,
            "name": str(item.get("name") or name),
            "visibility": str(item.get("visibility") or "unknown"),
            "default_branch": str(item.get("default_branch") or "unknown"),
            "archived": bool(item.get("archived", False)),
            "size": item.get("size"),
            "permissions": self._sanitize_permissions(item.get("permissions") or {}),
            "display_url": item.get("display_url"),
            "classification_hint": self._classification_hint(full_name),
            "created_at": self._now(),
        }

    def _sanitize_permissions(self, permissions: Dict[str, Any]) -> Dict[str, bool]:
        return {key: bool(permissions.get(key, False)) for key in ["admin", "maintain", "push", "pull", "triage"]}

    def _classification_hint(self, full_name: str) -> str:
        text = full_name.lower()
        if "baribudos" in text or "barbudo" in text:
            return "baribudos_platform"
        if "godmode" in text or "god-mode" in text or "andreos" in text or "devops-god-mode" in text:
            return "god_mode"
        if "proventil" in text:
            return "proventil"
        if "build" in text or "github-auto" in text or "devops" in text:
            return "devops_tools"
        return "unknown"

    def _store_snapshot(self, snapshot: Dict[str, Any], repos: List[Dict[str, Any]]) -> None:
        for repo in repos:
            repo["snapshot_id"] = snapshot["snapshot_id"]
        def mutate(state: Dict[str, Any]) -> Dict[str, Any]:
            state.setdefault("snapshots", []).append(snapshot)
            state.setdefault("repo_inventory", []).extend(repos)
            state["snapshots"] = state["snapshots"][-200:]
            state["repo_inventory"] = state["repo_inventory"][-5000:]
            return state
        INVENTORY_STORE.update(mutate)

    def _store_scanner_feed(self, snapshot: Dict[str, Any], scanner_result: Dict[str, Any]) -> None:
        feed = {"scanner_feed_id": f"scanner-feed-{uuid4().hex[:12]}", "snapshot_id": snapshot["snapshot_id"], "created_at": self._now(), "scanner_ok": scanner_result.get("ok"), "suggestion_count": len(scanner_result.get("suggestions", [])), "applied_count": len(scanner_result.get("applied_high_confidence", [])), "review_card_count": scanner_result.get("review_cards", {}).get("card_count")}
        def mutate(state: Dict[str, Any]) -> Dict[str, Any]:
            state.setdefault("scanner_feeds", []).append(feed)
            state["scanner_feeds"] = state["scanner_feeds"][-500:]
            return state
        INVENTORY_STORE.update(mutate)

    def _store_cards(self, cards: List[Dict[str, Any]]) -> None:
        def mutate(state: Dict[str, Any]) -> Dict[str, Any]:
            state.setdefault("new_repo_cards", []).extend(cards)
            state["new_repo_cards"] = state["new_repo_cards"][-1000:]
            return state
        INVENTORY_STORE.update(mutate)


github_repo_inventory_feed_service = GithubRepoInventoryFeedService()
