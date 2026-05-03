from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _data_dir() -> Path:
    base = os.environ.get("GODMODE_DATA_DIR")
    if base:
        root = Path(base)
    else:
        root = Path.home() / ".godmode" / "data"
    target = root / "pipelines"
    target.mkdir(parents=True, exist_ok=True)
    return target


class PipelinePersistenceExecutorService:
    """Persists orchestration pipelines and executes safe low-risk steps.

    This v1 only executes local/read-only/preparation steps. It never commits,
    merges, deletes, releases, changes credentials, or sends external AI handoffs.
    """

    AUTO_SAFE_SOURCES = {
        "goal_planner",
        "agent_roles",
        "ai_provider_router",
        "reusable_code_registry",
        "mcp_compatibility",
        "health_check",
    }

    BLOCKED_STATUSES = {"blocked", "requires_approval"}

    def status(self) -> dict[str, Any]:
        data_dir = _data_dir()
        return {
            "ok": True,
            "service": "pipeline_persistence_executor",
            "created_at": _utc_now(),
            "data_dir": str(data_dir),
            "pipeline_count": len(list(data_dir.glob("*.json"))),
            "execution_policy": "low_risk_local_only",
            "auto_safe_sources": sorted(self.AUTO_SAFE_SOURCES),
        }

    def panel(self) -> dict[str, Any]:
        return {
            **self.status(),
            "headline": "Pipeline Persistence + Low-Risk Executor",
            "description": "Guarda pipelines/playbooks em JSON local e executa apenas passos low-risk seguros.",
            "primary_actions": [
                {"label": "Guardar pipeline", "endpoint": "/api/pipeline-store/save", "method": "POST", "safe": True},
                {"label": "Listar pipelines", "endpoint": "/api/pipeline-store/list", "method": "GET", "safe": True},
                {"label": "Executar low-risk", "endpoint": "/api/pipeline-store/execute-low-risk", "method": "POST", "safe": True},
            ],
            "rules": self.rules(),
        }

    def rules(self) -> list[str]:
        return [
            "Persistir pipeline antes de executar passos reais.",
            "Executar automaticamente só passos low-risk locais/read-only/preparação.",
            "Nunca fazer commit, merge, release, delete, alteração de credenciais ou envio IA externo nesta fase.",
            "Passos blocked/requires_approval ficam parados até aprovação explícita.",
            "Cada execução cria log dentro do JSON do pipeline.",
            "Dados locais ficam em GODMODE_DATA_DIR ou ~/.godmode/data/pipelines.",
        ]

    def save_pipeline(self, pipeline: dict[str, Any], source: str = "manual") -> dict[str, Any]:
        pipeline_id = pipeline.get("pipeline_id") or f"pipe-{uuid4().hex[:10]}"
        record = {
            "ok": True,
            "pipeline_id": pipeline_id,
            "source": source,
            "created_at": pipeline.get("created_at") or _utc_now(),
            "updated_at": _utc_now(),
            "status": "saved",
            "pipeline": pipeline,
            "execution_log": [],
        }
        path = self._path(pipeline_id)
        path.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
        return {"ok": True, "pipeline_id": pipeline_id, "path": str(path), "status": "saved"}

    def create_and_save_from_goal(
        self,
        goal: str,
        project: str | None = None,
        repo: str | None = None,
        context: str | None = None,
        priority: str = "normal",
        sensitive: bool = False,
        needs_code: bool = False,
        preferred_provider: str | None = None,
    ) -> dict[str, Any]:
        try:
            from app.services.real_orchestration_pipeline_service import real_orchestration_pipeline_service

            pipeline = real_orchestration_pipeline_service.run(
                goal=goal,
                project=project,
                repo=repo,
                context=context,
                priority=priority,
                sensitive=sensitive,
                needs_code=needs_code,
                preferred_provider=preferred_provider,
                execution_mode="safe_queue",
                operator_approved=False,
            )
            saved = self.save_pipeline(pipeline=pipeline, source="create_and_save_from_goal")
            return {"ok": True, "saved": saved, "pipeline": pipeline}
        except Exception as exc:
            return {"ok": False, "error_type": exc.__class__.__name__, "detail": str(exc)[:240]}

    def list_pipelines(self, limit: int = 50) -> dict[str, Any]:
        items = []
        for path in sorted(_data_dir().glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)[:limit]:
            try:
                record = json.loads(path.read_text(encoding="utf-8"))
                items.append(
                    {
                        "pipeline_id": record.get("pipeline_id"),
                        "status": record.get("status"),
                        "source": record.get("source"),
                        "created_at": record.get("created_at"),
                        "updated_at": record.get("updated_at"),
                        "goal": record.get("pipeline", {}).get("goal"),
                        "ready_count": len(record.get("pipeline", {}).get("ready_to_execute_safe_steps", [])),
                        "blocked_count": len(record.get("pipeline", {}).get("blocked_steps", [])),
                        "path": str(path),
                    }
                )
            except Exception as exc:
                items.append({"pipeline_id": path.stem, "status": "unreadable", "error": str(exc)[:120], "path": str(path)})
        return {"ok": True, "count": len(items), "pipelines": items}

    def load_pipeline(self, pipeline_id: str) -> dict[str, Any]:
        path = self._path(pipeline_id)
        if not path.exists():
            return {"ok": False, "error_type": "pipeline_not_found", "pipeline_id": pipeline_id}
        try:
            return {"ok": True, "record": json.loads(path.read_text(encoding="utf-8")), "path": str(path)}
        except Exception as exc:
            return {"ok": False, "error_type": exc.__class__.__name__, "detail": str(exc)[:240], "path": str(path)}

    def execute_low_risk(self, pipeline_id: str, dry_run: bool = False) -> dict[str, Any]:
        loaded = self.load_pipeline(pipeline_id)
        if not loaded.get("ok"):
            return loaded
        record = loaded["record"]
        pipeline = record.get("pipeline", {})
        queue = pipeline.get("safe_action_queue", [])
        results = []
        for step in queue:
            result = self._execute_step(step=step, pipeline=pipeline, dry_run=dry_run)
            results.append(result)
        record.setdefault("execution_log", []).append(
            {
                "created_at": _utc_now(),
                "dry_run": dry_run,
                "result_count": len(results),
                "executed_count": len([r for r in results if r.get("executed")]),
                "blocked_count": len([r for r in results if not r.get("allowed")]),
                "results": results,
            }
        )
        record["updated_at"] = _utc_now()
        record["status"] = "dry_run_completed" if dry_run else "low_risk_executed"
        self._path(pipeline_id).write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
        return {
            "ok": True,
            "pipeline_id": pipeline_id,
            "dry_run": dry_run,
            "executed_count": len([r for r in results if r.get("executed")]),
            "blocked_count": len([r for r in results if not r.get("allowed")]),
            "results": results,
        }

    def _execute_step(self, step: dict[str, Any], pipeline: dict[str, Any], dry_run: bool) -> dict[str, Any]:
        status = step.get("status")
        source = step.get("source")
        risk = step.get("risk", "unknown")
        if status in self.BLOCKED_STATUSES:
            return {"step_id": step.get("id"), "allowed": False, "executed": False, "reason": f"status {status}", "step": step}
        if source not in self.AUTO_SAFE_SOURCES and risk != "low":
            return {"step_id": step.get("id"), "allowed": False, "executed": False, "reason": f"source/risk not auto-safe: {source}/{risk}", "step": step}
        if dry_run:
            return {"step_id": step.get("id"), "allowed": True, "executed": False, "dry_run": True, "action": self._action_for(step, pipeline)}
        action_result = self._run_safe_action(step=step, pipeline=pipeline)
        return {"step_id": step.get("id"), "allowed": True, "executed": True, "action_result": action_result, "step": step}

    def _run_safe_action(self, step: dict[str, Any], pipeline: dict[str, Any]) -> dict[str, Any]:
        source = step.get("source")
        if source == "goal_planner":
            return {"ok": True, "type": "ack_goal_plan", "goal_id": pipeline.get("goal_plan", {}).get("goal_id")}
        if source == "agent_roles":
            return {"ok": True, "type": "ack_agent_roles", "role_steps": len(pipeline.get("agent_roles", {}).get("steps", []))}
        if source == "ai_provider_router":
            selected = pipeline.get("provider_route", {}).get("selected_provider", {})
            return {"ok": True, "type": "ack_provider_route", "selected_provider": selected.get("provider_id")}
        if source == "reusable_code_registry":
            return {"ok": True, "type": "requires_registry_search", "endpoint": "/api/reusable-code-registry/search"}
        return {"ok": True, "type": "ack_safe_step", "source": source}

    def _action_for(self, step: dict[str, Any], pipeline: dict[str, Any]) -> dict[str, Any]:
        return {"source": step.get("source"), "title": step.get("title"), "risk": step.get("risk"), "status": step.get("status")}

    def _path(self, pipeline_id: str) -> Path:
        safe = "".join(ch for ch in pipeline_id if ch.isalnum() or ch in {"-", "_"})[:80]
        return _data_dir() / f"{safe}.json"

    def package(self) -> dict[str, Any]:
        return {"status": self.status(), "panel": self.panel(), "rules": self.rules(), "recent": self.list_pipelines(limit=10)}


pipeline_persistence_executor_service = PipelinePersistenceExecutorService()
