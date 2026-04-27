from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Callable, Dict, List


class HomeOperatorUxService:
    """Daily-use operator layer for the God Mode Home.

    This service does not create another technical cockpit. It translates the
    existing health/readiness/autopilot signals into a simple mobile-first daily
    operator experience: primary action, safe buttons and command phrases.
    """

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def _safe(self, label: str, fn: Callable[[], Any]) -> Dict[str, Any]:
        try:
            value = fn()
            return value if isinstance(value, dict) else {"ok": True, "mode": label, "value": value}
        except Exception as exc:
            return {"ok": False, "mode": label, "error": exc.__class__.__name__, "detail": str(exc)[:240]}

    def _health(self):
        from app.services.home_system_health_service import home_system_health_service

        return home_system_health_service

    def _priority(self):
        from app.services.operator_priority_service import operator_priority_service

        return operator_priority_service

    def _pc(self):
        from app.services.pc_autopilot_loop_service import pc_autopilot_loop_service

        return pc_autopilot_loop_service

    def build_panel(self, tenant_id: str = "owner-andre") -> Dict[str, Any]:
        health = self._safe("home_system_health", lambda: self._health().get_status(tenant_id=tenant_id))
        priority = self._safe("operator_priority", self._priority().get_status)
        pc = self._safe("pc_autopilot", self._pc().get_status)
        active_project = priority.get("active_project") or "GOD_MODE"
        primary_action = self._primary_action(health=health, pc=pc, active_project=active_project)
        return {
            "ok": True,
            "mode": "home_operator_ux_panel",
            "created_at": self._now(),
            "tenant_id": tenant_id,
            "active_project": active_project,
            "headline": self._headline(health=health, pc=pc),
            "primary_action": primary_action,
            "safe_buttons": self._safe_buttons(primary_action),
            "quick_commands": self._quick_commands(active_project),
            "driving_safe": True,
            "operator_rules": [
                "Escolhe projeto por prioridade, não por dinheiro.",
                "O backend continua até terminar, bloquear ou pedir OK.",
                "Não escrever dados sensíveis no chat: tokens, passwords, cookies ou API keys.",
                "Se estiver a conduzir, usar só botões curtos e aprovações claras.",
            ],
            "signals": {
                "health_score": health.get("health_score"),
                "health_status": health.get("status"),
                "pc_autopilot_status": pc.get("status"),
                "priority_ok": priority.get("ok") is True,
                "money_priority_enabled": priority.get("money_priority_enabled", False),
            },
        }

    def _headline(self, health: Dict[str, Any], pc: Dict[str, Any]) -> str:
        health_score = health.get("health_score", 0)
        pc_status = pc.get("status") or "unknown"
        if health.get("status") == "blocked":
            return f"Sistema bloqueado · saúde {health_score}%"
        if health.get("status") == "attention":
            return f"Precisa atenção · saúde {health_score}% · PC {pc_status}"
        if pc_status in {"running", "enabled_idle"}:
            return f"Pronto para trabalhar · saúde {health_score}% · PC ativo"
        return f"Pronto para ordem · saúde {health_score}%"

    def _primary_action(self, health: Dict[str, Any], pc: Dict[str, Any], active_project: str) -> Dict[str, Any]:
        if health.get("next_action"):
            action = dict(health["next_action"])
            action.setdefault("kind", "health_next_action")
            action.setdefault("priority", "critical")
            return action
        if pc.get("status") == "disabled":
            return {"kind": "start_autopilot", "label": "Ligar PC Autopilot", "endpoint": "/api/god-mode-home/start-autopilot", "priority": "critical"}
        return {
            "kind": "continue_project",
            "label": f"Continuar {active_project}",
            "endpoint": "/api/god-mode-home/continue",
            "payload": {"requested_project": active_project},
            "priority": "critical",
        }

    def _safe_buttons(self, primary_action: Dict[str, Any]) -> List[Dict[str, Any]]:
        buttons = [
            primary_action,
            {"kind": "chat", "label": "Chat", "route": "/app/operator-chat-sync-cards", "priority": "critical"},
            {"kind": "approve", "label": "Aprovar próximo", "endpoint": "/api/god-mode-home/approve-next", "priority": "high"},
            {"kind": "health", "label": "Saúde", "endpoint": "/api/home-system-health/snapshot", "priority": "high"},
            {"kind": "stop", "label": "Parar", "endpoint": "/api/god-mode-home/stop-autopilot", "priority": "medium"},
        ]
        seen = set()
        unique = []
        for button in buttons:
            key = button.get("endpoint") or button.get("route") or button.get("label")
            if key in seen:
                continue
            seen.add(key)
            unique.append(button)
        return unique

    def _quick_commands(self, active_project: str) -> List[Dict[str, str]]:
        return [
            {
                "id": "continue_active_project",
                "label": f"Continua {active_project}",
                "message": f"continua o projeto {active_project} até terminares ou precisares do meu OK",
            },
            {
                "id": "fix_blockers",
                "label": "Corrigir blockers",
                "message": f"analisa os blockers do {active_project}, cria plano curto e executa o que for seguro sem contornar aprovações",
            },
            {
                "id": "prepare_install",
                "label": "Preparar instalação",
                "message": "mostra o caminho mais simples para instalar e abrir o God Mode no PC e no APK",
            },
            {
                "id": "summarize_next",
                "label": "Resumo curto",
                "message": "dá-me só o estado atual, próximo passo e o que precisa do meu OK",
            },
        ]

    def get_status(self, tenant_id: str = "owner-andre") -> Dict[str, Any]:
        panel = self.build_panel(tenant_id=tenant_id)
        return {
            "ok": True,
            "mode": "home_operator_ux_status",
            "headline": panel["headline"],
            "active_project": panel["active_project"],
            "primary_action": panel["primary_action"],
            "safe_button_count": len(panel["safe_buttons"]),
            "quick_command_count": len(panel["quick_commands"]),
            "driving_safe": panel["driving_safe"],
        }

    def get_package(self, tenant_id: str = "owner-andre") -> Dict[str, Any]:
        return {"ok": True, "mode": "home_operator_ux_package", "package": {"status": self.get_status(tenant_id), "panel": self.build_panel(tenant_id)}}


home_operator_ux_service = HomeOperatorUxService()
