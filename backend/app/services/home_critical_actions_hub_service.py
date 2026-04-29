from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, List
from uuid import uuid4

from app.utils.atomic_json_store import AtomicJsonStore

DATA_DIR = Path("data")
HUB_FILE = DATA_DIR / "home_critical_actions_hub.json"
HUB_STORE = AtomicJsonStore(
    HUB_FILE,
    default_factory=lambda: {
        "version": 1,
        "policy": "single_mobile_first_hub_for_recent_critical_modules",
        "snapshots": [],
    },
)


class HomeCriticalActionsHubService:
    """Mobile-first hub for the latest critical God Mode modules.

    This hub prevents important phases from becoming hidden backend-only modules.
    It exposes a compact, button-driven control surface for Home/Modo Fácil.
    """

    MODULES = [
        {
            "id": "real_completion",
            "label": "Estado real %",
            "endpoint": "/api/god-mode-completion/panel",
            "status_endpoint": "/api/god-mode-completion/status",
            "priority": "critical",
            "purpose": "ver percentagem real até 100%",
        },
        {
            "id": "pc_migration",
            "label": "Setup automático PC",
            "endpoint": "/api/pc-migration-control/panel",
            "action_endpoint": "/api/pc-migration-control/auto-setup",
            "status_endpoint": "/api/pc-migration-control/status",
            "priority": "critical",
            "purpose": "scan, ferramentas, backup e restore",
        },
        {
            "id": "autonomous_delivery",
            "label": "Entrega automática",
            "endpoint": "/api/autonomous-delivery/panel",
            "action_endpoint": "/api/autonomous-delivery/run",
            "status_endpoint": "/api/autonomous-delivery/status",
            "priority": "critical",
            "purpose": "instalar, pesquisar e gerar código",
        },
        {
            "id": "memory_providers",
            "label": "Memória / providers",
            "endpoint": "/api/memory-context-router/panel",
            "action_endpoint": "/api/memory-context-router/prepare-priority-projects",
            "status_endpoint": "/api/memory-context-router/status",
            "priority": "critical",
            "purpose": "preparar AndreOS/Obsidian e contexto compacto",
        },
        {
            "id": "new_project",
            "label": "Projeto novo",
            "endpoint": "/api/new-project-start/panel",
            "status_endpoint": "/api/new-project-start/status",
            "priority": "critical",
            "purpose": "começar projeto do zero",
        },
        {
            "id": "approved_queue_mobile",
            "label": "Fila aprovada",
            "endpoint": "/api/approved-work-queue-mobile/panel",
            "action_endpoint": "/api/approved-work-queue-mobile/run-safe",
            "status_endpoint": "/api/approved-work-queue-mobile/status",
            "priority": "critical",
            "purpose": "executar passos seguros e ver gates",
        },
        {
            "id": "local_tools",
            "label": "Ferramentas locais",
            "endpoint": "/api/local-tool-capability/panel",
            "action_endpoint": "/api/local-tool-capability/scan",
            "status_endpoint": "/api/local-tool-capability/status",
            "priority": "high",
            "purpose": "check-up das ferramentas do PC",
        },
        {
            "id": "bootstrap_backup",
            "label": "Backup portátil",
            "endpoint": "/api/local-bootstrap-backup/panel",
            "action_endpoint": "/api/local-bootstrap-backup/create-backup",
            "status_endpoint": "/api/local-bootstrap-backup/status",
            "priority": "high",
            "purpose": "instalação/configuração e backup copiável",
        },
        {
            "id": "restore_approved",
            "label": "Restore aprovado",
            "endpoint": "/api/restore-approved/panel",
            "status_endpoint": "/api/restore-approved/status",
            "priority": "high",
            "purpose": "restore seguro no PC novo",
        },
        {
            "id": "external_chat_cleanup",
            "label": "Limpar chats IA",
            "endpoint": "/api/external-chat-cleanup/panel",
            "status_endpoint": "/api/external-chat-cleanup/status",
            "priority": "high",
            "purpose": "extrair contexto e limpar conversas antigas",
        },
        {
            "id": "provider_delivery",
            "label": "Resolver provider",
            "endpoint": "/api/provider-delivery-router/panel",
            "status_endpoint": "/api/provider-delivery-router/status",
            "priority": "high",
            "purpose": "continuar entrega quando provider falhar/limitar",
        },
    ]

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def _safe_import_status(self, module: Dict[str, Any]) -> Dict[str, Any]:
        service_map: Dict[str, Callable[[], Dict[str, Any]]] = {
            "real_completion": lambda: __import__("app.services.god_mode_real_completion_scorecard_service", fromlist=["god_mode_real_completion_scorecard_service"]).god_mode_real_completion_scorecard_service.get_status(),
            "pc_migration": lambda: __import__("app.services.pc_migration_control_center_service", fromlist=["pc_migration_control_center_service"]).pc_migration_control_center_service.get_status(),
            "autonomous_delivery": lambda: __import__("app.services.autonomous_install_research_code_service", fromlist=["autonomous_install_research_code_service"]).autonomous_install_research_code_service.get_status(),
            "memory_providers": lambda: __import__("app.services.memory_context_router_service", fromlist=["memory_context_router_service"]).memory_context_router_service.get_status(),
            "new_project": lambda: __import__("app.services.new_project_start_intake_service", fromlist=["new_project_start_intake_service"]).new_project_start_intake_service.get_status(),
            "approved_queue_mobile": lambda: __import__("app.services.approved_work_queue_mobile_panel_service", fromlist=["approved_work_queue_mobile_panel_service"]).approved_work_queue_mobile_panel_service.get_status(),
            "local_tools": lambda: __import__("app.services.local_tool_capability_scan_service", fromlist=["local_tool_capability_scan_service"]).local_tool_capability_scan_service.get_status(),
            "bootstrap_backup": lambda: __import__("app.services.local_bootstrap_backup_service", fromlist=["local_bootstrap_backup_service"]).local_bootstrap_backup_service.get_status(),
            "restore_approved": lambda: __import__("app.services.restore_approved_runner_service", fromlist=["restore_approved_runner_service"]).restore_approved_runner_service.get_status(),
            "external_chat_cleanup": lambda: __import__("app.services.external_chat_cleanup_archive_service", fromlist=["external_chat_cleanup_archive_service"]).external_chat_cleanup_archive_service.get_status(),
            "provider_delivery": lambda: __import__("app.services.provider_completion_router_service", fromlist=["provider_completion_router_service"]).provider_completion_router_service.get_status(),
        }
        try:
            status = service_map[module["id"]]()
            return status if isinstance(status, dict) else {"ok": True, "value": status}
        except Exception as exc:
            return {"ok": False, "error": exc.__class__.__name__, "detail": str(exc)[:300]}

    def snapshot(self) -> Dict[str, Any]:
        modules = []
        for module in self.MODULES:
            status = self._safe_import_status(module)
            modules.append({**module, "status": status, "traffic_light": self._module_light(module, status)})
        overall = self._overall(modules)
        snapshot = {
            "snapshot_id": f"home-critical-actions-{uuid4().hex[:12]}",
            "created_at": self._now(),
            "mode": "home_critical_actions_hub",
            "headline": "God Mode — ações críticas",
            "overall": overall,
            "primary_cards": [item for item in modules if item.get("priority") == "critical"],
            "secondary_cards": [item for item in modules if item.get("priority") != "critical"],
            "quick_buttons": self._quick_buttons(modules),
            "operator_next": self._operator_next(modules, overall),
            "mobile_rules": [
                "botões grandes",
                "um ecrã principal",
                "mostrar percentagem real",
                "priorizar setup, memória, entrega e fila",
                "parar só em login, aprovação, bloqueio ou conclusão",
            ],
        }
        self._store(snapshot)
        return {"ok": True, "mode": "home_critical_actions_hub_snapshot", "snapshot": snapshot}

    def _module_light(self, module: Dict[str, Any], status: Dict[str, Any]) -> Dict[str, str]:
        if not status.get("ok", False):
            return {"color": "red", "label": "atenção", "reason": status.get("error", "not_ok")}
        if module["id"] == "real_completion":
            percent = status.get("overall_percent", 0) or 0
            if percent >= 85:
                return {"color": "green", "label": f"{percent}%", "reason": "near_real_use"}
            if percent >= 70:
                return {"color": "yellow", "label": f"{percent}%", "reason": "advanced_needs_tests"}
            return {"color": "red", "label": f"{percent}%", "reason": "needs_work"}
        if module["id"] == "pc_migration" and status.get("auto_mode_enabled"):
            return {"color": "green", "label": "auto", "reason": "auto_mode_enabled"}
        return {"color": "green", "label": "ok", "reason": "module_available"}

    def _overall(self, modules: List[Dict[str, Any]]) -> Dict[str, Any]:
        red = len([m for m in modules if m["traffic_light"]["color"] == "red"])
        yellow = len([m for m in modules if m["traffic_light"]["color"] == "yellow"])
        green = len([m for m in modules if m["traffic_light"]["color"] == "green"])
        if red:
            return {"color": "red", "label": "há módulos críticos com erro", "green": green, "yellow": yellow, "red": red}
        if yellow:
            return {"color": "yellow", "label": "avançado, mas precisa testes reais", "green": green, "yellow": yellow, "red": red}
        return {"color": "green", "label": "hub pronto", "green": green, "yellow": yellow, "red": red}

    def _quick_buttons(self, modules: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        buttons = []
        for module in modules:
            buttons.append({
                "id": module["id"],
                "label": module["label"],
                "endpoint": module["endpoint"],
                "action_endpoint": module.get("action_endpoint"),
                "priority": module["priority"],
            })
        return buttons

    def _operator_next(self, modules: List[Dict[str, Any]], overall: Dict[str, Any]) -> Dict[str, Any]:
        completion = next((m for m in modules if m["id"] == "real_completion"), None)
        completion_percent = ((completion or {}).get("status") or {}).get("overall_percent", 0) or 0
        if completion_percent < 85:
            return {"label": "Subir percentagem real", "endpoint": "/api/god-mode-completion/panel", "priority": "critical"}
        pc = next((m for m in modules if m["id"] == "pc_migration"), None)
        if pc and pc.get("status", {}).get("auto_run_count", 0) == 0:
            return {"label": "Executar setup automático", "endpoint": "/api/pc-migration-control/auto-setup", "priority": "critical"}
        return {"label": "Continuar entrega automática", "endpoint": "/api/autonomous-delivery/run", "priority": "critical"}

    def _store(self, snapshot: Dict[str, Any]) -> None:
        def mutate(state: Dict[str, Any]) -> Dict[str, Any]:
            state.setdefault("version", 1)
            state.setdefault("policy", "single_mobile_first_hub_for_recent_critical_modules")
            state.setdefault("snapshots", [])
            state["snapshots"].append(snapshot)
            state["snapshots"] = state["snapshots"][-100:]
            return state
        HUB_STORE.update(mutate)

    def latest(self) -> Dict[str, Any]:
        state = HUB_STORE.load()
        snapshots = state.get("snapshots") or []
        return {"ok": True, "mode": "home_critical_actions_latest", "latest_snapshot": snapshots[-1] if snapshots else None, "snapshot_count": len(snapshots)}

    def get_status(self) -> Dict[str, Any]:
        latest = self.latest().get("latest_snapshot")
        if not latest:
            latest = self.snapshot().get("snapshot")
        return {
            "ok": True,
            "mode": "home_critical_actions_status",
            "overall": latest.get("overall"),
            "primary_count": len(latest.get("primary_cards") or []),
            "secondary_count": len(latest.get("secondary_cards") or []),
            "operator_next": latest.get("operator_next"),
        }

    def get_package(self) -> Dict[str, Any]:
        return {"ok": True, "mode": "home_critical_actions_package", "package": {"status": self.get_status(), "snapshot": self.snapshot(), "latest": self.latest()}}


home_critical_actions_hub_service = HomeCriticalActionsHubService()
