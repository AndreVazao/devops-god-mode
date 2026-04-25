from __future__ import annotations

import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List
from uuid import uuid4

from app.services.memory_core_service import memory_core_service
from app.services.project_portfolio_service import project_portfolio_service
from app.utils.atomic_json_store import AtomicJsonStore

DATA_DIR = Path("data")
DISCOVERY_FILE = DATA_DIR / "repository_discovery_scout.json"
DISCOVERY_STORE = AtomicJsonStore(
    DISCOVERY_FILE,
    default_factory=lambda: {"candidates": [], "audits": [], "decisions": []},
)

DEFAULT_SEARCH_TERMS = {
    "BOT_FACTORY": ["bot-factory", "good-factory", "botfactory", "bot-generator", "reverse-engineering-bots", "game-bot-factory", "factory"],
    "BARIBUDOS_STUDIO": ["baribudos-studio", "bodybou-studio", "very-good-studio"],
    "BARIBUDOS_STUDIO_WEBSITE": ["baribudos-studio-website", "bodybou-studio-website", "studio-website"],
    "PROVENTIL": ["proventil", "proventil-app", "proventil-web"],
    "VERBAFORGE": ["verbaforge", "verba-forge", "viralvazao"],
    "BUILD_CONTROL_CENTER": ["build-control-center", "build-center", "universal-build"],
}


class RepositoryDiscoveryScoutService:
    """Portfolio-aware repo discovery planner.

    This service does not guess private GitHub state by itself. It creates a clear
    candidate matrix, stores manual/reported matches, links confirmed repos into
    Project Portfolio and records the decision in AndreOS Memory Core.
    """

    def get_status(self) -> Dict[str, Any]:
        store = self._load_store()
        return {
            "ok": True,
            "mode": "repository_discovery_scout_status",
            "status": "repository_discovery_scout_ready",
            "store_file": str(DISCOVERY_FILE),
            "atomic_store_enabled": True,
            "candidate_count": len(store.get("candidates", [])),
            "audit_count": len(store.get("audits", [])),
        }

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def _normalize_store(self, store: Dict[str, Any]) -> Dict[str, Any]:
        if not isinstance(store, dict):
            return {"candidates": [], "audits": [], "decisions": []}
        store.setdefault("candidates", [])
        store.setdefault("audits", [])
        store.setdefault("decisions", [])
        return store

    def _load_store(self) -> Dict[str, Any]:
        return self._normalize_store(DISCOVERY_STORE.load())

    def _slug(self, value: str) -> str:
        return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")

    def build_search_plan(self, project_id: str) -> Dict[str, Any]:
        normalized = project_id.upper().replace("-", "_").replace(" ", "_")
        portfolio = project_portfolio_service.build_dashboard()
        project = next((item for item in portfolio.get("projects", []) if item.get("project_id") == normalized), None)
        if project is None:
            return {"ok": False, "error": "project_not_in_portfolio", "project_id": normalized}
        terms = DEFAULT_SEARCH_TERMS.get(normalized, [self._slug(normalized), normalized.lower()])
        existing_repos = project.get("repositories", [])
        plan = {
            "plan_id": f"repo-search-{uuid4().hex[:12]}",
            "created_at": self._now(),
            "project_id": normalized,
            "project_name": project.get("name", normalized),
            "goal": project.get("goal", ""),
            "existing_repositories": existing_repos,
            "search_terms": terms,
            "recommended_github_queries": [f"user:AndreVazao {term}" for term in terms],
            "decision_needed": "link_existing_repo" if existing_repos else "find_or_create_repo",
            "safe_next_steps": [
                "Pesquisar repos por nomes prováveis.",
                "Se encontrar repo, confirmar se pertence ao projeto.",
                "Ligar repo ao Project Portfolio com aprovação.",
                "Se não encontrar repo, criar proposta de novo repo em vez de criar automaticamente.",
            ],
        }
        return {"ok": True, "mode": "repository_discovery_search_plan", "plan": plan}

    def add_candidate(self, project_id: str, repository_full_name: str, confidence: float = 0.5, source: str = "manual", note: str = "") -> Dict[str, Any]:
        normalized = project_id.upper().replace("-", "_").replace(" ", "_")
        repo = repository_full_name.strip()
        if not repo or "/" not in repo:
            return {"ok": False, "error": "invalid_repository_full_name"}
        candidate = {
            "candidate_id": f"candidate-{uuid4().hex[:12]}",
            "project_id": normalized,
            "repository_full_name": repo,
            "confidence": max(0.0, min(float(confidence), 1.0)),
            "source": source,
            "note": note,
            "status": "candidate",
            "created_at": self._now(),
        }

        def mutate(store: Dict[str, Any]) -> Dict[str, Any]:
            store = self._normalize_store(store)
            store["candidates"].append(candidate)
            store["candidates"] = store["candidates"][-1000:]
            return store

        DISCOVERY_STORE.update(mutate)
        memory_core_service.write_history(normalized, "Repository Discovery candidate added", f"{repo} confidence={candidate['confidence']} source={source}")
        return {"ok": True, "mode": "repository_discovery_add_candidate", "candidate": candidate}

    def list_candidates(self, project_id: str | None = None, limit: int = 100) -> Dict[str, Any]:
        store = self._load_store()
        candidates = store.get("candidates", [])
        if project_id:
            normalized = project_id.upper().replace("-", "_").replace(" ", "_")
            candidates = [item for item in candidates if item.get("project_id") == normalized]
        candidates = candidates[-max(min(limit, 300), 1):]
        return {"ok": True, "mode": "repository_discovery_candidate_list", "candidate_count": len(candidates), "candidates": candidates}

    def confirm_candidate(self, candidate_id: str, role: str = "unknown") -> Dict[str, Any]:
        store = self._load_store()
        candidate = next((item for item in store.get("candidates", []) if item.get("candidate_id") == candidate_id), None)
        if candidate is None:
            return {"ok": False, "error": "candidate_not_found", "candidate_id": candidate_id}
        link = project_portfolio_service.link_repository(candidate["project_id"], candidate["repository_full_name"], role=role)
        decision = {
            "decision_id": f"repo-decision-{uuid4().hex[:12]}",
            "candidate_id": candidate_id,
            "project_id": candidate["project_id"],
            "repository_full_name": candidate["repository_full_name"],
            "role": role,
            "decision": "confirmed_and_linked" if link.get("ok") else "link_failed",
            "created_at": self._now(),
        }

        def mutate(payload: Dict[str, Any]) -> Dict[str, Any]:
            payload = self._normalize_store(payload)
            for item in payload.get("candidates", []):
                if item.get("candidate_id") == candidate_id:
                    item["status"] = decision["decision"]
                    item["updated_at"] = self._now()
                    item["role"] = role
                    break
            payload["decisions"].append(decision)
            payload["decisions"] = payload["decisions"][-500:]
            return payload

        DISCOVERY_STORE.update(mutate)
        memory_core_service.write_decision(candidate["project_id"], f"Repo {candidate['repository_full_name']} ligado ao projeto {candidate['project_id']}.", f"Confirmado pelo Repository Discovery Scout com role {role}.")
        return {"ok": True, "mode": "repository_discovery_confirm_candidate", "candidate": candidate, "portfolio_link": link, "decision": decision}

    def propose_new_repo(self, project_id: str, suggested_repo_name: str | None = None) -> Dict[str, Any]:
        normalized = project_id.upper().replace("-", "_").replace(" ", "_")
        repo_name = suggested_repo_name or normalized.lower().replace("_", "-")
        proposal = {
            "proposal_id": f"repo-proposal-{uuid4().hex[:12]}",
            "project_id": normalized,
            "suggested_repository_full_name": f"AndreVazao/{repo_name}",
            "created_at": self._now(),
            "status": "needs_operator_approval",
            "reason": "Nenhum repositório confirmado no portfólio. Criar repo só depois de aprovação explícita.",
            "recommended_first_files": ["README.md", "PROJECT_TREE.txt", ".github/workflows/build.yml", "docs/ARCHITECTURE.md"],
        }

        def mutate(payload: Dict[str, Any]) -> Dict[str, Any]:
            payload = self._normalize_store(payload)
            payload["audits"].append(proposal)
            payload["audits"] = payload["audits"][-500:]
            return payload

        DISCOVERY_STORE.update(mutate)
        memory_core_service.write_history(normalized, "Repository creation proposal prepared", proposal["suggested_repository_full_name"])
        return {"ok": True, "mode": "repository_discovery_propose_new_repo", "proposal": proposal}

    def audit_project_repository_state(self, project_id: str) -> Dict[str, Any]:
        plan = self.build_search_plan(project_id)
        if not plan.get("ok"):
            return plan
        normalized = plan["plan"]["project_id"]
        candidates = self.list_candidates(normalized).get("candidates", [])
        confirmed = [item for item in candidates if item.get("status") == "confirmed_and_linked"]
        needs_repo = not plan["plan"].get("existing_repositories") and not confirmed
        proposal = self.propose_new_repo(normalized) if needs_repo else None
        audit = {
            "audit_id": f"repo-audit-{uuid4().hex[:12]}",
            "created_at": self._now(),
            "project_id": normalized,
            "existing_repository_count": len(plan["plan"].get("existing_repositories", [])),
            "candidate_count": len(candidates),
            "confirmed_count": len(confirmed),
            "status": "needs_repo_decision" if needs_repo else "has_repository_or_candidate",
            "plan": plan["plan"],
            "proposal": proposal.get("proposal") if proposal else None,
        }

        def mutate(payload: Dict[str, Any]) -> Dict[str, Any]:
            payload = self._normalize_store(payload)
            payload["audits"].append(audit)
            payload["audits"] = payload["audits"][-500:]
            return payload

        DISCOVERY_STORE.update(mutate)
        return {"ok": True, "mode": "repository_discovery_project_audit", "audit": audit}

    def build_dashboard(self) -> Dict[str, Any]:
        portfolio = project_portfolio_service.build_dashboard()
        audits = [self.audit_project_repository_state(project["project_id"]).get("audit") for project in portfolio.get("projects", [])]
        audits = [item for item in audits if item]
        needs_repo = [item for item in audits if item.get("status") == "needs_repo_decision"]
        return {
            "ok": True,
            "mode": "repository_discovery_dashboard",
            "project_count": len(audits),
            "needs_repo_decision_count": len(needs_repo),
            "audits": audits,
            "candidates": self.list_candidates(limit=200).get("candidates", []),
        }

    def get_package(self) -> Dict[str, Any]:
        return {"ok": True, "mode": "repository_discovery_package", "package": {"status": self.get_status(), "dashboard": self.build_dashboard()}}


repository_discovery_scout_service = RepositoryDiscoveryScoutService()
