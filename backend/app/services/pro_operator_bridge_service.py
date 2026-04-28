from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List
from uuid import uuid4

from app.services.daily_command_router_service import daily_command_router_service
from app.services.local_ai_adapter_service import local_ai_adapter_service
from app.services.professional_scorecard_service import professional_scorecard_service
from app.services.start_now_panel_service import start_now_panel_service


class ProOperatorBridgeService:
    """Professional operator bridge for mobile-first natural-language commands.

    It does three jobs:
    1. Understand a short operator request.
    2. Pick the safest existing route.
    3. Execute only low/normal risk routes automatically; otherwise return an approval-ready plan.
    """

    HIGH_RISK_WORDS = [
        "apagar",
        "delete",
        "remove",
        "reset",
        "formatar",
        "token",
        "password",
        "senha",
        "cookie",
        "secret",
        "credential",
        "destruir",
        "limpar tudo",
    ]

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def analyze(self, text: str, tenant_id: str = "owner-andre", requested_project: str = "GOD_MODE") -> Dict[str, Any]:
        clean = (text or "").strip()
        bridge_id = f"pro-bridge-{uuid4().hex[:12]}"
        if not clean:
            return {
                "ok": False,
                "mode": "pro_operator_analysis",
                "bridge_id": bridge_id,
                "error": "empty_text",
                "operator_next": {"label": "Escrever uma ordem curta", "route": "/app/home"},
            }
        local = local_ai_adapter_service.classify_operator_text(clean)
        deterministic = self._deterministic_route(clean)
        risk = self._risk(clean, local_result=local.get("result", ""), route_id=deterministic["route_id"])
        score = professional_scorecard_service.build_scorecard(tenant_id=tenant_id, requested_project=requested_project)
        start_now = start_now_panel_service.build_panel(tenant_id=tenant_id, requested_project=requested_project)
        approval_required = risk in {"high", "blocked"} or score.get("score", 0) < 75
        return {
            "ok": True,
            "mode": "pro_operator_analysis",
            "bridge_id": bridge_id,
            "created_at": self._now(),
            "tenant_id": tenant_id,
            "requested_project": requested_project,
            "text": clean[:1200],
            "classification": local,
            "route": deterministic,
            "risk": risk,
            "approval_required": approval_required,
            "can_auto_run": not approval_required and deterministic.get("kind") in {"daily_command", "read_panel"},
            "professional_score": {
                "score": score.get("score"),
                "grade": score.get("grade"),
                "status": score.get("status"),
                "blocker_count": len(score.get("blockers", [])),
            },
            "start_now_status": {
                "status": start_now.get("status"),
                "blocker_count": len(start_now.get("blockers", [])),
                "primary_action": start_now.get("primary_action"),
            },
            "operator_next": self._operator_next(approval_required=approval_required, route=deterministic),
            "safety": {
                "destructive_changes_allowed": False,
                "secrets_allowed_in_prompt": False,
                "operator_priority_source": "operator",
                "fallback_without_local_ai": local.get("source") == "deterministic_fallback" or local.get("ok") is True,
            },
        }

    def run(self, text: str, tenant_id: str = "owner-andre", requested_project: str = "GOD_MODE", approve: bool = False) -> Dict[str, Any]:
        analysis = self.analyze(text=text, tenant_id=tenant_id, requested_project=requested_project)
        if not analysis.get("ok"):
            return analysis
        route = analysis["route"]
        if analysis["approval_required"] and not approve:
            return {
                "ok": False,
                "mode": "pro_operator_run",
                "status": "waiting_operator_approval",
                "analysis": analysis,
                "operator_next": {"label": "Rever plano antes de executar", "endpoint": "/api/pro-operator/analyze", "route": "/app/home"},
            }
        if route["kind"] == "daily_command":
            result = daily_command_router_service.route(
                command_id=route["command_id"],
                tenant_id=tenant_id,
                requested_project=requested_project,
            )
        elif route["kind"] == "read_panel" and route["endpoint"] == "/api/start-now/panel":
            result = start_now_panel_service.build_panel(tenant_id=tenant_id, requested_project=requested_project)
        elif route["kind"] == "read_panel" and route["endpoint"] == "/api/professional-scorecard/scorecard":
            result = professional_scorecard_service.build_scorecard(tenant_id=tenant_id, requested_project=requested_project)
        elif route["kind"] == "read_panel" and route["endpoint"] == "/api/local-ai/panel":
            result = local_ai_adapter_service.build_panel()
        else:
            result = {"ok": False, "error": "unsupported_route", "route": route}
        return {
            "ok": bool(result.get("ok", False)),
            "mode": "pro_operator_run",
            "status": "executed" if result.get("ok") else "failed",
            "analysis": analysis,
            "result": result,
            "operator_next": result.get("operator_next", {"label": "Voltar à Home", "route": "/app/home"}) if isinstance(result, dict) else {"label": "Voltar à Home", "route": "/app/home"},
        }

    def _deterministic_route(self, text: str) -> Dict[str, Any]:
        low = text.lower()
        if any(word in low for word in ["começar", "arrancar", "iniciar", "start now", "começa"]):
            return {"kind": "read_panel", "route_id": "start_now", "label": "Começar agora", "endpoint": "/api/start-now/panel"}
        if any(word in low for word in ["score", "profissional", "profissionalismo", "avalia"]):
            return {"kind": "read_panel", "route_id": "professional_scorecard", "label": "Score profissional", "endpoint": "/api/professional-scorecard/scorecard"}
        if any(word in low for word in ["ia local", "ollama", "gemma", "modelo local"]):
            return {"kind": "read_panel", "route_id": "local_ai", "label": "IA local", "endpoint": "/api/local-ai/panel"}
        if any(word in low for word in ["apk", "exe", "artifact", "download", "descarregar"]):
            return {"kind": "daily_command", "route_id": "show_artifacts", "label": "Ver APK/EXE", "command_id": "show_artifacts"}
        if any(word in low for word in ["instalar", "instalação", "preparar instalação"]):
            return {"kind": "daily_command", "route_id": "prepare_install", "label": "Preparar instalação", "command_id": "prepare_install"}
        if any(word in low for word in ["saúde", "health", "estado", "status"]):
            return {"kind": "daily_command", "route_id": "show_health", "label": "Ver saúde", "command_id": "show_health"}
        if any(word in low for word in ["blocker", "bloqueio", "corrige", "arranja", "fix"]):
            return {"kind": "daily_command", "route_id": "fix_blockers", "label": "Corrigir blockers", "command_id": "fix_blockers"}
        if any(word in low for word in ["resumo", "resume", "próximo", "proximo"]):
            return {"kind": "daily_command", "route_id": "summarize_next", "label": "Resumo curto", "command_id": "summarize_next"}
        return {"kind": "daily_command", "route_id": "continue_active_project", "label": "Continuar projeto ativo", "command_id": "continue_active_project"}

    def _risk(self, text: str, local_result: str, route_id: str) -> str:
        low = text.lower()
        if any(word in low for word in self.HIGH_RISK_WORDS):
            return "high"
        if "risk=high" in (local_result or "").lower():
            return "high"
        if route_id in {"fix_blockers", "continue_active_project"}:
            return "medium"
        return "low"

    def _operator_next(self, approval_required: bool, route: Dict[str, Any]) -> Dict[str, Any]:
        if approval_required:
            return {"label": "Rever antes de executar", "endpoint": "/api/pro-operator/analyze", "route": "/app/home"}
        if route.get("endpoint"):
            return {"label": route.get("label", "Abrir painel"), "endpoint": route["endpoint"], "route": "/app/home"}
        return {"label": route.get("label", "Executar"), "endpoint": "/api/pro-operator/run", "route": "/app/home"}

    def build_panel(self, tenant_id: str = "owner-andre", requested_project: str = "GOD_MODE") -> Dict[str, Any]:
        score = professional_scorecard_service.get_status(tenant_id=tenant_id)
        local = local_ai_adapter_service.get_status()
        return {
            "ok": True,
            "mode": "pro_operator_panel",
            "created_at": self._now(),
            "headline": "Operador Pro",
            "input_placeholder": "Ex: continua o God Mode, mostra APK/EXE, avalia profissionalismo, liga IA local...",
            "analyze_endpoint": "/api/pro-operator/analyze",
            "run_endpoint": "/api/pro-operator/run",
            "quick_examples": [
                "começar agora",
                "mostra o score profissional",
                "ver IA local",
                "mostra APK e EXE",
                "corrige blockers do God Mode",
                "dá resumo e próximo passo",
            ],
            "signals": {
                "professional_score": score,
                "local_ai": local,
            },
            "rules": [
                "ordens de baixo risco podem seguir direto",
                "risco alto fica em análise e pede confirmação",
                "IA local é opcional e nunca bloqueia o fluxo",
                "ações destrutivas não avançam automaticamente",
            ],
        }

    def get_status(self, tenant_id: str = "owner-andre") -> Dict[str, Any]:
        panel = self.build_panel(tenant_id=tenant_id)
        return {
            "ok": True,
            "mode": "pro_operator_status",
            "headline": panel["headline"],
            "professional_score": panel["signals"]["professional_score"],
            "local_ai_status": panel["signals"]["local_ai"].get("status"),
        }

    def get_package(self, tenant_id: str = "owner-andre", requested_project: str = "GOD_MODE") -> Dict[str, Any]:
        return {"ok": True, "mode": "pro_operator_package", "package": {"status": self.get_status(tenant_id=tenant_id), "panel": self.build_panel(tenant_id=tenant_id, requested_project=requested_project)}}


pro_operator_bridge_service = ProOperatorBridgeService()
