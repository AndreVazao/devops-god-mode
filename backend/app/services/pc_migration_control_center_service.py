from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import uuid4

from app.services.local_tool_capability_scan_service import local_tool_capability_scan_service
from app.services.local_bootstrap_backup_service import local_bootstrap_backup_service
from app.services.restore_approved_runner_service import restore_approved_runner_service
from app.services.memory_context_router_service import memory_context_router_service
from app.utils.atomic_json_store import AtomicJsonStore

DATA_DIR = Path("data")
CENTER_FILE = DATA_DIR / "pc_migration_control_center.json"
CENTER_STORE = AtomicJsonStore(
    CENTER_FILE,
    default_factory=lambda: {
        "version": 1,
        "policy": "automatic_pc_setup_with_operator_gates",
        "sessions": [],
        "auto_runs": [],
    },
)


class PcMigrationControlCenterService:
    """Mobile-first control center for first run, tool setup, backup and restore.

    The goal is zero manual configuration whenever possible. The service runs
    safe automation automatically and stops only for operator approval when an
    action can install software, overwrite files, or require manual login.
    """

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def build_session(self, pc_profile: str = "auto", intent: str = "first_run_or_migration") -> Dict[str, Any]:
        session_id = f"pc-migration-session-{uuid4().hex[:12]}"
        tool_status = local_tool_capability_scan_service.get_status()
        bootstrap_status = local_bootstrap_backup_service.get_status()
        restore_status = restore_approved_runner_service.get_status()
        memory_status = memory_context_router_service.get_status()
        session = {
            "session_id": session_id,
            "created_at": self._now(),
            "pc_profile": pc_profile,
            "intent": intent,
            "mode": "pc_migration_control_center",
            "status": "ready_for_auto_or_operator_action",
            "traffic_light": self._traffic_light(tool_status, bootstrap_status, restore_status, memory_status),
            "summary_cards": self._summary_cards(tool_status, bootstrap_status, restore_status, memory_status),
            "flows": self._flows(pc_profile=pc_profile),
            "auto_mode": self.auto_mode_policy(),
            "safe_buttons": self._safe_buttons(),
            "operator_next": self._operator_next(tool_status, bootstrap_status, restore_status, memory_status),
        }
        self._store_session(session)
        return {"ok": True, "mode": "pc_migration_control_session", "session": session}

    def auto_mode_policy(self) -> Dict[str, Any]:
        return {
            "enabled": True,
            "label": "Piloto automático de setup",
            "what_runs_automatically": [
                "check-up do PC",
                "plano de ferramentas em falta",
                "geração de script de instalação/configuração",
                "preparação de memória AndreOS/Obsidian",
                "backup portátil",
                "painel de próxima ação",
            ],
            "what_stops_for_operator": [
                "executar script que instala ferramentas",
                "login manual em browsers/providers",
                "restore que sobrescreve ficheiros",
                "rollback",
                "qualquer ação com dados sensíveis",
            ],
            "configuration_principle": "auto-detectar caminhos e defaults; não pedir configuração manual quando for possível inferir com segurança",
        }

    def auto_setup(
        self,
        pc_profile: str = "auto",
        include_backup: bool = True,
        backup_destination_path: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Run every safe first-run step automatically.

        This creates local state, scripts and backup files, but does not execute
        installers and does not restore/overwrite user files.
        """
        run_id = f"pc-auto-setup-{uuid4().hex[:12]}"
        steps: List[Dict[str, Any]] = []

        scan_result = local_tool_capability_scan_service.scan()
        steps.append(self._step("scan_pc", "Check-up do PC", scan_result))

        bootstrap_plan = local_bootstrap_backup_service.bootstrap_plan(pc_profile=pc_profile)
        steps.append(self._step("bootstrap_plan", "Plano de ferramentas", bootstrap_plan))

        install_script = local_bootstrap_backup_service.install_script(pc_profile=pc_profile)
        steps.append(self._step("install_script", "Script de instalação/configuração", install_script))

        memory_result = memory_context_router_service.prepare_priority_projects(limit=30)
        steps.append(self._step("prepare_memory", "Preparar memórias dos projetos", memory_result))

        backup_result = None
        if include_backup:
            backup_result = local_bootstrap_backup_service.create_backup(destination_path=backup_destination_path, include_data=True)
            steps.append(self._step("portable_backup", "Backup portátil", backup_result))

        session = self.build_session(pc_profile=pc_profile, intent="auto_setup")
        auto_run = {
            "run_id": run_id,
            "created_at": self._now(),
            "pc_profile": pc_profile,
            "include_backup": include_backup,
            "status": "completed_safe_steps",
            "steps": steps,
            "install_script_path": (install_script.get("script_path") if isinstance(install_script, dict) else None),
            "backup_path": ((backup_result or {}).get("backup") or {}).get("zip_path") if backup_result else None,
            "blocked_until_operator": [
                {
                    "id": "run_install_script",
                    "label": "Executar script de instalação/configuração no PC",
                    "reason": "pode instalar software e alterar o sistema",
                    "operator_action": True,
                },
                {
                    "id": "restore_backup",
                    "label": "Restaurar backup no PC novo",
                    "reason": "pode sobrescrever ficheiros existentes",
                    "endpoint": "/api/restore-approved/run",
                    "requires_phrase": "RESTORE GOD MODE",
                },
            ],
            "session": session.get("session"),
        }
        self._store_auto_run(auto_run)
        return {"ok": True, "mode": "pc_migration_auto_setup", "auto_run": auto_run}

    def _step(self, step_id: str, label: str, result: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "step_id": step_id,
            "label": label,
            "ok": bool(result.get("ok", False)) if isinstance(result, dict) else False,
            "mode": result.get("mode") if isinstance(result, dict) else None,
            "result": result,
        }

    def _traffic_light(self, tool_status: Dict[str, Any], bootstrap_status: Dict[str, Any], restore_status: Dict[str, Any], memory_status: Dict[str, Any]) -> Dict[str, str]:
        if tool_status.get("status") == "not_scanned_yet":
            return {"color": "blue", "label": "Pronto para setup automático", "reason": "local_scan_missing"}
        if bootstrap_status.get("backup_count", 0) == 0:
            return {"color": "yellow", "label": "Falta backup portátil", "reason": "no_backup_yet"}
        if restore_status.get("restore_run_count", 0) > 0:
            return {"color": "green", "label": "PC restaurado", "reason": "restore_done"}
        return {"color": "green", "label": "Setup preparado", "reason": "scan_and_backup_available"}

    def _summary_cards(self, tool_status: Dict[str, Any], bootstrap_status: Dict[str, Any], restore_status: Dict[str, Any], memory_status: Dict[str, Any]) -> List[Dict[str, Any]]:
        return [
            {"id": "auto_setup", "title": "Setup automático", "status": "ready", "summary": "Executa check-up, plano, script, memória e backup num só fluxo.", "action": {"label": "Executar auto setup", "endpoint": "/api/pc-migration-control/auto-setup"}},
            {"id": "local_scan", "title": "Check-up do PC", "status": tool_status.get("status"), "value": tool_status, "action": {"label": "Fazer check-up", "endpoint": "/api/local-tool-capability/scan"}},
            {"id": "tools", "title": "Ferramentas", "status": "planned", "value": bootstrap_status, "action": {"label": "Plano ferramentas", "endpoint": "/api/local-bootstrap-backup/plan"}},
            {"id": "backup", "title": "Backup portátil", "status": "available" if bootstrap_status.get("backup_count", 0) > 0 else "not_created", "value": bootstrap_status, "action": {"label": "Criar backup", "endpoint": "/api/local-bootstrap-backup/create-backup"}},
            {"id": "restore", "title": "Restore no PC novo", "status": "available", "value": restore_status, "action": {"label": "Restore", "endpoint": "/api/restore-approved/panel"}},
            {"id": "memory", "title": "Memória/contexto", "status": "ready" if memory_status.get("ok") else "attention", "value": memory_status, "action": {"label": "Preparar memórias", "endpoint": "/api/memory-context-router/prepare-priority-projects"}},
        ]

    def _flows(self, pc_profile: str) -> List[Dict[str, Any]]:
        return [
            {
                "flow_id": "one_click_auto_setup",
                "title": "Um botão: preparar este PC",
                "steps": [
                    {"step": 1, "label": "Fazer check-up automático"},
                    {"step": 2, "label": "Gerar plano de ferramentas"},
                    {"step": 3, "label": "Gerar script de instalação/configuração"},
                    {"step": 4, "label": "Preparar memória dos projetos"},
                    {"step": 5, "label": "Criar backup portátil"},
                    {"step": 6, "label": "Pedir OK só para instalar/restaurar/sobrescrever"},
                ],
            },
            {
                "flow_id": "old_pc_to_new_pc",
                "title": "Migrar de PC antigo para PC novo",
                "steps": [
                    {"step": 1, "label": "No PC antigo: auto setup + backup", "endpoint": "/api/pc-migration-control/auto-setup"},
                    {"step": 2, "label": "Copiar ZIP para pen/disco", "operator_action": True},
                    {"step": 3, "label": "No PC novo: instalar God Mode"},
                    {"step": 4, "label": "No PC novo: preview restore", "endpoint": "/api/restore-approved/preview"},
                    {"step": 5, "label": "No PC novo: restore aprovado", "endpoint": "/api/restore-approved/run", "requires_phrase": "RESTORE GOD MODE"},
                    {"step": 6, "label": "No PC novo: novo auto setup", "endpoint": "/api/pc-migration-control/auto-setup"},
                ],
            },
        ]

    def _safe_buttons(self) -> List[Dict[str, Any]]:
        return [
            {"id": "auto_setup", "label": "Setup automático", "endpoint": "/api/pc-migration-control/auto-setup", "priority": "critical"},
            {"id": "scan_pc", "label": "Check-up PC", "endpoint": "/api/local-tool-capability/scan", "priority": "critical"},
            {"id": "tools_plan", "label": "Plano ferramentas", "endpoint": "/api/local-bootstrap-backup/plan", "priority": "high"},
            {"id": "backup", "label": "Backup", "endpoint": "/api/local-bootstrap-backup/create-backup", "priority": "high"},
            {"id": "restore", "label": "Restore", "endpoint": "/api/restore-approved/panel", "priority": "high"},
        ]

    def _operator_next(self, tool_status: Dict[str, Any], bootstrap_status: Dict[str, Any], restore_status: Dict[str, Any], memory_status: Dict[str, Any]) -> Dict[str, Any]:
        if tool_status.get("status") == "not_scanned_yet":
            return {"label": "Executar setup automático", "endpoint": "/api/pc-migration-control/auto-setup", "priority": "critical"}
        if bootstrap_status.get("backup_count", 0) == 0:
            return {"label": "Criar backup portátil", "endpoint": "/api/local-bootstrap-backup/create-backup", "priority": "critical"}
        return {"label": "Continuar para restore ou validação", "endpoint": "/api/pc-migration-control/panel", "priority": "high"}

    def _store_session(self, session: Dict[str, Any]) -> None:
        def mutate(state: Dict[str, Any]) -> Dict[str, Any]:
            state.setdefault("sessions", [])
            state["sessions"].append(session)
            state["sessions"] = state["sessions"][-100:]
            return state
        CENTER_STORE.update(mutate)

    def _store_auto_run(self, auto_run: Dict[str, Any]) -> None:
        def mutate(state: Dict[str, Any]) -> Dict[str, Any]:
            state.setdefault("auto_runs", [])
            state["auto_runs"].append(auto_run)
            state["auto_runs"] = state["auto_runs"][-100:]
            return state
        CENTER_STORE.update(mutate)

    def latest(self) -> Dict[str, Any]:
        state = CENTER_STORE.load()
        sessions = state.get("sessions") or []
        auto_runs = state.get("auto_runs") or []
        return {"ok": True, "mode": "pc_migration_control_latest", "latest_session": sessions[-1] if sessions else None, "latest_auto_run": auto_runs[-1] if auto_runs else None, "session_count": len(sessions), "auto_run_count": len(auto_runs)}

    def panel(self, pc_profile: str = "auto", intent: str = "first_run_or_migration") -> Dict[str, Any]:
        return self.build_session(pc_profile=pc_profile, intent=intent)

    def get_status(self) -> Dict[str, Any]:
        latest = self.latest()
        session = latest.get("latest_session") or {}
        return {"ok": True, "mode": "pc_migration_control_status", "session_count": latest.get("session_count", 0), "auto_run_count": latest.get("auto_run_count", 0), "latest_traffic_light": session.get("traffic_light"), "latest_operator_next": session.get("operator_next"), "auto_mode_enabled": True}

    def get_package(self) -> Dict[str, Any]:
        return {"ok": True, "mode": "pc_migration_control_package", "package": {"status": self.get_status(), "panel": self.panel(), "latest": self.latest(), "auto_mode": self.auto_mode_policy()}}


pc_migration_control_center_service = PcMigrationControlCenterService()
