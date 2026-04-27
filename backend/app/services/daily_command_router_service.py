from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List
from uuid import uuid4


class DailyCommandRouterService:
    """Tiny daily command router for the operator Home UX.

    It turns stable button IDs into safe backend actions so the mobile operator
    does not need to memorize technical commands.
    """

    COMMANDS = {
        "continue_active_project": {
            "label": "Continuar projeto ativo",
            "kind": "chat_command",
            "template": "continua o projeto {project} até terminares ou precisares do meu OK",
        },
        "fix_blockers": {
            "label": "Corrigir blockers",
            "kind": "chat_command",
            "template": "analisa os blockers do {project}, cria plano curto e executa o que for seguro sem contornar aprovações",
        },
        "prepare_install": {
            "label": "Preparar instalação",
            "kind": "read_endpoint",
            "endpoint": "/api/install-first-run/guide",
        },
        "summarize_next": {
            "label": "Resumo curto",
            "kind": "chat_command",
            "template": "dá-me só o estado atual do {project}, próximo passo e o que precisa do meu OK",
        },
        "show_health": {
            "label": "Ver saúde",
            "kind": "read_endpoint",
            "endpoint": "/api/home-system-health/snapshot",
        },
        "show_artifacts": {
            "label": "Ver APK/EXE",
            "kind": "read_endpoint",
            "endpoint": "/api/artifacts-center/dashboard",
        },
    }

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def _priority(self):
        from app.services.operator_priority_service import operator_priority_service

        return operator_priority_service

    def _chat(self):
        from app.services.operator_chat_real_work_bridge_service import operator_chat_real_work_bridge_service

        return operator_chat_real_work_bridge_service

    def _install(self):
        from app.services.install_first_run_guide_service import install_first_run_guide_service

        return install_first_run_guide_service

    def _health(self):
        from app.services.home_system_health_service import home_system_health_service

        return home_system_health_service

    def _artifacts(self):
        from app.services.artifacts_center_service import artifacts_center_service

        return artifacts_center_service

    def available_commands(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "mode": "daily_command_router_commands",
            "commands": [
                {"id": command_id, "label": spec["label"], "kind": spec["kind"], "endpoint": spec.get("endpoint")}
                for command_id, spec in self.COMMANDS.items()
            ],
        }

    def route(self, command_id: str, tenant_id: str = "owner-andre", requested_project: str | None = None) -> Dict[str, Any]:
        spec = self.COMMANDS.get(command_id)
        if not spec:
            return {
                "ok": False,
                "mode": "daily_command_router_result",
                "error": "unknown_command_id",
                "command_id": command_id,
                "available_command_ids": sorted(self.COMMANDS.keys()),
            }
        resolved_project = self._resolve_project(requested_project)
        route_id = f"daily-route-{uuid4().hex[:12]}"
        if spec["kind"] == "chat_command":
            message = spec["template"].format(project=resolved_project)
            result = self._chat().submit_chat_command(
                message=message,
                tenant_id=tenant_id,
                requested_project=resolved_project,
                auto_run=True,
            )
            return {
                "ok": True,
                "mode": "daily_command_router_result",
                "route_id": route_id,
                "command_id": command_id,
                "label": spec["label"],
                "kind": "chat_command",
                "project": resolved_project,
                "message": message,
                "result": result,
                "operator_next": self._operator_next(result),
            }
        if command_id == "prepare_install":
            result = self._install().build_guide(tenant_id=tenant_id)
        elif command_id == "show_health":
            result = self._health().build_snapshot(tenant_id=tenant_id)
        elif command_id == "show_artifacts":
            result = self._artifacts().build_dashboard()
        else:
            result = {"ok": False, "error": "unhandled_read_endpoint"}
        return {
            "ok": bool(result.get("ok", False)),
            "mode": "daily_command_router_result",
            "route_id": route_id,
            "command_id": command_id,
            "label": spec["label"],
            "kind": "read_endpoint",
            "endpoint": spec.get("endpoint"),
            "project": resolved_project,
            "result": result,
            "operator_next": {"label": "Rever resultado", "route": "/app/home"},
        }

    def _resolve_project(self, requested_project: str | None = None) -> str:
        resolved = self._priority().resolve_project(requested_project)
        return (resolved.get("project") or {}).get("project_id") or requested_project or "GOD_MODE"

    def _operator_next(self, result: Dict[str, Any]) -> Dict[str, Any]:
        report = result.get("report", {}) if isinstance(result, dict) else {}
        if report.get("autopilot_stop_reason") in {"blocked_waiting_operator", "approval_required"}:
            return {"label": "Abrir aprovações", "route": "/app/mobile-approval-cockpit-v2"}
        if report.get("job_id"):
            return {"label": "Acompanhar job", "route": "/app/operator-chat-sync-cards", "job_id": report.get("job_id")}
        return {"label": "Voltar à Home", "route": "/app/home"}

    def get_status(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "mode": "daily_command_router_status",
            "command_count": len(self.COMMANDS),
            "command_ids": sorted(self.COMMANDS.keys()),
            "created_at": self._now(),
        }

    def get_package(self) -> Dict[str, Any]:
        return {"ok": True, "mode": "daily_command_router_package", "package": {"status": self.get_status(), "commands": self.available_commands()}}


daily_command_router_service = DailyCommandRouterService()
