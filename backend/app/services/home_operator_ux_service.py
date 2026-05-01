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
            "daily_command_route_endpoint": "/api/daily-command-router/route",
            "general_test_endpoint": "/api/real-operator-rehearsal/run",
            "critical_actions_endpoint": "/api/home-critical-actions/panel",
            "launch_center_endpoint": "/api/home-launch/panel",
            "download_install_endpoint": "/api/download-install-center-v2/panel",
            "final_readiness_endpoint": "/api/final-install-readiness-v2/check",
            "andreos_context_endpoint": "/api/andreos-context/panel",
            "andreos_memory_repo_endpoint": "/api/andreos-memory-repo/panel",
            "memory_boundary_endpoint": "/api/memory-boundary/panel",
            "ai_handoff_trace_endpoint": "/api/ai-handoff-trace/panel",
            "ollama_local_brain_endpoint": "/api/ollama-local-brain/panel",
            "desktop_self_update_endpoint": "/api/desktop-self-update/panel",
            "driving_safe": True,
            "operator_rules": [
                "Escolhe projeto por prioridade, não por dinheiro.",
                "O backend continua até terminar, bloquear ou pedir OK.",
                "Não escrever dados sensíveis no chat: tokens, passwords, cookies ou API keys.",
                "Se estiver a conduzir, usar só botões curtos e aprovações claras.",
                "GitHub memory é para programação das repos/programas; Obsidian local é para trabalho local e evolução.",
                "Antes de pedir ajuda a uma IA para código, usar a GitHub memory técnica do projeto.",
                "Toda passagem para IA deve ficar com trace_id e histórico.",
                "Usar Ollama como IA local privada para resumos, triagem e fallback, não como fonte final sem validação.",
                "Depois da primeira instalação com updater, preferir updates por pacote em vez de reinstalar tudo.",
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
        return {
            "kind": "continue_project",
            "label": f"Continuar {active_project}",
            "endpoint": "/api/daily-command-router/route",
            "payload": {"command_id": "continue_active_project", "requested_project": active_project},
            "priority": "critical",
        }

    def _safe_buttons(self, primary_action: Dict[str, Any]) -> List[Dict[str, Any]]:
        buttons = [
            {"kind": "desktop_self_update", "label": "Atualizações", "endpoint": "/api/desktop-self-update/panel", "priority": "critical"},
            {"kind": "memory_boundary", "label": "GitHub / Obsidian", "endpoint": "/api/memory-boundary/panel", "priority": "critical"},
            {"kind": "andreos_context", "label": "Contexto AndreOS", "endpoint": "/api/andreos-context/panel", "priority": "critical"},
            {"kind": "ai_handoff_trace", "label": "Handoff IA", "endpoint": "/api/ai-handoff-trace/panel", "priority": "critical"},
            {"kind": "ollama_local_brain", "label": "IA Local", "endpoint": "/api/ollama-local-brain/panel", "priority": "critical"},
            {"kind": "launch_center", "label": "Instalar / Baixar", "endpoint": "/api/home-launch/panel", "priority": "critical"},
            primary_action,
            {"kind": "final_readiness", "label": "Pronto para instalar?", "endpoint": "/api/final-install-readiness-v2/check", "priority": "critical"},
            {"kind": "download_install", "label": "Baixar APK/EXE", "endpoint": "/api/download-install-center-v2/panel", "priority": "critical"},
            {"kind": "critical_actions", "label": "Ações críticas", "endpoint": "/api/home-critical-actions/panel", "priority": "critical"},
            {"kind": "real_completion", "label": "Estado real %", "endpoint": "/api/god-mode-completion/panel", "priority": "critical"},
            {"kind": "general_test", "label": "Teste geral", "endpoint": "/api/real-operator-rehearsal/run", "payload": {"tenant_id": "owner-andre"}, "priority": "critical"},
            {"kind": "chat", "label": "Chat", "route": "/app/operator-chat-sync-cards", "priority": "critical"},
            {"kind": "approve", "label": "Aprovar próximo", "endpoint": "/api/god-mode-home/approve-next", "priority": "high"},
            {"kind": "health", "label": "Saúde", "endpoint": "/api/daily-command-router/route", "payload": {"command_id": "show_health"}, "priority": "high"},
            {"kind": "start_pc_autopilot", "label": "Ligar PC", "endpoint": "/api/god-mode-home/start-autopilot", "priority": "high"},
            {"kind": "stop", "label": "Parar", "endpoint": "/api/god-mode-home/stop-autopilot", "priority": "medium"},
        ]
        seen = set()
        unique = []
        for button in buttons:
            key = f"{button.get('endpoint') or button.get('route') or button.get('label')}::{button.get('kind')}"
            if key in seen:
                continue
            seen.add(key)
            unique.append(button)
        return unique

    def _quick_commands(self, active_project: str) -> List[Dict[str, str]]:
        route_endpoint = "/api/daily-command-router/route"
        return [
            {
                "id": "open_memory_boundary",
                "label": "GitHub/Obsidian",
                "message": "abre a regra de memória: GitHub para programação de repos e Obsidian para trabalho local/evolução",
                "route_endpoint": "/api/memory-boundary/panel",
            },
            {
                "id": "open_desktop_self_update",
                "label": "Atualizações",
                "message": "abre o painel de atualizações do God Mode, mostra versão atual e política de update sem reinstalar tudo",
                "route_endpoint": "/api/desktop-self-update/panel",
            },
            {
                "id": "open_ollama_local_brain",
                "label": "IA Local",
                "message": "abre o painel Ollama, testa modelos locais, escolhe o melhor e define quando usar IA local",
                "route_endpoint": "/api/ollama-local-brain/panel",
            },
            {
                "id": "open_ai_handoff_trace",
                "label": "Handoff IA",
                "message": "prepara um pedido para IA com repo, memória AndreOS e trace_id, e mostra como registar o resultado",
                "route_endpoint": "/api/ai-handoff-trace/panel",
            },
            {
                "id": "open_andreos_context",
                "label": "Contexto AndreOS",
                "message": "abre o orquestrador de contexto AndreOS e prepara contexto do projeto ativo antes de falar com IA",
                "route_endpoint": "/api/andreos-context/panel",
            },
            {
                "id": "open_launch_center",
                "label": "Instalar/Baixar",
                "message": "abre o centro de instalação, download, pairing e primeiro teste real",
                "route_endpoint": "/api/home-launch/panel",
            },
            {
                "id": "continue_active_project",
                "label": f"Continua {active_project}",
                "message": f"continua o projeto {active_project} até terminares ou precisares do meu OK",
                "route_endpoint": route_endpoint,
            },
            {
                "id": "fix_blockers",
                "label": "Corrigir blockers",
                "message": f"analisa os blockers do {active_project}, cria plano curto e executa o que for seguro sem contornar aprovações",
                "route_endpoint": route_endpoint,
            },
            {
                "id": "prepare_install",
                "label": "Preparar instalação",
                "message": "mostra o caminho mais simples para instalar e abrir o God Mode no PC e no APK",
                "route_endpoint": route_endpoint,
            },
            {
                "id": "show_critical_actions",
                "label": "Ações críticas",
                "message": "mostra o painel de ações críticas do God Mode e diz o próximo passo mais importante",
                "route_endpoint": "/api/home-critical-actions/panel",
            },
            {
                "id": "summarize_next",
                "label": "Resumo curto",
                "message": "dá-me só o estado atual, próximo passo e o que precisa do meu OK",
                "route_endpoint": route_endpoint,
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
            "daily_command_route_endpoint": panel["daily_command_route_endpoint"],
            "general_test_endpoint": panel["general_test_endpoint"],
            "critical_actions_endpoint": panel["critical_actions_endpoint"],
            "launch_center_endpoint": panel["launch_center_endpoint"],
            "download_install_endpoint": panel["download_install_endpoint"],
            "final_readiness_endpoint": panel["final_readiness_endpoint"],
            "andreos_context_endpoint": panel["andreos_context_endpoint"],
            "andreos_memory_repo_endpoint": panel["andreos_memory_repo_endpoint"],
            "memory_boundary_endpoint": panel["memory_boundary_endpoint"],
            "ai_handoff_trace_endpoint": panel["ai_handoff_trace_endpoint"],
            "ollama_local_brain_endpoint": panel["ollama_local_brain_endpoint"],
            "desktop_self_update_endpoint": panel["desktop_self_update_endpoint"],
            "driving_safe": panel["driving_safe"],
        }

    def get_package(self, tenant_id: str = "owner-andre") -> Dict[str, Any]:
        return {"ok": True, "mode": "home_operator_ux_package", "package": {"status": self.get_status(tenant_id), "panel": self.build_panel(tenant_id)}}


home_operator_ux_service = HomeOperatorUxService()
