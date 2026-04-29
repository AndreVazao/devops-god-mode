from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, List
from uuid import uuid4

from app.utils.atomic_json_store import AtomicJsonStore

DATA_DIR = Path("data")
ADVISOR_FILE = DATA_DIR / "spectacular_upgrade_advisor.json"
ADVISOR_STORE = AtomicJsonStore(
    ADVISOR_FILE,
    default_factory=lambda: {
        "version": 1,
        "policy": "turn_god_mode_from_very_good_to_spectacular_by_prioritized_gaps",
        "reports": [],
    },
)


class SpectacularUpgradeAdvisorService:
    """Senior-engineer advisor for what God Mode still needs.

    This service is intentionally opinionated. It looks at current strategic
    modules and recommends the next upgrades that most improve real-world use,
    automation, reliability and operator simplicity.
    """

    UPGRADE_CATALOG = [
        {
            "id": "browser_provider_executor",
            "label": "Executor real de browser/providers",
            "why": "Sem isto, leitura de chats, pesquisa Google/provider e retoma real continuam parcialmente planeadas.",
            "impact": 10,
            "effort": 8,
            "risk": 7,
            "category": "real_world_execution",
            "recommended_phase": "Phase 131",
            "must_have": True,
        },
        {
            "id": "repo_file_patch_executor",
            "label": "Executor real de ficheiros/repos com preview, patch, PR e rollback",
            "why": "É o salto entre aconselhar e trabalhar mesmo em projetos reais com segurança.",
            "impact": 10,
            "effort": 7,
            "risk": 6,
            "category": "delivery",
            "recommended_phase": "Phase 132",
            "must_have": True,
        },
        {
            "id": "first_run_pairing_wizard",
            "label": "Wizard APK ↔ PC de primeiro arranque",
            "why": "O operador precisa ligar telemóvel ao backend sem configurar IPs/portas à mão.",
            "impact": 9,
            "effort": 6,
            "risk": 5,
            "category": "mobile_first",
            "recommended_phase": "Phase 133",
            "must_have": True,
        },
        {
            "id": "job_resume_engine",
            "label": "Motor de jobs retomáveis com checkpoints",
            "why": "Se a net cair, APK fechar ou provider limitar, o backend deve continuar/retomar sem perder estado.",
            "impact": 9,
            "effort": 7,
            "risk": 5,
            "category": "reliability",
            "recommended_phase": "Phase 134",
            "must_have": True,
        },
        {
            "id": "real_install_smoke_test",
            "label": "Smoke test real pós-instalação APK/EXE",
            "why": "Dá prova objetiva de que o produto abriu, ligou, fez pedido e respondeu.",
            "impact": 8,
            "effort": 5,
            "risk": 4,
            "category": "quality",
            "recommended_phase": "Phase 135",
            "must_have": True,
        },
        {
            "id": "project_done_archive_gate",
            "label": "Gate de projeto concluído + arquivo/limpeza",
            "why": "Fecha projetos, congela memória, limpa conversas antigas e impede mexer sem nova aprovação.",
            "impact": 7,
            "effort": 4,
            "risk": 3,
            "category": "project_lifecycle",
            "recommended_phase": "Phase 136",
            "must_have": False,
        },
        {
            "id": "operator_voice_mode",
            "label": "Modo voz/condutor com respostas curtas e confirmações seguras",
            "why": "Tu usas muitas vezes o telemóvel na rua/condução; voz reduz fricção.",
            "impact": 8,
            "effort": 6,
            "risk": 5,
            "category": "operator_ux",
            "recommended_phase": "Phase 137",
            "must_have": False,
        },
        {
            "id": "artifact_download_center_v2",
            "label": "Centro de downloads APK/EXE com links e versão atual",
            "why": "O operador deve ver claramente o que baixar, versão, data, commit e estado.",
            "impact": 7,
            "effort": 4,
            "risk": 3,
            "category": "installability",
            "recommended_phase": "Phase 138",
            "must_have": False,
        },
        {
            "id": "self_healing_diagnostics",
            "label": "Auto-diagnóstico e auto-correção de falhas comuns",
            "why": "Quando algo falhar, o God Mode deve tentar corrigir dependências, portas, paths e ambiente.",
            "impact": 9,
            "effort": 7,
            "risk": 5,
            "category": "reliability",
            "recommended_phase": "Phase 139",
            "must_have": True,
        },
        {
            "id": "knowledge_quality_guard",
            "label": "Guardião de qualidade da memória/conhecimento",
            "why": "Evita memória suja, duplicada, obsoleta ou errada em Obsidian/AndreOS.",
            "impact": 7,
            "effort": 5,
            "risk": 3,
            "category": "memory_quality",
            "recommended_phase": "Phase 140",
            "must_have": False,
        },
    ]

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def _safe(self, label: str, fn: Callable[[], Dict[str, Any]]) -> Dict[str, Any]:
        try:
            value = fn()
            return value if isinstance(value, dict) else {"ok": True, "value": value}
        except Exception as exc:
            return {"ok": False, "mode": label, "error": exc.__class__.__name__, "detail": str(exc)[:300]}

    def current_signals(self) -> Dict[str, Any]:
        return {
            "completion": self._safe("completion", lambda: __import__("app.services.god_mode_real_completion_scorecard_service", fromlist=["god_mode_real_completion_scorecard_service"]).god_mode_real_completion_scorecard_service.get_status()),
            "critical_hub": self._safe("critical_hub", lambda: __import__("app.services.home_critical_actions_hub_service", fromlist=["home_critical_actions_hub_service"]).home_critical_actions_hub_service.get_status()),
            "pc_migration": self._safe("pc_migration", lambda: __import__("app.services.pc_migration_control_center_service", fromlist=["pc_migration_control_center_service"]).pc_migration_control_center_service.get_status()),
            "performance": self._safe("performance", lambda: __import__("app.services.local_performance_autopilot_service", fromlist=["local_performance_autopilot_service"]).local_performance_autopilot_service.get_status()),
            "autonomous_delivery": self._safe("autonomous_delivery", lambda: __import__("app.services.autonomous_install_research_code_service", fromlist=["autonomous_install_research_code_service"]).autonomous_install_research_code_service.get_status()),
            "external_chat_cleanup": self._safe("external_chat_cleanup", lambda: __import__("app.services.external_chat_cleanup_archive_service", fromlist=["external_chat_cleanup_archive_service"]).external_chat_cleanup_archive_service.get_status()),
        }

    def report(self) -> Dict[str, Any]:
        signals = self.current_signals()
        ranked = self._rank_upgrades(signals)
        top = ranked[:5]
        report = {
            "report_id": f"spectacular-upgrade-report-{uuid4().hex[:12]}",
            "created_at": self._now(),
            "mode": "spectacular_upgrade_advisor_report",
            "headline": "De muito bom para espetacular",
            "overall_read": self._overall_read(signals),
            "top_recommendations": top,
            "all_recommendations": ranked,
            "senior_advice": self._senior_advice(top),
            "next_phase_recommendation": top[0] if top else None,
            "signals": signals,
        }
        self._store(report)
        return {"ok": True, "mode": "spectacular_upgrade_advisor_report", "report": report}

    def _rank_upgrades(self, signals: Dict[str, Any]) -> List[Dict[str, Any]]:
        completion = signals.get("completion", {})
        readiness = completion.get("real_world_readiness_percent", 70) or 70
        autonomy = completion.get("operational_autonomy_percent", 70) or 70
        ranked = []
        for item in self.UPGRADE_CATALOG:
            urgency = 0
            if item["must_have"]:
                urgency += 8
            if item["category"] == "real_world_execution" and readiness < 85:
                urgency += 10
            if item["category"] == "delivery" and readiness < 85:
                urgency += 9
            if item["category"] in {"reliability", "operator_ux"} and autonomy < 85:
                urgency += 7
            score = round((item["impact"] * 3.0) + urgency - (item["effort"] * 0.7) - (item["risk"] * 0.4), 2)
            ranked.append({**item, "advisor_score": score})
        return sorted(ranked, key=lambda value: value["advisor_score"], reverse=True)

    def _overall_read(self, signals: Dict[str, Any]) -> Dict[str, Any]:
        completion = signals.get("completion", {})
        overall = completion.get("overall_percent", 76)
        if overall >= 90:
            label = "quase espetacular"
        elif overall >= 80:
            label = "muito bom, falta prova real"
        else:
            label = "muito avançado, ainda falta execução real"
        return {
            "overall_percent": overall,
            "technical_percent": completion.get("technical_completion_percent"),
            "real_world_percent": completion.get("real_world_readiness_percent"),
            "autonomy_percent": completion.get("operational_autonomy_percent"),
            "label": label,
        }

    def _senior_advice(self, top: List[Dict[str, Any]]) -> List[str]:
        advice = [
            "Não adicionaria mais dashboards soltos; agora o foco deve ser execução real controlada.",
            "O maior salto é transformar planos em ações reais com preview, rollback e checkpoints.",
            "Browser/provider executor e repo patch executor são os dois pilares que mais aproximam dos 100%.",
            "Tudo novo deve aparecer na Home/Modo Fácil ou no Hub de Ações Críticas.",
        ]
        if top:
            advice.append(f"Próxima fase recomendada: {top[0]['recommended_phase']} — {top[0]['label']}.")
        return advice

    def phase_plan(self) -> Dict[str, Any]:
        report = self.report().get("report", {})
        top = report.get("top_recommendations", [])
        return {
            "ok": True,
            "mode": "spectacular_upgrade_phase_plan",
            "next_phases": [
                {
                    "phase": item.get("recommended_phase"),
                    "upgrade_id": item.get("id"),
                    "label": item.get("label"),
                    "why": item.get("why"),
                    "advisor_score": item.get("advisor_score"),
                    "must_have": item.get("must_have"),
                }
                for item in top
            ],
        }

    def _store(self, report: Dict[str, Any]) -> None:
        def mutate(state: Dict[str, Any]) -> Dict[str, Any]:
            state.setdefault("version", 1)
            state.setdefault("policy", "turn_god_mode_from_very_good_to_spectacular_by_prioritized_gaps")
            state.setdefault("reports", [])
            state["reports"].append(report)
            state["reports"] = state["reports"][-100:]
            return state
        ADVISOR_STORE.update(mutate)

    def latest(self) -> Dict[str, Any]:
        state = ADVISOR_STORE.load()
        reports = state.get("reports") or []
        return {"ok": True, "mode": "spectacular_upgrade_latest", "latest_report": reports[-1] if reports else None, "report_count": len(reports)}

    def panel(self) -> Dict[str, Any]:
        report = self.report().get("report")
        return {
            "ok": True,
            "mode": "spectacular_upgrade_panel",
            "headline": "Conselheiro sénior do God Mode",
            "report": report,
            "safe_buttons": [
                {"id": "report", "label": "Analisar lacunas", "endpoint": "/api/spectacular-upgrade-advisor/report", "priority": "critical"},
                {"id": "phase_plan", "label": "Próximas fases", "endpoint": "/api/spectacular-upgrade-advisor/phase-plan", "priority": "critical"},
                {"id": "latest", "label": "Último conselho", "endpoint": "/api/spectacular-upgrade-advisor/latest", "priority": "high"},
            ],
        }

    def get_status(self) -> Dict[str, Any]:
        latest = self.latest().get("latest_report")
        if not latest:
            latest = self.report().get("report")
        next_phase = latest.get("next_phase_recommendation") or {}
        return {
            "ok": True,
            "mode": "spectacular_upgrade_status",
            "overall_read": latest.get("overall_read"),
            "next_phase": next_phase.get("recommended_phase"),
            "next_upgrade": next_phase.get("label"),
            "top_count": len(latest.get("top_recommendations") or []),
        }

    def get_package(self) -> Dict[str, Any]:
        return {"ok": True, "mode": "spectacular_upgrade_package", "package": {"status": self.get_status(), "panel": self.panel(), "latest": self.latest()}}


spectacular_upgrade_advisor_service = SpectacularUpgradeAdvisorService()
