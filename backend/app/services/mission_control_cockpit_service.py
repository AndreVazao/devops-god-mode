from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List

from app.services.approved_card_execution_queue_service import approved_card_execution_queue_service
from app.services.memory_core_service import memory_core_service
from app.services.mobile_approval_cockpit_v2_service import mobile_approval_cockpit_v2_service
from app.services.operator_command_intake_service import operator_command_intake_service
from app.services.project_tree_sync_guard_service import project_tree_sync_guard_service
from app.services.system_integrity_audit_service import system_integrity_audit_service

PROJECTS = ["GOD_MODE", "PROVENTIL", "VERBAFORGE", "BOT_LORDS_MOBILE", "ECU_REPRO", "BUILD_CONTROL_CENTER"]


class MissionControlCockpitService:
    """One-screen operator cockpit for the God Mode mobile-first workflow."""

    def get_status(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "mode": "mission_control_cockpit_status",
            "status": "mission_control_ready",
            "memory_core_enabled": True,
            "mobile_first": True,
        }

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def _safe_call(self, label: str, fn: Any) -> Dict[str, Any]:
        try:
            result = fn()
            return {"ok": True, "label": label, "result": result}
        except Exception as exc:  # pragma: no cover - defensive cockpit shield
            return {"ok": False, "label": label, "error": str(exc)}

    def _project_score(self, project_name: str) -> Dict[str, Any]:
        memory = memory_core_service.read_project(project_name)
        files = memory.get("memory", {}) if memory.get("ok") else {}
        last_session = files.get("ULTIMA_SESSAO.md", "")
        backlog = files.get("BACKLOG.md", "")
        decisions = files.get("DECISOES.md", "")
        has_last_session = len(last_session.strip()) > 80
        has_backlog = "- [ ]" in backlog
        has_decisions = len(decisions.strip()) > 80
        score = 20 + (30 if has_last_session else 0) + (25 if has_backlog else 0) + (25 if has_decisions else 0)
        return {
            "project": project_name,
            "memory_score": min(score, 100),
            "has_last_session": has_last_session,
            "has_backlog": has_backlog,
            "has_decisions": has_decisions,
            "obsidian": memory_core_service.obsidian_link(project_name, "MEMORIA_MESTRE.md"),
        }

    def build_dashboard(self, tenant_id: str = "owner-andre") -> Dict[str, Any]:
        memory_core_service.initialize()
        operator = self._safe_call("operator_commands", lambda: operator_command_intake_service.list_commands(tenant_id=tenant_id, limit=20))
        approvals = self._safe_call("mobile_approvals", lambda: mobile_approval_cockpit_v2_service.build_dashboard(tenant_id=tenant_id))
        queue = self._safe_call("execution_queue", lambda: approved_card_execution_queue_service.build_dashboard(tenant_id=tenant_id))
        integrity = self._safe_call("system_integrity", lambda: system_integrity_audit_service.build_dashboard())
        tree = self._safe_call("project_tree", lambda: project_tree_sync_guard_service.build_dashboard())
        projects = [self._project_score(project) for project in PROJECTS]
        pending_approvals = approvals.get("result", {}).get("pending_approval_count", 0) if approvals.get("ok") else 0
        queued_tasks = queue.get("result", {}).get("queued_count", 0) if queue.get("ok") else 0
        integrity_status = integrity.get("result", {}).get("status", "unknown") if integrity.get("ok") else "error"
        tree_sync = tree.get("result", {}).get("in_sync", False) if tree.get("ok") else False
        readiness = "green" if pending_approvals == 0 and integrity_status in {"clean", "ready_with_attention"} and tree_sync else "yellow"
        if integrity_status == "blocked" or not integrity.get("ok") or not tree.get("ok"):
            readiness = "red"
        return {
            "ok": True,
            "mode": "mission_control_cockpit_dashboard",
            "created_at": self._now(),
            "tenant_id": tenant_id,
            "readiness": readiness,
            "summary": {
                "pending_approvals": pending_approvals,
                "queued_tasks": queued_tasks,
                "integrity_status": integrity_status,
                "project_tree_in_sync": tree_sync,
                "project_count": len(projects),
            },
            "projects": projects,
            "operator": operator,
            "approvals": approvals,
            "queue": queue,
            "integrity": integrity,
            "project_tree": tree,
            "quick_actions": [
                {"id": "submit-command", "label": "Enviar comando", "endpoint": "/api/operator-command-intake/submit", "method": "POST"},
                {"id": "open-memory", "label": "Abrir memória", "endpoint": "/app/memory-core", "method": "GET"},
                {"id": "open-approvals", "label": "Aprovações", "endpoint": "/app/mobile-approval-cockpit-v2", "method": "GET"},
                {"id": "open-integrity", "label": "Auditoria", "endpoint": "/app/system-integrity-audit", "method": "GET"},
            ],
        }

    def submit_mobile_command(self, command_text: str, project_hint: str = "GOD_MODE", tenant_id: str = "owner-andre") -> Dict[str, Any]:
        command = operator_command_intake_service.submit_command(
            command_text=command_text,
            tenant_id=tenant_id,
            project_hint=project_hint,
            source_channel="mission_control_cockpit",
        )
        if not command.get("ok"):
            return command
        card = mobile_approval_cockpit_v2_service.seed_from_latest_operator_command(tenant_id=tenant_id)
        return {"ok": True, "mode": "mission_control_submit_mobile_command", "command": command, "approval_card": card, "dashboard": self.build_dashboard(tenant_id=tenant_id)}

    def get_package(self) -> Dict[str, Any]:
        return {"ok": True, "mode": "mission_control_cockpit_package", "package": {"status": self.get_status(), "dashboard": self.build_dashboard()}}


mission_control_cockpit_service = MissionControlCockpitService()
