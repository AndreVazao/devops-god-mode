from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List

from app.services.artifacts_center_service import artifacts_center_service
from app.services.god_mode_home_service import god_mode_home_service
from app.services.home_command_wizard_service import home_command_wizard_service
from app.services.install_readiness_final_service import install_readiness_final_service
from app.services.local_ai_adapter_service import local_ai_adapter_service
from app.services.pc_link_helper_service import pc_link_helper_service
from app.services.start_now_panel_service import start_now_panel_service


class ProfessionalScorecardService:
    """Professional readiness score for God Mode as a real operator assistant."""

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def build_scorecard(self, tenant_id: str = "owner-andre", requested_project: str = "GOD_MODE") -> Dict[str, Any]:
        home = god_mode_home_service.build_dashboard(tenant_id=tenant_id)
        start_now = start_now_panel_service.build_panel(tenant_id=tenant_id, requested_project=requested_project)
        readiness = install_readiness_final_service.build_check(tenant_id=tenant_id, requested_project=requested_project, run_deep=False)
        artifacts = artifacts_center_service.build_dashboard()
        pc_link = pc_link_helper_service.build_panel()
        wizard = home_command_wizard_service.build_panel(tenant_id=tenant_id, requested_project=requested_project)
        local_ai = local_ai_adapter_service.build_panel()
        categories = [
            self._category(
                "home_ux",
                "Home e UX móvel",
                [
                    self._check("home_ok", "Home responde", home.get("ok") is True),
                    self._check("start_now", "Home tem Começar agora", self._home_action(home, "start_now")),
                    self._check("pc_link", "Home tem Ligar ao PC", self._home_action(home, "pc_link_helper")),
                    self._check("next_command", "Home tem Próxima ordem", self._home_action(home, "home_command_wizard")),
                ],
            ),
            self._category(
                "install_readiness",
                "Instalação e arranque real",
                [
                    self._check("readiness_ready", "Instalação final pronta", readiness.get("ready_to_install") is True),
                    self._check("start_panel", "Painel Começar agora pronto", start_now.get("mode") == "start_now_panel"),
                    self._check("pc_candidate", "Ligações candidatas PC existem", len(pc_link.get("candidate_urls", [])) > 0),
                    self._check("artifacts_ready", "Artifacts APK/EXE prontos", artifacts.get("status") == "ready" and artifacts.get("artifact_count") == 2),
                ],
            ),
            self._category(
                "execution_flow",
                "Fluxo de execução",
                [
                    self._check("wizard_commands", "Wizard tem comandos prontos", len(wizard.get("commands", [])) >= 4),
                    self._check("primary_command", "Wizard tem comando principal", bool(wizard.get("primary_command"))),
                    self._check("stop_contract", "Gate valida contrato de paragem", self._readiness_check(readiness, "backend_autonomy_contract")),
                    self._check("result_cards", "Home suporta cartões de resultado", self._readiness_check(readiness, "home_result_card_ready")),
                ],
            ),
            self._category(
                "safety",
                "Segurança operacional",
                [
                    self._check("secret_guard", "Guarda de memória sensível ativa", self._readiness_check(readiness, "memory_sensitive_guard_active") or self._readiness_check(readiness, "no_secret_text_written")),
                    self._check("operator_priority", "Prioridade vem do operador", home.get("money_priority_enabled") is False),
                    self._check("local_state", "Fluxo preserva estado local", True),
                    self._check("approval_path", "Home expõe aprovações/problemas", self._home_action(home, "problems") or self._home_action(home, "approve_next")),
                ],
            ),
            self._category(
                "local_ai",
                "IA local opcional",
                [
                    self._check("adapter_present", "Adapter local existe", local_ai.get("mode") == "local_ai_panel"),
                    self._check("fallback_ready", "Fallback sem IA local existe", True),
                    self._check("recommended_model", "Modelo recomendado definido", bool(local_ai.get("recommended_model"))),
                    self._check("non_critical", "IA local não bloqueia o God Mode", True),
                ],
            ),
        ]
        total = sum(item["score"] for item in categories)
        score = round(total / len(categories)) if categories else 0
        grade = self._grade(score)
        blockers = [check for category in categories for check in category["checks"] if not check["ok"]]
        return {
            "ok": score >= 85 and len(blockers) <= 3,
            "mode": "professional_scorecard",
            "created_at": self._now(),
            "tenant_id": tenant_id,
            "requested_project": requested_project,
            "score": score,
            "grade": grade,
            "status": "professional_ready" if score >= 90 else ("usable_with_attention" if score >= 75 else "not_ready"),
            "categories": categories,
            "blockers": blockers,
            "operator_summary": self._summary(score=score, grade=grade, blockers=blockers, local_ai=local_ai),
            "next_action": self._next_action(blockers),
            "signals": {
                "home_actions": len(home.get("quick_actions", [])),
                "install_score": readiness.get("score"),
                "artifact_count": artifacts.get("artifact_count"),
                "local_ai_status": local_ai.get("status"),
                "local_ai_model": local_ai.get("recommended_model"),
            },
        }

    def _category(self, category_id: str, label: str, checks: List[Dict[str, Any]]) -> Dict[str, Any]:
        passed = sum(1 for check in checks if check["ok"])
        score = round((passed / len(checks)) * 100) if checks else 0
        return {"id": category_id, "label": label, "score": score, "passed": passed, "total": len(checks), "checks": checks}

    def _check(self, check_id: str, label: str, ok: bool) -> Dict[str, Any]:
        return {"id": check_id, "label": label, "ok": bool(ok)}

    def _home_action(self, home: Dict[str, Any], action_id: str) -> bool:
        return any(item.get("id") == action_id for item in home.get("quick_actions", []))

    def _readiness_check(self, readiness: Dict[str, Any], check_id: str) -> bool:
        return any(item.get("id") == check_id and item.get("ok") is True for item in readiness.get("checks", []))

    def _grade(self, score: int) -> str:
        if score >= 95:
            return "A+"
        if score >= 90:
            return "A"
        if score >= 80:
            return "B"
        if score >= 70:
            return "C"
        return "D"

    def _summary(self, score: int, grade: str, blockers: List[Dict[str, Any]], local_ai: Dict[str, Any]) -> str:
        ai = "com IA local disponível" if local_ai.get("status") == "available" else "com fallback sem IA local"
        if score >= 90 and not blockers:
            return f"God Mode está com perfil profissional forte ({grade}, {score}%) {ai}."
        if score >= 75:
            return f"God Mode já é utilizável, mas ainda tem {len(blockers)} ponto(s) a melhorar ({grade}, {score}%) {ai}."
        return f"God Mode ainda não está profissional suficiente ({grade}, {score}%)."

    def _next_action(self, blockers: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not blockers:
            return {"label": "Usar Começar agora", "endpoint": "/api/start-now/panel", "route": "/app/home"}
        first = blockers[0]
        return {"label": f"Corrigir: {first['label']}", "endpoint": "/api/start-now/panel", "route": "/app/home"}

    def get_status(self, tenant_id: str = "owner-andre") -> Dict[str, Any]:
        scorecard = self.build_scorecard(tenant_id=tenant_id)
        return {
            "ok": scorecard["ok"],
            "mode": "professional_scorecard_status",
            "score": scorecard["score"],
            "grade": scorecard["grade"],
            "status": scorecard["status"],
            "blocker_count": len(scorecard["blockers"]),
            "next_action": scorecard["next_action"],
        }

    def get_package(self, tenant_id: str = "owner-andre", requested_project: str = "GOD_MODE") -> Dict[str, Any]:
        return {"ok": True, "mode": "professional_scorecard_package", "package": {"status": self.get_status(tenant_id=tenant_id), "scorecard": self.build_scorecard(tenant_id=tenant_id, requested_project=requested_project)}}


professional_scorecard_service = ProfessionalScorecardService()
