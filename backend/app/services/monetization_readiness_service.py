from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List
from uuid import uuid4

from app.services.memory_core_service import memory_core_service
from app.services.project_portfolio_service import project_portfolio_service
from app.services.repository_discovery_scout_service import repository_discovery_scout_service
from app.utils.atomic_json_store import AtomicJsonStore

DATA_DIR = Path("data")
MONETIZATION_FILE = DATA_DIR / "monetization_readiness.json"
MONETIZATION_STORE = AtomicJsonStore(
    MONETIZATION_FILE,
    default_factory=lambda: {"reports": [], "project_overrides": {}, "actions": []},
)

DEFAULT_MVP = {
    "GOD_MODE": "Cockpit local/mobile operacional para gerir projetos, memória, GitHub, aprovações e builds.",
    "BOT_FACTORY": "MVP de observação e planeamento: registar jogos-alvo, padrões observados e gerar plano/repo de bot por jogo.",
    "BARIBUDOS_STUDIO": "Studio mínimo que gere conteúdo, estado de produção e ligação ao website.",
    "BARIBUDOS_STUDIO_WEBSITE": "Landing pública com oferta clara, contacto/checkout e ligação ao Studio.",
    "PROVENTIL": "Sistema de orçamentos e propostas com histórico por morada e geração de PDF/email.",
    "VERBAFORGE": "Gerador semi-automático de conteúdo vendável com aprovação e publicação assistida.",
    "BOT_LORDS_MOBILE": "Versão read-only/assistida para planeamento, comandos e memória operacional segura.",
    "ECU_REPRO": "Diagnóstico seguro com relatório, backup conceptual, presets e consentimento do cliente.",
    "BUILD_CONTROL_CENTER": "Dashboard que lista repos e aciona builds APK/EXE com links de artefactos.",
}

SELLABLE_FEATURE = {
    "GOD_MODE": "Serviço interno de produtividade para acelerar entrega dos restantes produtos.",
    "BOT_FACTORY": "Pacote de análise/blueprint de bot por jogo antes de automação paga.",
    "BARIBUDOS_STUDIO": "Produção de histórias/conteúdo Baribudos com workflow de aprovação.",
    "BARIBUDOS_STUDIO_WEBSITE": "Página pública para captar leads e vender produtos/conteúdo.",
    "PROVENTIL": "Propostas profissionais rápidas para videoporteiros/ventilação.",
    "VERBAFORGE": "Ebooks/cursos/posts prontos para vender/publicar.",
    "BOT_LORDS_MOBILE": "Assistente de organização e estratégia, sem depender de automação destrutiva.",
    "ECU_REPRO": "Relatório de diagnóstico e proposta técnica para cliente/oficina.",
    "BUILD_CONTROL_CENTER": "Builds centralizados como serviço interno para acelerar releases.",
}


def priority_weight(priority: str) -> int:
    return {"critical": 30, "high": 22, "medium": 14, "low": 6}.get(priority, 10)


class MonetizationReadinessService:
    """MVP and money-path matrix for the project portfolio."""

    def get_status(self) -> Dict[str, Any]:
        store = self._load_store()
        return {
            "ok": True,
            "mode": "monetization_readiness_status",
            "status": "monetization_readiness_ready",
            "store_file": str(MONETIZATION_FILE),
            "atomic_store_enabled": True,
            "report_count": len(store.get("reports", [])),
        }

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def _normalize_store(self, store: Dict[str, Any]) -> Dict[str, Any]:
        if not isinstance(store, dict):
            return {"reports": [], "project_overrides": {}, "actions": []}
        store.setdefault("reports", [])
        store.setdefault("project_overrides", {})
        store.setdefault("actions", [])
        return store

    def _load_store(self) -> Dict[str, Any]:
        return self._normalize_store(MONETIZATION_STORE.load())

    def _memory_score(self, project_id: str) -> int:
        memory = memory_core_service.read_project(project_id)
        files = memory.get("memory", {}) if memory.get("ok") else {}
        checks = [
            len(files.get("MEMORIA_MESTRE.md", "").strip()) > 120,
            len(files.get("ARQUITETURA.md", "").strip()) > 80,
            "- [ ]" in files.get("BACKLOG.md", ""),
            len(files.get("DECISOES.md", "").strip()) > 80,
            len(files.get("ULTIMA_SESSAO.md", "").strip()) > 80,
        ]
        return round(sum(1 for item in checks if item) / len(checks) * 100)

    def _repo_score(self, project_id: str, repositories: List[str]) -> Dict[str, Any]:
        if repositories:
            return {"score": 100, "status": "repo_linked", "blocker": ""}
        audit = repository_discovery_scout_service.audit_project_repository_state(project_id)
        status = audit.get("audit", {}).get("status", "unknown") if audit.get("ok") else "unknown"
        return {"score": 30 if status == "needs_repo_decision" else 50, "status": status, "blocker": "Repo/app ainda não confirmado"}

    def _project_row(self, project: Dict[str, Any]) -> Dict[str, Any]:
        project_id = project.get("project_id")
        repos = project.get("repositories", [])
        memory_score = self._memory_score(project_id)
        repo = self._repo_score(project_id, repos)
        priority = project.get("priority", "medium")
        mvp = DEFAULT_MVP.get(project_id, f"Definir MVP vendável para {project.get('name', project_id)}.")
        sellable = SELLABLE_FEATURE.get(project_id, "Definir primeira feature vendável.")
        blockers: List[str] = []
        if repo["blocker"]:
            blockers.append(repo["blocker"])
        if memory_score < 80:
            blockers.append("Memória AndreOS ainda incompleta")
        if not project.get("goal"):
            blockers.append("Objetivo comercial pouco definido")
        readiness_score = min(100, priority_weight(priority) + round(memory_score * 0.25) + round(repo["score"] * 0.25) + (20 if sellable else 0))
        status = "ready_to_package" if readiness_score >= 80 and not blockers else "needs_focus"
        if readiness_score < 55:
            status = "blocked"
        next_action = self._next_action(project_id, status, blockers, repos)
        return {
            "project_id": project_id,
            "name": project.get("name", project_id),
            "priority": priority,
            "category": project.get("category", "general"),
            "goal": project.get("goal", ""),
            "repositories": repos,
            "mvp": mvp,
            "first_sellable_feature": sellable,
            "revenue_path": self._revenue_path(project_id, project.get("category", "general")),
            "memory_score": memory_score,
            "repository_score": repo["score"],
            "repository_status": repo["status"],
            "readiness_score": readiness_score,
            "status": status,
            "blockers": blockers,
            "next_action": next_action,
        }

    def _revenue_path(self, project_id: str, category: str) -> str:
        if project_id == "PROVENTIL":
            return "Usar para fechar orçamentos e obras reais em Portugal. Receita por serviço/proposta/obra."
        if project_id in {"BARIBUDOS_STUDIO", "BARIBUDOS_STUDIO_WEBSITE", "VERBAFORGE"}:
            return "Conteúdo, ebooks, cursos, leads, campanhas e produtos digitais."
        if project_id == "BOT_FACTORY":
            return "Blueprints/bots por jogo, licenciamento futuro e automações por projeto."
        if project_id == "ECU_REPRO":
            return "Relatórios de diagnóstico, presets seguros e propostas para oficinas/clientes."
        if project_id == "BUILD_CONTROL_CENTER":
            return "Reduz tempo de release dos produtos que geram dinheiro."
        if project_id == "GOD_MODE":
            return "Motor interno para acelerar todos os produtos monetizáveis."
        return f"Definir caminho de receita para categoria {category}."

    def _next_action(self, project_id: str, status: str, blockers: List[str], repos: List[str]) -> str:
        if not repos:
            return "Confirmar repo existente ou aprovar criação de repo novo."
        if "Memória AndreOS ainda incompleta" in blockers:
            return "Preencher ARQUITETURA, BACKLOG, DECISOES e ULTIMA_SESSAO antes de desenvolver."
        if status == "ready_to_package":
            return "Preparar PR de empacotamento/MVP e plano de entrega."
        return "Fazer auditoria profunda e transformar blockers em tarefas aprováveis."

    def build_matrix(self) -> Dict[str, Any]:
        portfolio = project_portfolio_service.build_dashboard()
        rows = [self._project_row(project) for project in portfolio.get("projects", [])]
        rows = sorted(rows, key=lambda item: (item["status"] != "ready_to_package", -item["readiness_score"], item["name"]))
        report = {
            "report_id": f"money-matrix-{uuid4().hex[:12]}",
            "created_at": self._now(),
            "project_count": len(rows),
            "ready_count": len([item for item in rows if item["status"] == "ready_to_package"]),
            "blocked_count": len([item for item in rows if item["status"] == "blocked"]),
            "focus_count": len([item for item in rows if item["status"] == "needs_focus"]),
            "rows": rows,
            "top_recommendations": self._recommendations(rows),
        }

        def mutate(store: Dict[str, Any]) -> Dict[str, Any]:
            store = self._normalize_store(store)
            store["reports"].append(report)
            store["reports"] = store["reports"][-100:]
            return store

        MONETIZATION_STORE.update(mutate)
        memory_core_service.write_history("GOD_MODE", "Monetization readiness matrix generated", f"Report {report['report_id']} with {report['project_count']} projects")
        return {"ok": True, "mode": "monetization_readiness_matrix", "report": report}

    def _recommendations(self, rows: List[Dict[str, Any]]) -> List[str]:
        recommendations: List[str] = []
        ready = [item for item in rows if item["status"] == "ready_to_package"]
        if ready:
            recommendations.append(f"Empacotar primeiro: {ready[0]['name']} — {ready[0]['first_sellable_feature']}")
        no_repo = [item for item in rows if not item.get("repositories")]
        if no_repo:
            recommendations.append(f"Resolver repo primeiro: {no_repo[0]['name']}.")
        high = [item for item in rows if item["priority"] in {"critical", "high"}]
        if high:
            recommendations.append(f"Foco comercial imediato: {high[0]['name']} com score {high[0]['readiness_score']}.")
        recommendations.append("Não adicionar ferramentas novas até cada projeto high ter MVP, repo, build/deploy e primeira oferta vendável definidos.")
        return recommendations

    def list_reports(self, limit: int = 20) -> Dict[str, Any]:
        store = self._load_store()
        reports = store.get("reports", [])[-max(min(limit, 100), 1):]
        return {"ok": True, "mode": "monetization_readiness_report_list", "report_count": len(reports), "reports": reports}

    def build_dashboard(self) -> Dict[str, Any]:
        matrix = self.build_matrix()
        report = matrix["report"]
        return {
            "ok": True,
            "mode": "monetization_readiness_dashboard",
            "summary": {k: report[k] for k in ["project_count", "ready_count", "blocked_count", "focus_count"]},
            "rows": report["rows"],
            "top_recommendations": report["top_recommendations"],
        }

    def get_package(self) -> Dict[str, Any]:
        return {"ok": True, "mode": "monetization_readiness_package", "package": {"status": self.get_status(), "dashboard": self.build_dashboard()}}


monetization_readiness_service = MonetizationReadinessService()
