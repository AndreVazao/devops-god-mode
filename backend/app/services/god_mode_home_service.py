from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Callable, Dict, List
from uuid import uuid4

from app.services.memory_core_service import memory_core_service
from app.services.mobile_approval_cockpit_v2_service import mobile_approval_cockpit_v2_service
from app.services.operator_priority_service import operator_priority_service


class GodModeHomeService:
    """Unified mobile-first home cockpit.

    One screen, many engines underneath. The operator project order is the source
    of truth. Money is a consequence of shipping/fixing projects, not the routing
    priority for this cockpit.
    """

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def _safe(self, label: str, fn: Callable[[], Any]) -> Dict[str, Any]:
        try:
            value = fn()
            return value if isinstance(value, dict) else {"ok": True, "mode": label, "value": value}
        except Exception as exc:
            return {"ok": False, "mode": label, "error": exc.__class__.__name__, "detail": str(exc)[:300]}

    def _chat_bridge(self):
        from app.services.operator_chat_real_work_bridge_service import operator_chat_real_work_bridge_service
        return operator_chat_real_work_bridge_service

    def _chat_autopilot(self):
        from app.services.chat_autopilot_supervisor_service import chat_autopilot_supervisor_service
        return chat_autopilot_supervisor_service

    def _pc_autopilot(self):
        from app.services.pc_autopilot_loop_service import pc_autopilot_loop_service
        return pc_autopilot_loop_service

    def _real_work(self):
        from app.services.real_work_command_pipeline_service import real_work_command_pipeline_service
        return real_work_command_pipeline_service

    def _ready_to_use(self):
        from app.services.ready_to_use_home_check_service import ready_to_use_home_check_service
        return ready_to_use_home_check_service

    def _install_guide(self):
        from app.services.install_first_run_guide_service import install_first_run_guide_service
        return install_first_run_guide_service

    def _artifacts(self):
        from app.services.artifacts_center_service import artifacts_center_service
        return artifacts_center_service

    def _health(self):
        from app.services.home_system_health_service import home_system_health_service
        return home_system_health_service

    def _pending_approvals(self, tenant_id: str = "owner-andre") -> Dict[str, Any]:
        cards = mobile_approval_cockpit_v2_service.list_cards(tenant_id=tenant_id, status="pending_approval", limit=50)
        return {"ok": cards.get("ok", False), "count": cards.get("card_count", 0), "cards": cards.get("cards", [])}

    def _latest_result(self) -> Dict[str, Any]:
        return {
            "chat": self._safe("chat_latest", self._chat_bridge().latest).get("report"),
            "real_work": self._safe("real_work_latest", self._real_work().latest).get("report"),
            "chat_autopilot": self._safe("chat_autopilot_latest", self._chat_autopilot().latest).get("report"),
            "pc_autopilot": self._safe("pc_autopilot_latest", self._pc_autopilot().latest).get("cycle"),
        }

    def _traffic_light(self, dashboard: Dict[str, Any]) -> Dict[str, str]:
        approvals = dashboard.get("approvals", {})
        health = dashboard.get("home_system_health", {})
        ready = dashboard.get("ready_to_use", {})
        pc_status = dashboard.get("pc_autopilot", {}).get("status")
        if approvals.get("count", 0) > 0:
            return {"color": "yellow", "label": "Precisa do teu OK", "reason": "pending_approval"}
        if health.get("status") == "blocked":
            return {"color": "red", "label": "Sistema bloqueado", "reason": "health_blocked"}
        if health.get("status") == "attention":
            return {"color": "yellow", "label": "Sistema precisa atenção", "reason": "health_attention"}
        if ready.get("status") == "not_ready":
            return {"color": "red", "label": "Ainda não está pronto", "reason": "ready_to_use_blockers"}
        if ready.get("status") == "almost_ready":
            return {"color": "yellow", "label": "Quase pronto", "reason": "ready_to_use_partial"}
        if pc_status == "running":
            return {"color": "green", "label": "PC a trabalhar", "reason": "pc_autopilot_running"}
        if pc_status == "enabled_idle":
            return {"color": "green", "label": "Pronto", "reason": "pc_autopilot_enabled"}
        return {"color": "blue", "label": "Pronto para ordem", "reason": "waiting_operator_command"}

    def _next_task(self, dashboard: Dict[str, Any]) -> Dict[str, str]:
        if dashboard.get("approvals", {}).get("count", 0) > 0:
            return {"kind": "approval", "label": "Decidir aprovações pendentes", "route": "/app/mobile-approval-cockpit-v2", "priority": "critical"}
        health = dashboard.get("home_system_health", {})
        if health.get("blocker_count", 0) > 0 and health.get("next_action"):
            return health["next_action"]
        ready = dashboard.get("ready_to_use", {})
        if ready.get("status") in {"not_ready", "almost_ready"} and ready.get("next_action"):
            return ready["next_action"]
        if dashboard.get("pc_autopilot", {}).get("status") == "disabled":
            return {"kind": "autopilot", "label": "Ligar PC Autopilot", "endpoint": "/api/god-mode-home/start-autopilot", "priority": "high"}
        latest_chat = dashboard.get("latest_result", {}).get("chat") or {}
        if latest_chat.get("job_id"):
            return {"kind": "job", "label": f"Acompanhar job {latest_chat.get('job_id')}", "route": "/app/operator-chat-sync-cards", "priority": "medium"}
        return {"kind": "command", "label": "Dar próxima ordem no chat", "route": "/app/operator-chat-sync-cards", "priority": "high"}

    def _quick_actions(self) -> List[Dict[str, str]]:
        return [
            {"id": "chat", "label": "Chat", "route": "/app/operator-chat-sync-cards", "priority": "critical"},
            {"id": "first_real_install_launcher", "label": "Instalar agora", "endpoint": "/api/first-real-install-launcher/plan", "priority": "critical"},
            {"id": "continue", "label": "Continuar", "endpoint": "/api/god-mode-home/continue", "priority": "critical"},
            {"id": "easy", "label": "Modo fácil", "endpoint": "/api/home-operator-ux/panel", "priority": "critical"},
            {"id": "install_readiness_final", "label": "Instalação final", "endpoint": "/api/install-readiness-final/check", "priority": "critical"},
            {"id": "health", "label": "Saúde", "endpoint": "/api/home-system-health/snapshot", "priority": "critical"},
            {"id": "install", "label": "Instalar/1º arranque", "endpoint": "/api/install-first-run/guide", "priority": "critical"},
            {"id": "artifacts", "label": "APK/EXE", "endpoint": "/api/artifacts-center/dashboard", "priority": "critical"},
            {"id": "start_autopilot", "label": "Ligar PC Autopilot", "endpoint": "/api/god-mode-home/start-autopilot", "priority": "high"},
            {"id": "stop_autopilot", "label": "Parar", "endpoint": "/api/god-mode-home/stop-autopilot", "priority": "medium"},
            {"id": "approve_next", "label": "Aprovar próximo", "endpoint": "/api/god-mode-home/approve-next", "priority": "high"},
            {"id": "ready", "label": "Pronto para usar", "endpoint": "/api/ready-to-use/checklist", "priority": "high"},
            {"id": "problems", "label": "Ver problemas", "route": "/app/mobile-approval-cockpit-v2", "priority": "high"},
            {"id": "priority", "label": "Prioridades", "route": "/app/operator-priority", "priority": "medium"},
            {"id": "pc_loop", "label": "PC Loop", "route": "/app/pc-autopilot", "priority": "medium"},
        ]

    def build_dashboard(self, tenant_id: str = "owner-andre") -> Dict[str, Any]:
        priority = self._safe("operator_priority", operator_priority_service.get_status)
        active_project = priority.get("active_project") or "GOD_MODE"
        memory = self._safe("memory_context", lambda: memory_core_service.compact_context(active_project, max_chars=1600))
        pc_raw = self._safe("pc_autopilot", self._pc_autopilot().get_status)
        ready = self._safe("ready_to_use", lambda: self._ready_to_use().get_status(tenant_id=tenant_id))
        install = self._safe("install_first_run", lambda: self._install_guide().get_status(tenant_id=tenant_id))
        artifacts = self._safe("artifacts_center", self._artifacts().get_status)
        health = self._safe("home_system_health", lambda: self._health().get_status(tenant_id=tenant_id))
        dashboard = {
            "ok": True,
            "mode": "god_mode_home_dashboard",
            "created_at": self._now(),
            "tenant_id": tenant_id,
            "policy": "one_home_screen_controls_specialized_cockpits",
            "money_priority_enabled": False,
            "home_routes": ["/app/home", "/app/god-mode", "/app/god-mode-home"],
            "operator_priority": priority,
            "active_project": active_project,
            "chat": self._safe("operator_chat_real_work", self._chat_bridge().get_status),
            "pc_autopilot": pc_raw,
            "chat_autopilot": self._safe("chat_autopilot", self._chat_autopilot().get_status),
            "real_work": self._safe("real_work", self._real_work().get_status),
            "approvals": self._safe("pending_approvals", lambda: self._pending_approvals(tenant_id)),
            "ready_to_use": ready,
            "install_first_run": install,
            "artifacts_center": artifacts,
            "home_system_health": health,
            "memory": {"ok": memory.get("ok", False), "active_project": active_project, "chars": memory.get("chars", 0), "preview": (memory.get("context") or "")[-700:]},
            "latest_result": self._latest_result(),
        }
        dashboard["traffic_light"] = self._traffic_light(dashboard)
        dashboard["next_task"] = self._next_task(dashboard)
        dashboard["quick_actions"] = self._quick_actions()
        dashboard["operator_message"] = f"{dashboard['traffic_light']['label']} · {dashboard['next_task'].get('label', 'Dar ordem no chat')}"
        return dashboard

    def get_status(self, tenant_id: str = "owner-andre") -> Dict[str, Any]:
        dashboard = self.build_dashboard(tenant_id=tenant_id)
        return {
            "ok": True,
            "mode": "god_mode_home_status",
            "traffic_light": dashboard["traffic_light"],
            "active_project": dashboard["active_project"],
            "pc_autopilot_status": dashboard["pc_autopilot"].get("status"),
            "pending_approval_count": dashboard["approvals"].get("count", 0),
            "ready_to_use": dashboard["ready_to_use"],
            "install_first_run": dashboard["install_first_run"],
            "artifacts_center": dashboard["artifacts_center"],
            "home_system_health": dashboard["home_system_health"],
            "next_task": dashboard["next_task"],
            "money_priority_enabled": False,
        }

    def get_package(self, tenant_id: str = "owner-andre") -> Dict[str, Any]:
        return {"ok": True, "mode": "god_mode_home_package", "package": {"status": self.get_status(tenant_id), "dashboard": self.build_dashboard(tenant_id)}}

    def continue_work(self, command_text: str | None = None, tenant_id: str = "owner-andre", requested_project: str | None = None) -> Dict[str, Any]:
        resolved = operator_priority_service.resolve_project(requested_project)
        project = (resolved.get("project") or {}).get("project_id") or "GOD_MODE"
        command = command_text or f"continua o projeto {project} até precisares do meu OK"
        result = self._chat_bridge().submit_chat_command(message=command, tenant_id=tenant_id, requested_project=project, auto_run=True)
        memory_core_service.write_history(project, "God Mode Home continue", f"Command: {command}")
        return {"ok": True, "mode": "god_mode_home_continue", "action_id": f"home-continue-{uuid4().hex[:12]}", "project": project, "command": command, "result": result, "dashboard": self.build_dashboard(tenant_id)}

    def start_autopilot(self) -> Dict[str, Any]:
        result = self._pc_autopilot().start()
        return {"ok": True, "mode": "god_mode_home_start_autopilot", "result": result, "dashboard": self.build_dashboard()}

    def stop_autopilot(self) -> Dict[str, Any]:
        result = self._pc_autopilot().stop()
        return {"ok": True, "mode": "god_mode_home_stop_autopilot", "result": result, "dashboard": self.build_dashboard()}

    def approve_next(self, tenant_id: str = "owner-andre", operator_note: str = "Approved from God Mode Home") -> Dict[str, Any]:
        pending = self._pending_approvals(tenant_id=tenant_id)
        cards = pending.get("cards", [])
        if not cards:
            return {"ok": False, "mode": "god_mode_home_approve_next", "error": "no_pending_approval", "dashboard": self.build_dashboard(tenant_id)}
        card = cards[-1]
        decision = mobile_approval_cockpit_v2_service.decide_card(card_id=card["card_id"], decision="approved", operator_note=operator_note, tenant_id=tenant_id)
        return {"ok": decision.get("ok", False), "mode": "god_mode_home_approve_next", "decision": decision, "dashboard": self.build_dashboard(tenant_id)}

    def chat(self, message: str, tenant_id: str = "owner-andre", requested_project: str | None = None) -> Dict[str, Any]:
        result = self._chat_bridge().submit_chat_command(message=message, tenant_id=tenant_id, requested_project=requested_project, auto_run=True)
        return {"ok": True, "mode": "god_mode_home_chat", "result": result, "dashboard": self.build_dashboard(tenant_id)}

    def driving_mode(self, tenant_id: str = "owner-andre") -> Dict[str, Any]:
        dashboard = self.build_dashboard(tenant_id=tenant_id)
        next_task = dashboard.get("next_task", {})
        ready = dashboard.get("ready_to_use", {})
        install = dashboard.get("install_first_run", {})
        artifacts = dashboard.get("artifacts_center", {})
        health = dashboard.get("home_system_health", {})
        return {"ok": True, "mode": "god_mode_home_driving_mode", "speakable": [dashboard.get("operator_message", "Pronto."), f"Saúde: {health.get('health_score', 0)} por cento.", f"Prontidão: {ready.get('readiness_score', 0)} por cento.", f"Instalação: {install.get('done_count', 0)} passos prontos.", f"Artifacts: {artifacts.get('artifact_count', 0)} pacotes previstos.", f"Próxima ação: {next_task.get('label', 'dar ordem no chat')}", "Não escrevas dados sensíveis no chat."], "safe_buttons": [next_task, *dashboard.get("quick_actions", [])[:4]]}


god_mode_home_service = GodModeHomeService()
