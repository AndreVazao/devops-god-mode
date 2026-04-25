from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List
from uuid import uuid4

from app.services.memory_core_service import memory_core_service
from app.services.monetization_readiness_service import monetization_readiness_service
from app.services.mobile_approval_cockpit_v2_service import mobile_approval_cockpit_v2_service
from app.utils.atomic_json_store import AtomicJsonStore

DATA_DIR = Path("data")
REVENUE_SPRINT_FILE = DATA_DIR / "revenue_sprint_planner.json"
REVENUE_SPRINT_STORE = AtomicJsonStore(
    REVENUE_SPRINT_FILE,
    default_factory=lambda: {"sprints": [], "tasks": [], "approvals": []},
)


class RevenueSprintPlannerService:
    """Turns monetization readiness into short approved execution sprints."""

    def get_status(self) -> Dict[str, Any]:
        store = self._load_store()
        return {
            "ok": True,
            "mode": "revenue_sprint_planner_status",
            "status": "revenue_sprint_planner_ready",
            "store_file": str(REVENUE_SPRINT_FILE),
            "atomic_store_enabled": True,
            "sprint_count": len(store.get("sprints", [])),
            "task_count": len(store.get("tasks", [])),
        }

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def _normalize_store(self, store: Dict[str, Any]) -> Dict[str, Any]:
        if not isinstance(store, dict):
            return {"sprints": [], "tasks": [], "approvals": []}
        store.setdefault("sprints", [])
        store.setdefault("tasks", [])
        store.setdefault("approvals", [])
        return store

    def _load_store(self) -> Dict[str, Any]:
        return self._normalize_store(REVENUE_SPRINT_STORE.load())

    def _task_set_for_project(self, row: Dict[str, Any]) -> List[Dict[str, Any]]:
        project_id = row["project_id"]
        tasks: List[Dict[str, Any]] = []
        if not row.get("repositories"):
            tasks.append({"label": "Resolver repo/app", "description": "Confirmar repo existente ou aprovar criação de repo novo.", "risk": "approval_required", "kind": "repo"})
        if row.get("memory_score", 0) < 80:
            tasks.append({"label": "Completar memória AndreOS", "description": "Preencher ARQUITETURA, BACKLOG, DECISOES e ULTIMA_SESSAO.", "risk": "safe_write_memory", "kind": "memory"})
        tasks.append({"label": "Definir pacote MVP", "description": row.get("mvp", "Definir MVP vendável."), "risk": "safe_planning", "kind": "mvp"})
        tasks.append({"label": "Definir primeira oferta vendável", "description": row.get("first_sellable_feature", "Definir feature vendável."), "risk": "safe_planning", "kind": "offer"})
        tasks.append({"label": "Preparar checklist de entrega", "description": f"Caminho de receita: {row.get('revenue_path', '')}", "risk": "safe_planning", "kind": "delivery"})
        return [
            {
                "task_id": f"rev-task-{uuid4().hex[:12]}",
                "project_id": project_id,
                "title": task["label"],
                "description": task["description"],
                "risk": task["risk"],
                "kind": task["kind"],
                "status": "planned",
                "created_at": self._now(),
            }
            for task in tasks[:5]
        ]

    def create_sprint(self, max_projects: int = 3, tenant_id: str = "owner-andre") -> Dict[str, Any]:
        matrix = monetization_readiness_service.build_matrix()
        if not matrix.get("ok"):
            return matrix
        rows = matrix["report"]["rows"]
        priority_rows = sorted(
            rows,
            key=lambda item: (
                item.get("status") == "blocked",
                item.get("priority") not in {"critical", "high"},
                -item.get("readiness_score", 0),
            ),
        )[: max(1, min(max_projects, 6))]
        tasks: List[Dict[str, Any]] = []
        for row in priority_rows:
            tasks.extend(self._task_set_for_project(row))
        sprint = {
            "sprint_id": f"revenue-sprint-{uuid4().hex[:12]}",
            "created_at": self._now(),
            "tenant_id": tenant_id,
            "status": "needs_operator_approval",
            "project_ids": [row["project_id"] for row in priority_rows],
            "task_ids": [task["task_id"] for task in tasks],
            "summary": "Sprint curto focado em transformar projetos críticos/high em MVP, oferta vendável e caminho de entrega.",
            "matrix_report_id": matrix["report"]["report_id"],
        }

        def mutate(store: Dict[str, Any]) -> Dict[str, Any]:
            store = self._normalize_store(store)
            store["sprints"].append(sprint)
            store["tasks"].extend(tasks)
            store["sprints"] = store["sprints"][-100:]
            store["tasks"] = store["tasks"][-1000:]
            return store

        REVENUE_SPRINT_STORE.update(mutate)
        memory_core_service.write_history("GOD_MODE", "Revenue sprint created", f"Sprint {sprint['sprint_id']} with projects: {', '.join(sprint['project_ids'])}")
        return {"ok": True, "mode": "revenue_sprint_create", "sprint": sprint, "tasks": tasks, "matrix": matrix["report"]}

    def create_approval_card_for_latest_sprint(self, tenant_id: str = "owner-andre") -> Dict[str, Any]:
        store = self._load_store()
        if not store.get("sprints"):
            created = self.create_sprint(tenant_id=tenant_id)
            if not created.get("ok"):
                return created
            store = self._load_store()
        sprint = store["sprints"][-1]
        tasks = [task for task in store.get("tasks", []) if task.get("task_id") in sprint.get("task_ids", [])]
        body = "\n".join([f"- {task['project_id']}: {task['title']} — {task['description']}" for task in tasks[:12]])
        card = mobile_approval_cockpit_v2_service.create_card(
            title="Aprovar Revenue Sprint",
            body=f"{sprint['summary']}\n\n{body}",
            card_type="operator_command",
            project_id="god-mode",
            tenant_id=tenant_id,
            priority="high",
            requires_approval=True,
            actions=[
                {"action_id": "approve-revenue-sprint", "label": "Aprovar sprint", "decision": "approved"},
                {"action_id": "reject-revenue-sprint", "label": "Rejeitar", "decision": "rejected"},
                {"action_id": "revise-revenue-sprint", "label": "Pedir ajustes", "decision": "needs_changes"},
            ],
            source_ref={"type": "revenue_sprint", "sprint_id": sprint["sprint_id"]},
            metadata={"sprint": sprint, "tasks": tasks},
        )
        return {"ok": True, "mode": "revenue_sprint_approval_card", "sprint": sprint, "tasks": tasks, "approval_card": card}

    def list_sprints(self, limit: int = 20) -> Dict[str, Any]:
        store = self._load_store()
        sprints = store.get("sprints", [])[-max(1, min(limit, 100)):]
        return {"ok": True, "mode": "revenue_sprint_list", "sprint_count": len(sprints), "sprints": sprints}

    def build_dashboard(self) -> Dict[str, Any]:
        store = self._load_store()
        latest = store.get("sprints", [])[-1] if store.get("sprints") else None
        latest_tasks = [task for task in store.get("tasks", []) if latest and task.get("task_id") in latest.get("task_ids", [])]
        return {
            "ok": True,
            "mode": "revenue_sprint_dashboard",
            "sprint_count": len(store.get("sprints", [])),
            "task_count": len(store.get("tasks", [])),
            "latest_sprint": latest,
            "latest_tasks": latest_tasks,
            "quick_start": [
                "Gerar sprint de 3 projetos críticos/high.",
                "Aprovar cartão no Mobile Approval Cockpit.",
                "Executar primeiro tarefas de repo, memória e MVP.",
                "Só depois avançar para código/deploy.",
            ],
        }

    def get_package(self) -> Dict[str, Any]:
        return {"ok": True, "mode": "revenue_sprint_package", "package": {"status": self.get_status(), "dashboard": self.build_dashboard()}}


revenue_sprint_planner_service = RevenueSprintPlannerService()
