from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List

from app.services.daily_command_router_service import daily_command_router_service
from app.services.first_real_install_launcher_service import first_real_install_launcher_service
from app.services.god_mode_home_service import god_mode_home_service
from app.services.install_readiness_final_service import install_readiness_final_service


class HomeCommandWizardService:
    """Simple Home wizard for the next safe operator command."""

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def build_panel(self, tenant_id: str = "owner-andre", requested_project: str = "GOD_MODE") -> Dict[str, Any]:
        home = god_mode_home_service.build_dashboard(tenant_id=tenant_id)
        install = first_real_install_launcher_service.build_plan(
            tenant_id=tenant_id,
            requested_project=requested_project,
        )
        readiness = install_readiness_final_service.build_check(
            tenant_id=tenant_id,
            requested_project=requested_project,
            run_deep=False,
        )
        project = requested_project or home.get("active_project") or "GOD_MODE"
        commands = self._commands(project=project, install_ready=readiness.get("ready_to_install") is True)
        return {
            "ok": True,
            "mode": "home_command_wizard_panel",
            "created_at": self._now(),
            "tenant_id": tenant_id,
            "project": project,
            "headline": "Escolhe a próxima ordem segura",
            "status": "ready" if readiness.get("ready_to_install") else "check_install_first",
            "primary_command": commands[0],
            "commands": commands,
            "send_endpoint": "/api/daily-command-router/route",
            "chat_endpoint": "/api/god-mode-home/chat",
            "home_route": "/app/home",
            "signals": {
                "home_active_project": home.get("active_project"),
                "traffic_light": home.get("traffic_light"),
                "install_ready": readiness.get("ready_to_install"),
                "install_score": readiness.get("score"),
                "launch_ready": install.get("ready_to_launch"),
                "launch_blocker_count": len(install.get("blockers", [])),
            },
            "operator_rules": [
                "Usa comandos curtos quando estiveres no telemóvel.",
                "Se aparecer aprovação, decide antes de continuar.",
                "Não coloques credenciais no texto da ordem.",
                "A prioridade vem do operador.",
            ],
        }

    def _commands(self, project: str, install_ready: bool) -> List[Dict[str, Any]]:
        base = [
            {
                "id": "continue_active_project",
                "label": "Continuar projeto",
                "button_text": "Continuar",
                "message_preview": f"continua o projeto {project} até terminares ou precisares do meu OK",
                "endpoint": "/api/daily-command-router/route",
                "payload": {"command_id": "continue_active_project", "requested_project": project, "tenant_id": "owner-andre"},
                "safe_level": "normal",
            },
            {
                "id": "fix_blockers",
                "label": "Corrigir bloqueios",
                "button_text": "Corrigir blockers",
                "message_preview": f"analisa blockers do {project} e executa só o que for seguro",
                "endpoint": "/api/daily-command-router/route",
                "payload": {"command_id": "fix_blockers", "requested_project": project, "tenant_id": "owner-andre"},
                "safe_level": "careful",
            },
            {
                "id": "summarize_next",
                "label": "Resumo e próximo passo",
                "button_text": "Resumo curto",
                "message_preview": f"dá o estado atual do {project}, próximo passo e pedidos de OK",
                "endpoint": "/api/daily-command-router/route",
                "payload": {"command_id": "summarize_next", "requested_project": project, "tenant_id": "owner-andre"},
                "safe_level": "readable",
            },
            {
                "id": "show_artifacts",
                "label": "Ver APK/EXE",
                "button_text": "APK/EXE",
                "message_preview": "abrir centro de artifacts e atalhos de download",
                "endpoint": "/api/daily-command-router/route",
                "payload": {"command_id": "show_artifacts", "requested_project": project, "tenant_id": "owner-andre"},
                "safe_level": "readable",
            },
        ]
        if not install_ready:
            return [
                {
                    "id": "install_readiness_final",
                    "label": "Confirmar instalação final",
                    "button_text": "Instalação final",
                    "message_preview": "validar Home, Modo Fácil, Teste geral, memória, rehearsal e artifacts",
                    "endpoint": "/api/install-readiness-final/check",
                    "payload": {"tenant_id": "owner-andre", "requested_project": project, "run_deep": True},
                    "safe_level": "gate",
                },
                *base,
            ]
        return base

    def run(self, command_id: str, tenant_id: str = "owner-andre", requested_project: str = "GOD_MODE") -> Dict[str, Any]:
        panel = self.build_panel(tenant_id=tenant_id, requested_project=requested_project)
        command = next((item for item in panel["commands"] if item["id"] == command_id), None)
        if not command:
            return {
                "ok": False,
                "mode": "home_command_wizard_run",
                "error": "unknown_command_id",
                "command_id": command_id,
                "available_command_ids": [item["id"] for item in panel["commands"]],
            }
        if command["endpoint"] == "/api/daily-command-router/route":
            result = daily_command_router_service.route(
                command_id=command["payload"]["command_id"],
                tenant_id=tenant_id,
                requested_project=requested_project,
            )
        elif command["endpoint"] == "/api/install-readiness-final/check":
            result = install_readiness_final_service.build_check(
                tenant_id=tenant_id,
                requested_project=requested_project,
                run_deep=True,
            )
        else:
            result = {"ok": False, "error": "unsupported_endpoint", "endpoint": command["endpoint"]}
        return {
            "ok": bool(result.get("ok", False)),
            "mode": "home_command_wizard_run",
            "command": command,
            "result": result,
            "operator_next": result.get("operator_next", {"label": "Voltar à Home", "route": "/app/home"}),
        }

    def get_status(self, tenant_id: str = "owner-andre") -> Dict[str, Any]:
        panel = self.build_panel(tenant_id=tenant_id)
        return {
            "ok": True,
            "mode": "home_command_wizard_status",
            "status": panel["status"],
            "project": panel["project"],
            "primary_command": panel["primary_command"],
            "command_count": len(panel["commands"]),
            "signals": panel["signals"],
        }

    def get_package(self, tenant_id: str = "owner-andre", requested_project: str = "GOD_MODE") -> Dict[str, Any]:
        return {
            "ok": True,
            "mode": "home_command_wizard_package",
            "package": {
                "status": self.get_status(tenant_id=tenant_id),
                "panel": self.build_panel(tenant_id=tenant_id, requested_project=requested_project),
            },
        }


home_command_wizard_service = HomeCommandWizardService()
