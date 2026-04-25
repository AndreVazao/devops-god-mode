from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List
from uuid import uuid4

from app.services.memory_core_service import memory_core_service
from app.services.repo_relationship_graph_service import repo_relationship_graph_service
from app.utils.atomic_json_store import AtomicJsonStore

DATA_DIR = Path("data")
PORTFOLIO_FILE = DATA_DIR / "project_portfolio.json"
PORTFOLIO_STORE = AtomicJsonStore(
    PORTFOLIO_FILE,
    default_factory=lambda: {"projects": {}, "repositories": {}, "links": [], "snapshots": []},
)

SEED_PROJECTS: List[Dict[str, Any]] = [
    {
        "project_id": "GOD_MODE",
        "name": "God Mode",
        "category": "core_platform",
        "goal": "Cockpit mobile/PC com memória AndreOS, IA, GitHub, aprovações e execução segura.",
        "priority": "critical",
        "repositories": ["AndreVazao/devops-god-mode"],
    },
    {
        "project_id": "BOT_FACTORY",
        "name": "Bot Factory",
        "category": "bot_generation_platform",
        "goal": "Programa para criar outros bots por observação, engenharia reversa assistida, avaliação contínua de jogos e aprendizagem a partir do telemóvel enquanto André joga.",
        "priority": "critical",
        "repositories": [],
        "monetization_path": "Gerar bots reutilizáveis/licenciáveis para jogos e automações, começando por análise read-only, captura de padrões e geração de projetos por fases.",
        "notes": "Não desenvolver o bot aqui agora; o God Mode deve primeiro mapear, auditar e depois criar/reconstruir o projeto certo quando houver repo ou decisão de novo repo.",
    },
    {
        "project_id": "BARIBUDOS_STUDIO",
        "name": "Baribudos Studio",
        "category": "content_business",
        "goal": "Cockpit/estúdio para controlar conteúdo, website e ecossistema Baribudos.",
        "priority": "high",
        "repositories": ["AndreVazao/baribudos-studio", "AndreVazao/baribudos-studio-website"],
    },
    {
        "project_id": "BARIBUDOS_STUDIO_WEBSITE",
        "name": "Baribudos Studio Website",
        "category": "website",
        "goal": "Website público ligado ao Baribudos Studio.",
        "priority": "high",
        "repositories": ["AndreVazao/baribudos-studio-website"],
        "parent_project_id": "BARIBUDOS_STUDIO",
    },
    {
        "project_id": "PROVENTIL",
        "name": "ProVentil",
        "category": "business_ops",
        "goal": "Sistema comercial/técnico para videoporteiros, ventilação, orçamentos, obras e histórico.",
        "priority": "high",
        "repositories": [],
    },
    {
        "project_id": "VERBAFORGE",
        "name": "VerbaForge",
        "category": "content_automation",
        "goal": "Geração e publicação de conteúdo monetizável com memória, aprovação e métricas.",
        "priority": "high",
        "repositories": [],
    },
    {
        "project_id": "BOT_LORDS_MOBILE",
        "name": "Bot Lords Mobile",
        "category": "automation",
        "goal": "Automação multi-instância/headless com comandos, permissões, memória e auditoria.",
        "priority": "medium",
        "repositories": [],
    },
    {
        "project_id": "ECU_REPRO",
        "name": "ECU Repro",
        "category": "diagnostics",
        "goal": "Diagnóstico/reprogramação assistida com backups, segurança e histórico por veículo.",
        "priority": "medium",
        "repositories": [],
    },
    {
        "project_id": "BUILD_CONTROL_CENTER",
        "name": "Build Control Center",
        "category": "devops",
        "goal": "Dashboard para listar repos, lançar builds e recolher artifacts APK/EXE.",
        "priority": "high",
        "repositories": [],
    },
]


class ProjectPortfolioService:
    """Portfolio brain for all André projects and repository relationships."""

    def get_status(self) -> Dict[str, Any]:
        store = self._load_store()
        return {
            "ok": True,
            "mode": "project_portfolio_status",
            "status": "project_portfolio_ready",
            "store_file": str(PORTFOLIO_FILE),
            "atomic_store_enabled": True,
            "project_count": len(store.get("projects", {})),
            "repository_count": len(store.get("repositories", {})),
        }

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def _normalize_store(self, store: Dict[str, Any]) -> Dict[str, Any]:
        if not isinstance(store, dict):
            return {"projects": {}, "repositories": {}, "links": [], "snapshots": []}
        store.setdefault("projects", {})
        store.setdefault("repositories", {})
        store.setdefault("links", [])
        store.setdefault("snapshots", [])
        return store

    def _load_store(self) -> Dict[str, Any]:
        return self._normalize_store(PORTFOLIO_STORE.load())

    def seed_defaults(self) -> Dict[str, Any]:
        seeded: List[str] = []
        repo_seeded: List[str] = []
        now = self._now()

        def mutate(store: Dict[str, Any]) -> Dict[str, Any]:
            store = self._normalize_store(store)
            for project in SEED_PROJECTS:
                project_id = project["project_id"]
                existing = store["projects"].get(project_id, {})
                record = {
                    **existing,
                    **project,
                    "project_id": project_id,
                    "updated_at": now,
                    "created_at": existing.get("created_at", now),
                    "memory_project": project_id,
                    "status": existing.get("status", "active"),
                }
                store["projects"][project_id] = record
                seeded.append(project_id)
                for repo in project.get("repositories", []):
                    repo_record = store["repositories"].setdefault(repo, {"repository_full_name": repo, "created_at": now})
                    repo_record.update({"repository_full_name": repo, "project_id": project_id, "updated_at": now, "status": "linked"})
                    repo_seeded.append(repo)
            return store

        PORTFOLIO_STORE.update(mutate)
        for project in SEED_PROJECTS:
            memory_core_service.create_project(project["project_id"])
            if project.get("repositories"):
                memory_core_service.write_history(
                    project["project_id"],
                    action="Project Portfolio linked repositories",
                    result=", ".join(project.get("repositories", [])),
                )
        return {"ok": True, "mode": "project_portfolio_seed_defaults", "projects": sorted(set(seeded)), "repositories": sorted(set(repo_seeded))}

    def upsert_project(self, project_id: str, name: str, goal: str = "", category: str = "general", priority: str = "medium", repositories: List[str] | None = None) -> Dict[str, Any]:
        normalized_id = project_id.upper().replace("-", "_").replace(" ", "_")
        now = self._now()
        repos = repositories or []
        record: Dict[str, Any] = {}

        def mutate(store: Dict[str, Any]) -> Dict[str, Any]:
            nonlocal record
            store = self._normalize_store(store)
            existing = store["projects"].get(normalized_id, {})
            record = {
                **existing,
                "project_id": normalized_id,
                "name": name,
                "goal": goal,
                "category": category,
                "priority": priority,
                "repositories": sorted(set(existing.get("repositories", [])) | set(repos)),
                "memory_project": normalized_id,
                "status": existing.get("status", "active"),
                "created_at": existing.get("created_at", now),
                "updated_at": now,
            }
            store["projects"][normalized_id] = record
            for repo in repos:
                store["repositories"][repo] = {"repository_full_name": repo, "project_id": normalized_id, "status": "linked", "updated_at": now, "created_at": store["repositories"].get(repo, {}).get("created_at", now)}
            return store

        PORTFOLIO_STORE.update(mutate)
        memory_core_service.create_project(normalized_id)
        return {"ok": True, "mode": "project_portfolio_upsert_project", "project": record}

    def link_repository(self, project_id: str, repository_full_name: str, role: str = "unknown") -> Dict[str, Any]:
        normalized_id = project_id.upper().replace("-", "_").replace(" ", "_")
        repo = repository_full_name.strip()
        if not repo:
            return {"ok": False, "error": "repository_empty"}
        now = self._now()

        def mutate(store: Dict[str, Any]) -> Dict[str, Any]:
            store = self._normalize_store(store)
            project = store["projects"].setdefault(normalized_id, {"project_id": normalized_id, "name": normalized_id, "repositories": [], "created_at": now, "status": "active", "memory_project": normalized_id})
            project["repositories"] = sorted(set(project.get("repositories", [])) | {repo})
            project["updated_at"] = now
            store["repositories"][repo] = {"repository_full_name": repo, "project_id": normalized_id, "role": role, "status": "linked", "updated_at": now, "created_at": store["repositories"].get(repo, {}).get("created_at", now)}
            store["links"].append({"link_id": f"link-{uuid4().hex[:12]}", "project_id": normalized_id, "repository_full_name": repo, "role": role, "created_at": now})
            store["links"] = store["links"][-1000:]
            return store

        PORTFOLIO_STORE.update(mutate)
        memory_core_service.write_history(normalized_id, "Repository linked to project portfolio", f"{repo} as {role}")
        try:
            repo_relationship_graph_service.upsert_repository(repository_full_name=repo, project_id=normalized_id.lower().replace("_", "-"), project_name=normalized_id.replace("_", " ").title(), roles=[role], description="Linked by Project Portfolio", deploy_targets=["github-actions"])
        except Exception:
            pass
        return {"ok": True, "mode": "project_portfolio_link_repository", "project_id": normalized_id, "repository_full_name": repo, "role": role}

    def build_dashboard(self) -> Dict[str, Any]:
        self.seed_defaults()
        store = self._load_store()
        projects = list(store.get("projects", {}).values())
        repos = list(store.get("repositories", {}).values())
        by_priority: Dict[str, int] = {}
        for project in projects:
            by_priority[project.get("priority", "medium")] = by_priority.get(project.get("priority", "medium"), 0) + 1
        monetization_ready = [project for project in projects if project.get("priority") in {"critical", "high"}]
        snapshot = {
            "snapshot_id": f"portfolio-{uuid4().hex[:12]}",
            "created_at": self._now(),
            "project_count": len(projects),
            "repository_count": len(repos),
            "high_priority_count": len(monetization_ready),
        }
        return {
            "ok": True,
            "mode": "project_portfolio_dashboard",
            "summary": snapshot,
            "by_priority": by_priority,
            "projects": sorted(projects, key=lambda item: (item.get("priority") != "critical", item.get("priority") != "high", item.get("name", ""))),
            "repositories": repos,
            "next_recommended_actions": [
                "Ligar Baribudos Studio e Website ao Build Control Center.",
                "Auditar Bot Factory e decidir se já existe repo ou se deve criar repo novo.",
                "Auditar ProVentil para definir repo, deploy e MVP monetizável.",
                "Criar matriz de produto/preço para projetos com prioridade high.",
                "Adicionar estado de deploy por repo e último artifact disponível.",
            ],
        }

    def get_package(self) -> Dict[str, Any]:
        return {"ok": True, "mode": "project_portfolio_package", "package": {"status": self.get_status(), "dashboard": self.build_dashboard()}}


project_portfolio_service = ProjectPortfolioService()
