from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List
from uuid import uuid4

from app.services.memory_core_service import memory_core_service
from app.services.operator_priority_service import operator_priority_service
from app.services.request_orchestrator_service import request_orchestrator_service
from app.services.request_worker_loop_service import request_worker_loop_service
from app.utils.atomic_json_store import AtomicJsonStore

DATA_DIR = Path("data")
PIPELINE_FILE = DATA_DIR / "real_work_command_pipeline.json"
PIPELINE_STORE = AtomicJsonStore(
    PIPELINE_FILE,
    default_factory=lambda: {"version": 1, "commands": [], "packages": [], "reports": []},
)


class RealWorkCommandPipelineService:
    """Natural command -> project-aware execution package.

    This is the first bridge from a user order to a concrete backend work plan.
    It obeys operator project priority and does not rank projects by money.
    """

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def _normalize_store(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        payload.setdefault("version", 1)
        payload.setdefault("commands", [])
        payload.setdefault("packages", [])
        payload.setdefault("reports", [])
        return payload

    def _load(self) -> Dict[str, Any]:
        return self._normalize_store(PIPELINE_STORE.load())

    def _record(self, key: str, item: Dict[str, Any]) -> None:
        def mutate(payload: Dict[str, Any]) -> Dict[str, Any]:
            payload = self._normalize_store(payload)
            payload[key].append(item)
            payload[key] = payload[key][-300:]
            return payload

        PIPELINE_STORE.update(mutate)

    def get_status(self) -> Dict[str, Any]:
        store = self._load()
        priority = operator_priority_service.get_status()
        return {
            "ok": True,
            "mode": "real_work_command_pipeline_status",
            "status": "ready_for_operator_order_execution",
            "policy": "operator_project_order_first",
            "money_priority_enabled": False,
            "active_project": priority.get("active_project"),
            "command_count": len(store.get("commands", [])),
            "package_count": len(store.get("packages", [])),
            "report_count": len(store.get("reports", [])),
        }

    def submit_command(
        self,
        command_text: str,
        tenant_id: str = "owner-andre",
        requested_project: str | None = None,
        auto_run: bool = True,
    ) -> Dict[str, Any]:
        command = (command_text or "").strip()
        if not command:
            raise ValueError("empty_command")
        command_id = f"work-cmd-{uuid4().hex[:12]}"
        resolved = operator_priority_service.resolve_project(requested_project)
        project = resolved.get("project") or {"project_id": "GOD_MODE", "label": "God Mode", "priority": 1}
        package = self._build_execution_package(command_id, command, tenant_id, project, resolved.get("source"), auto_run)
        submit = request_orchestrator_service.submit_request(
            request=package["orchestrator_request"],
            tenant_id=tenant_id,
            project_id=project["project_id"],
            auto_run=False,
        )
        job = submit.get("job", {}) if isinstance(submit, dict) else {}
        job_id = job.get("job_id")
        package["orchestrator_submit"] = {
            "ok": bool(submit.get("ok", False)) if isinstance(submit, dict) else False,
            "job_id": job_id,
            "status": job.get("status"),
        }
        worker_tick = None
        if auto_run and job_id:
            worker_tick = request_worker_loop_service.tick(tenant_id=tenant_id, max_jobs=3)
        report = self._build_report(package, worker_tick)
        self._record("commands", {"command_id": command_id, "created_at": package["created_at"], "project_id": project["project_id"], "command_text": command, "job_id": job_id})
        self._record("packages", package)
        self._record("reports", report)
        memory_core_service.write_history(project["project_id"], "Real work command pipeline", f"{command_id}: {command[:160]}")
        return {"ok": True, "mode": "real_work_command_pipeline_submit", "package": package, "report": report, "worker_tick": worker_tick}

    def _build_execution_package(
        self,
        command_id: str,
        command: str,
        tenant_id: str,
        project: Dict[str, Any],
        project_source: str | None,
        auto_run: bool,
    ) -> Dict[str, Any]:
        intent = self._classify_intent(command)
        actions = self._actions_for_intent(intent, project)
        approval_required = any(item.get("risk") in {"medium", "high"} for item in actions)
        orchestrator_request = (
            f"Project: {project['project_id']}\n"
            f"Operator command: {command}\n"
            f"Intent: {intent}\n"
            "Policy: obey operator project priority; money is consequence, not the selection criterion.\n"
            "Execute safe steps until done or blocked by approval/credentials/manual input."
        )
        return {
            "command_id": command_id,
            "created_at": self._now(),
            "tenant_id": tenant_id,
            "project": project,
            "project_source": project_source,
            "operator_command": command,
            "intent": intent,
            "auto_run_requested": auto_run,
            "approval_required": approval_required,
            "orchestrator_request": orchestrator_request,
            "execution_actions": actions,
            "stop_conditions": [
                "needs_operator_ok",
                "needs_credentials_or_login",
                "destructive_action_requested",
                "unclear_project_direction",
                "checks_failed_after_safe_retry",
            ],
            "success_definition": "branch/PR/check/report or explicit blocked state with next approval card",
        }

    def _classify_intent(self, command: str) -> str:
        text = command.lower()
        if any(word in text for word in ["audita", "audit", "verifica", "analisa"]):
            return "deep_audit_and_fix_plan"
        if any(word in text for word in ["corrige", "arranja", "fix", "repara"]):
            return "repair_project"
        if any(word in text for word in ["continua", "avança", "segue", "desenvolve"]):
            return "continue_project"
        if any(word in text for word in ["build", "apk", "exe", "artifact"]):
            return "build_and_artifact_check"
        if any(word in text for word in ["repo", "github", "pr", "pull request"]):
            return "repo_pr_work"
        return "general_project_execution"

    def _actions_for_intent(self, intent: str, project: Dict[str, Any]) -> List[Dict[str, Any]]:
        base = [
            {"step": 1, "label": "Resolver projeto ativo", "risk": "low", "detail": project["project_id"]},
            {"step": 2, "label": "Ler memória AndreOS do projeto", "risk": "low", "detail": "context compact + backlog + última sessão"},
            {"step": 3, "label": "Criar plano curto executável", "risk": "low", "detail": "fase pequena, resultado verificável"},
        ]
        if intent == "deep_audit_and_fix_plan":
            base.extend([
                {"step": 4, "label": "Auditar repo/ficheiros ligados", "risk": "low", "detail": "imports, rotas, workflows, docs"},
                {"step": 5, "label": "Preparar plano de correção", "risk": "low", "detail": "ordenado por blockers"},
                {"step": 6, "label": "Pedir aprovação antes de alterações reais", "risk": "medium", "detail": "branch/PR"},
            ])
        elif intent == "repair_project":
            base.extend([
                {"step": 4, "label": "Criar branch de correção", "risk": "medium", "detail": "sem tocar main"},
                {"step": 5, "label": "Aplicar patch pequeno", "risk": "medium", "detail": "validável"},
                {"step": 6, "label": "Correr checks e abrir PR", "risk": "medium", "detail": "relatório no chat"},
            ])
        elif intent == "build_and_artifact_check":
            base.extend([
                {"step": 4, "label": "Verificar workflows canónicos", "risk": "low", "detail": "EXE/APK/Universal"},
                {"step": 5, "label": "Identificar artifact mais recente", "risk": "low", "detail": "links e estado"},
                {"step": 6, "label": "Propor rerun se necessário", "risk": "medium", "detail": "approval"},
            ])
        else:
            base.extend([
                {"step": 4, "label": "Executar próximo passo seguro", "risk": "medium", "detail": "branch/PR se houver escrita"},
                {"step": 5, "label": "Validar", "risk": "low", "detail": "checks/docs/tree"},
                {"step": 6, "label": "Reportar e bloquear se precisar OK", "risk": "low", "detail": "mobile approval"},
            ])
        return base

    def _build_report(self, package: Dict[str, Any], worker_tick: Any) -> Dict[str, Any]:
        submit = package.get("orchestrator_submit", {})
        return {
            "report_id": f"work-report-{uuid4().hex[:12]}",
            "created_at": self._now(),
            "command_id": package["command_id"],
            "project_id": package["project"]["project_id"],
            "intent": package["intent"],
            "job_id": submit.get("job_id"),
            "job_status": submit.get("status"),
            "worker_tick_ran": worker_tick is not None,
            "money_priority_enabled": False,
            "operator_priority_obeyed": True,
            "next_visible_step": "open request worker / approvals if blocked, otherwise follow PR/check report",
        }

    def latest(self) -> Dict[str, Any]:
        store = self._load()
        return {
            "ok": True,
            "mode": "real_work_command_pipeline_latest",
            "command": store["commands"][-1] if store["commands"] else None,
            "package": store["packages"][-1] if store["packages"] else None,
            "report": store["reports"][-1] if store["reports"] else None,
        }

    def get_package(self) -> Dict[str, Any]:
        return {"ok": True, "mode": "real_work_command_pipeline_package", "package": {"status": self.get_status(), "latest": self.latest()}}


real_work_command_pipeline_service = RealWorkCommandPipelineService()
