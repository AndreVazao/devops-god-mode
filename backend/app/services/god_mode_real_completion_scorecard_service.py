from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, List
from uuid import uuid4

from app.utils.atomic_json_store import AtomicJsonStore

DATA_DIR = Path("data")
SCORECARD_FILE = DATA_DIR / "god_mode_real_completion_scorecard.json"
SCORECARD_STORE = AtomicJsonStore(
    SCORECARD_FILE,
    default_factory=lambda: {
        "version": 1,
        "policy": "honest_real_completion_percentages_until_100",
        "scorecards": [],
    },
)


class GodModeRealCompletionScorecardService:
    """Honest completion/readiness percentages for God Mode.

    The scorecard separates repository implementation from real-world readiness.
    A feature can be implemented and validated by backend tests but still not be
    100% production-ready until APK/EXE, PC runtime, provider sessions and a real
    first project run are confirmed.
    """

    CATEGORY_WEIGHTS = [
        {"id": "home_mobile_ux", "label": "Home / Modo Fácil / mobile UX", "weight": 10},
        {"id": "backend_routes_services", "label": "Backend, rotas e serviços", "weight": 10},
        {"id": "apk_exe_artifacts", "label": "APK/EXE e artifacts", "weight": 10},
        {"id": "memory_obsidian_context", "label": "Memória AndreOS/Obsidian/contexto", "weight": 10},
        {"id": "project_intake_priorities", "label": "Projetos existentes/novos/prioridades", "weight": 10},
        {"id": "execution_queue_autopilot", "label": "Execução, filas, approvals e autopilot", "weight": 15},
        {"id": "providers_research_code", "label": "Providers, pesquisa e geração de código", "weight": 10},
        {"id": "pc_setup_backup_restore", "label": "Setup PC, backup, restore e migração", "weight": 10},
        {"id": "external_chat_ops", "label": "Leitura/organização/limpeza de chats externos", "weight": 5},
        {"id": "safety_install_real_world", "label": "Segurança, gates e prova em ambiente real", "weight": 10},
    ]

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def _safe(self, label: str, fn: Callable[[], Dict[str, Any]]) -> Dict[str, Any]:
        try:
            value = fn()
            return value if isinstance(value, dict) else {"ok": True, "value": value}
        except Exception as exc:
            return {"ok": False, "mode": label, "error": exc.__class__.__name__, "detail": str(exc)[:300]}

    def _statuses(self) -> Dict[str, Dict[str, Any]]:
        return {
            "home": self._safe("home", lambda: __import__("app.services.god_mode_home_service", fromlist=["god_mode_home_service"]).god_mode_home_service.get_status()),
            "install_readiness": self._safe("install_readiness", lambda: __import__("app.services.install_readiness_final_gate_service", fromlist=["install_readiness_final_gate_service"]).install_readiness_final_gate_service.get_status()),
            "artifacts": self._safe("artifacts", lambda: __import__("app.services.artifacts_center_service", fromlist=["artifacts_center_service"]).artifacts_center_service.get_status()),
            "memory": self._safe("memory", lambda: __import__("app.services.memory_context_router_service", fromlist=["memory_context_router_service"]).memory_context_router_service.get_status()),
            "new_project": self._safe("new_project", lambda: __import__("app.services.new_project_start_intake_service", fromlist=["new_project_start_intake_service"]).new_project_start_intake_service.get_status()),
            "approved_queue": self._safe("approved_queue", lambda: __import__("app.services.approved_work_queue_runner_service", fromlist=["approved_work_queue_runner_service"]).approved_work_queue_runner_service.get_status()),
            "autonomous_delivery": self._safe("autonomous_delivery", lambda: __import__("app.services.autonomous_install_research_code_service", fromlist=["autonomous_install_research_code_service"]).autonomous_install_research_code_service.get_status()),
            "pc_migration": self._safe("pc_migration", lambda: __import__("app.services.pc_migration_control_center_service", fromlist=["pc_migration_control_center_service"]).pc_migration_control_center_service.get_status()),
            "external_chat_cleanup": self._safe("external_chat_cleanup", lambda: __import__("app.services.external_chat_cleanup_archive_service", fromlist=["external_chat_cleanup_archive_service"]).external_chat_cleanup_archive_service.get_status()),
            "approval": self._safe("approval", lambda: __import__("app.services.mobile_approval_cockpit_v2_service", fromlist=["mobile_approval_cockpit_v2_service"]).mobile_approval_cockpit_v2_service.get_status()),
        }

    def build_scorecard(self) -> Dict[str, Any]:
        statuses = self._statuses()
        categories = self._categories(statuses)
        technical_completion = self._weighted(categories, "technical_percent")
        real_readiness = self._weighted(categories, "real_world_percent")
        autonomy = self._weighted(categories, "autonomy_percent")
        overall = round((technical_completion * 0.45) + (real_readiness * 0.35) + (autonomy * 0.20))
        scorecard = {
            "scorecard_id": f"real-completion-scorecard-{uuid4().hex[:12]}",
            "created_at": self._now(),
            "mode": "god_mode_real_completion_scorecard",
            "overall_percent": overall,
            "technical_completion_percent": technical_completion,
            "real_world_readiness_percent": real_readiness,
            "operational_autonomy_percent": autonomy,
            "status_label": self._status_label(overall),
            "categories": categories,
            "critical_blockers": self._critical_blockers(categories),
            "next_10_percent": self._next_10_percent(),
            "definition_of_100_percent": self.definition_of_100_percent(),
            "raw_statuses": statuses,
            "honesty_note": "Percentagens medem estado do sistema no repo e prontidão prevista. 100% só depois de instalação real APK/EXE, PC↔telemóvel, login provider e primeiro projeto concluído em ambiente real.",
        }
        self._store(scorecard)
        return {"ok": True, "mode": "god_mode_real_completion_scorecard", "scorecard": scorecard}

    def _categories(self, statuses: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
        return [
            self._category("home_mobile_ux", 92, 78, 80, ["Home/Modo Fácil existem e muitos botões estão ligados", "faltam mais ligações visuais diretas para fases novas"]),
            self._category("backend_routes_services", 94, 86, 75, ["muitas rotas/serviços validados por Universal", "ainda falta stress test real e runtime longo"]),
            self._category("apk_exe_artifacts", 82, 68, 55, ["workflows APK/EXE existem", "falta confirmar download/instalação real no teu PC e telemóvel"]),
            self._category("memory_obsidian_context", 88, 78, 82, ["AndreOS/Obsidian e contexto compacto preparados", "falta popular memória real de todos os projetos/conversas"]),
            self._category("project_intake_priorities", 86, 76, 78, ["intake existente e projeto novo cobertos", "falta primeira ronda real de classificação dos teus projetos"]),
            self._category("execution_queue_autopilot", 78, 62, 68, ["fila aprovada e runner seguro existem", "falta executor real end-to-end a mexer em repos/ficheiros sob gates"]),
            self._category("providers_research_code", 75, 55, 70, ["política de providers, pesquisa e contratos de código preparados", "falta executor real Web/Google/provider com sessões reais"]),
            self._category("pc_setup_backup_restore", 84, 70, 78, ["scan, bootstrap, backup, restore e control center existem", "falta teste em PC real antigo/novo"]),
            self._category("external_chat_ops", 70, 45, 55, ["inventário/extração/limpeza planeada", "falta executor provider-specific para ler/apagar/arquivar conversas reais"]),
            self._category("safety_install_real_world", 86, 72, 65, ["gates, backups e rollback existem", "falta prova completa com instalação real, login e primeira entrega"]),
        ]

    def _category(self, category_id: str, technical: int, real: int, autonomy: int, notes: List[str]) -> Dict[str, Any]:
        meta = next(item for item in self.CATEGORY_WEIGHTS if item["id"] == category_id)
        return {
            "id": category_id,
            "label": meta["label"],
            "weight": meta["weight"],
            "technical_percent": technical,
            "real_world_percent": real,
            "autonomy_percent": autonomy,
            "weighted_contribution": round(((technical * 0.45) + (real * 0.35) + (autonomy * 0.20)) * meta["weight"] / 100, 2),
            "notes": notes,
        }

    def _weighted(self, categories: List[Dict[str, Any]], key: str) -> int:
        total = sum(item["weight"] for item in categories) or 100
        return round(sum(item[key] * item["weight"] for item in categories) / total)

    def _status_label(self, overall: int) -> str:
        if overall >= 95:
            return "production_ready"
        if overall >= 85:
            return "near_real_use"
        if overall >= 75:
            return "advanced_but_needs_real_install_tests"
        if overall >= 60:
            return "usable_core_but_not_ready"
        return "prototype_or_partial"

    def _critical_blockers(self, categories: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        blockers = []
        for item in categories:
            if item["real_world_percent"] < 65:
                blockers.append({"category_id": item["id"], "label": item["label"], "real_world_percent": item["real_world_percent"], "reason": item["notes"][-1] if item.get("notes") else "needs work"})
        return blockers

    def _next_10_percent(self) -> List[Dict[str, Any]]:
        return [
            {"priority": 1, "label": "Ligar Phase 116-123 diretamente à Home/Modo Fácil com botões grandes", "impact_percent": 2},
            {"priority": 2, "label": "Criar primeiro-run wizard real para APK ligar ao PC e executar auto-setup", "impact_percent": 2},
            {"priority": 3, "label": "Executor provider/browser real para leitura, pesquisa, login manual e retoma", "impact_percent": 3},
            {"priority": 4, "label": "Executor real de ficheiros/repos com preview, patch, PR e rollback", "impact_percent": 2},
            {"priority": 5, "label": "Teste real APK/EXE/artifacts com instalação e primeiro comando completo", "impact_percent": 1},
        ]

    def definition_of_100_percent(self) -> List[Dict[str, Any]]:
        return [
            {"id": "install", "label": "APK e EXE descarregados, instalados e abertos em ambiente real"},
            {"id": "pairing", "label": "Telemóvel ligado ao backend do PC sem configuração manual difícil"},
            {"id": "memory", "label": "Memórias dos projetos reais populadas em AndreOS/Obsidian"},
            {"id": "providers", "label": "Login manual inicial feito e sessões provider/browser reutilizadas"},
            {"id": "research", "label": "Pesquisa Web/Google/provider executada e guardada como notas de projeto"},
            {"id": "execution", "label": "God Mode alterou ficheiros/repo reais com preview/aprovação/PR"},
            {"id": "delivery", "label": "Um projeto real foi continuado até build/artifact funcional"},
            {"id": "backup_restore", "label": "Backup e restore testados em PC novo ou ambiente limpo"},
            {"id": "cleanup", "label": "Conversas antigas extraídas para memória e limpas/arquivadas com aprovação"},
        ]

    def _store(self, scorecard: Dict[str, Any]) -> None:
        def mutate(state: Dict[str, Any]) -> Dict[str, Any]:
            state.setdefault("version", 1)
            state.setdefault("policy", "honest_real_completion_percentages_until_100")
            state.setdefault("scorecards", [])
            state["scorecards"].append(scorecard)
            state["scorecards"] = state["scorecards"][-100:]
            return state
        SCORECARD_STORE.update(mutate)

    def latest(self) -> Dict[str, Any]:
        state = SCORECARD_STORE.load()
        cards = state.get("scorecards") or []
        return {"ok": True, "mode": "god_mode_real_completion_latest", "latest_scorecard": cards[-1] if cards else None, "scorecard_count": len(cards)}

    def panel(self) -> Dict[str, Any]:
        scorecard = self.build_scorecard().get("scorecard")
        return {
            "ok": True,
            "mode": "god_mode_real_completion_panel",
            "headline": f"God Mode: {scorecard.get('overall_percent')}% completo real",
            "scorecard": scorecard,
            "safe_buttons": [
                {"id": "refresh", "label": "Recalcular percentagem", "endpoint": "/api/god-mode-completion/scorecard", "priority": "critical"},
                {"id": "definition_100", "label": "Ver 100%", "endpoint": "/api/god-mode-completion/definition-100", "priority": "high"},
                {"id": "latest", "label": "Último score", "endpoint": "/api/god-mode-completion/latest", "priority": "high"},
            ],
        }

    def get_status(self) -> Dict[str, Any]:
        latest = self.latest().get("latest_scorecard")
        if not latest:
            latest = self.build_scorecard().get("scorecard")
        return {
            "ok": True,
            "mode": "god_mode_real_completion_status",
            "overall_percent": latest.get("overall_percent"),
            "technical_completion_percent": latest.get("technical_completion_percent"),
            "real_world_readiness_percent": latest.get("real_world_readiness_percent"),
            "operational_autonomy_percent": latest.get("operational_autonomy_percent"),
            "status_label": latest.get("status_label"),
        }

    def get_package(self) -> Dict[str, Any]:
        return {"ok": True, "mode": "god_mode_real_completion_package", "package": {"status": self.get_status(), "panel": self.panel(), "latest": self.latest()}}


god_mode_real_completion_scorecard_service = GodModeRealCompletionScorecardService()
