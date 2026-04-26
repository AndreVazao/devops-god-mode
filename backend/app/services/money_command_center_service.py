from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List
from uuid import uuid4

from app.services.memory_core_service import memory_core_service
from app.services.mobile_approval_cockpit_v2_service import mobile_approval_cockpit_v2_service
from app.services.monetization_readiness_service import monetization_readiness_service
from app.services.project_portfolio_service import project_portfolio_service
from app.services.revenue_sprint_planner_service import revenue_sprint_planner_service
from app.utils.atomic_json_store import AtomicJsonStore

DATA_DIR = Path("data")
MONEY_COMMAND_FILE = DATA_DIR / "money_command_center.json"
MONEY_COMMAND_STORE = AtomicJsonStore(
    MONEY_COMMAND_FILE,
    default_factory=lambda: {"decisions": [], "flows": [], "events": []},
)


class MoneyCommandCenterService:
    """Mobile-first cockpit that turns portfolio readiness into the next money action."""

    def get_status(self) -> Dict[str, Any]:
        store = self._load_store()
        return {
            "ok": True,
            "mode": "money_command_center_status",
            "status": "money_command_center_ready",
            "store_file": str(MONEY_COMMAND_FILE),
            "atomic_store_enabled": True,
            "decision_count": len(store.get("decisions", [])),
            "flow_count": len(store.get("flows", [])),
        }

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def _normalize_store(self, store: Dict[str, Any]) -> Dict[str, Any]:
        if not isinstance(store, dict):
            return {"decisions": [], "flows": [], "events": []}
        store.setdefault("decisions", [])
        store.setdefault("flows", [])
        store.setdefault("events", [])
        return store

    def _load_store(self) -> Dict[str, Any]:
        return self._normalize_store(MONEY_COMMAND_STORE.load())

    def _remember(self, title: str, body: str) -> Dict[str, Any]:
        memory_core_service.initialize()
        history = memory_core_service.write_history("GOD_MODE", title, body)
        session = memory_core_service.update_last_session(
            "GOD_MODE",
            summary=f"Money Command Center: {title}",
            next_steps=body,
        )
        return {"history": history, "last_session": session}

    def _money_rank_key(self, row: Dict[str, Any]) -> tuple:
        has_repo = bool(row.get("repositories"))
        priority_rank = {"critical": 4, "high": 3, "medium": 2, "low": 1}.get(row.get("priority", "medium"), 2)
        project_bonus = {
            "PROVENTIL": 14,
            "BARIBUDOS_STUDIO_WEBSITE": 12,
            "BARIBUDOS_STUDIO": 10,
            "VERBAFORGE": 9,
            "BUILD_CONTROL_CENTER": 5,
            "GOD_MODE": 4,
            "BOT_FACTORY": 2,
        }.get(row.get("project_id"), 0)
        blocker_penalty = len(row.get("blockers", [])) * 5
        return (
            project_bonus + priority_rank * 10 + int(row.get("readiness_score", 0)) + (15 if has_repo else 0) - blocker_penalty,
            int(row.get("readiness_score", 0)),
        )

    def build_money_matrix(self) -> Dict[str, Any]:
        matrix = monetization_readiness_service.build_matrix()
        if not matrix.get("ok"):
            return matrix
        rows = sorted(matrix["report"].get("rows", []), key=self._money_rank_key, reverse=True)
        top = rows[0] if rows else None
        offers = [
            {
                "project_id": row.get("project_id"),
                "name": row.get("name"),
                "first_sellable_feature": row.get("first_sellable_feature"),
                "mvp": row.get("mvp"),
                "revenue_path": row.get("revenue_path"),
                "readiness_score": row.get("readiness_score"),
                "blockers": row.get("blockers", []),
            }
            for row in rows
        ]
        report = {
            "report_id": f"money-command-{uuid4().hex[:12]}",
            "created_at": self._now(),
            "top_project": top,
            "rows": rows,
            "offers": offers,
            "blockers": self._collect_blockers(rows),
            "operator_answer": self._operator_answer(top),
        }
        return {"ok": True, "mode": "money_command_matrix", "report": report}

    def _collect_blockers(self, rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        blockers: List[Dict[str, Any]] = []
        for row in rows:
            for blocker in row.get("blockers", []):
                blockers.append({
                    "project_id": row.get("project_id"),
                    "name": row.get("name"),
                    "blocker": blocker,
                    "next_action": row.get("next_action"),
                    "readiness_score": row.get("readiness_score"),
                })
        return blockers[:25]

    def _operator_answer(self, top: Dict[str, Any] | None) -> str:
        if not top:
            return "Ainda não há projetos suficientes no portfólio para escolher uma rota de dinheiro."
        return (
            f"Começa por {top.get('name')}: {top.get('first_sellable_feature')} "
            f"O passo curto é: {top.get('next_action')}"
        )

    def top_project(self) -> Dict[str, Any]:
        matrix = self.build_money_matrix()
        if not matrix.get("ok"):
            return matrix
        top = matrix["report"].get("top_project")
        if not top:
            return {"ok": False, "error": "no_projects_available"}
        self._remember("Money top project selected", f"Projeto recomendado: {top.get('project_id')} — {top.get('first_sellable_feature')}")
        return {"ok": True, "mode": "money_command_top_project", "top_project": top, "report": matrix["report"]}

    def create_revenue_sprint(self, max_projects: int = 3, tenant_id: str = "owner-andre") -> Dict[str, Any]:
        created = revenue_sprint_planner_service.create_sprint(max_projects=max_projects, tenant_id=tenant_id)
        if not created.get("ok"):
            return created
        sprint = created.get("sprint", {})
        tasks = created.get("tasks", [])
        memory = self._remember(
            "Money revenue sprint created",
            f"Sprint {sprint.get('sprint_id')} criado para {', '.join(sprint.get('project_ids', []))}. Tarefas: {len(tasks)}.",
        )
        flow = {
            "flow_id": f"money-flow-{uuid4().hex[:12]}",
            "created_at": self._now(),
            "status": "sprint_created",
            "sprint_id": sprint.get("sprint_id"),
            "project_ids": sprint.get("project_ids", []),
            "task_count": len(tasks),
        }

        def mutate(store: Dict[str, Any]) -> Dict[str, Any]:
            store = self._normalize_store(store)
            store["flows"].append(flow)
            store["flows"] = store["flows"][-100:]
            return store

        MONEY_COMMAND_STORE.update(mutate)
        return {"ok": True, "mode": "money_command_create_sprint", "sprint": sprint, "tasks": tasks, "matrix": created.get("matrix"), "flow": flow, "memory": memory}

    def create_approval_card(self, max_projects: int = 3, tenant_id: str = "owner-andre") -> Dict[str, Any]:
        created = self.create_revenue_sprint(max_projects=max_projects, tenant_id=tenant_id)
        if not created.get("ok"):
            return created
        sprint = created.get("sprint", {})
        tasks = created.get("tasks", [])
        task_lines = "\n".join([f"- {task['project_id']}: {task['title']} — {task['description']}" for task in tasks[:12]])
        card = mobile_approval_cockpit_v2_service.create_card(
            title="Aprovar próximo passo para ganhar dinheiro",
            body=(
                "O God Mode escolheu o sprint curto com maior probabilidade de virar dinheiro.\n\n"
                f"Projetos: {', '.join(sprint.get('project_ids', []))}\n\n"
                f"Tarefas:\n{task_lines}\n\n"
                "Ao aprovar, a próxima fase deve transformar isto em PRs pequenas, auditoria, build/deploy e checklist de entrega."
            ),
            card_type="operator_command",
            project_id="god-mode",
            tenant_id=tenant_id,
            priority="high",
            requires_approval=True,
            actions=[
                {"action_id": "approve-money-sprint", "label": "Aprovar próximo passo", "decision": "approved"},
                {"action_id": "reject-money-sprint", "label": "Rejeitar", "decision": "rejected"},
                {"action_id": "revise-money-sprint", "label": "Pedir ajustes", "decision": "needs_changes"},
            ],
            source_ref={"type": "money_command_center", "sprint_id": sprint.get("sprint_id")},
            metadata={"sprint": sprint, "tasks": tasks, "flow": created.get("flow")},
        )
        self._remember("Money approval card created", f"Cartão criado para sprint {sprint.get('sprint_id')}.")
        return {"ok": True, "mode": "money_command_approval_card", "sprint": sprint, "tasks": tasks, "approval_card": card, "flow": created.get("flow")}

    def prepare_mvp_delivery(self, project_id: str | None = None, tenant_id: str = "owner-andre") -> Dict[str, Any]:
        matrix = self.build_money_matrix()
        if not matrix.get("ok"):
            return matrix
        rows = matrix["report"].get("rows", [])
        selected = next((row for row in rows if row.get("project_id") == project_id), None) if project_id else (rows[0] if rows else None)
        if not selected:
            return {"ok": False, "error": "project_not_found"}
        checklist = [
            {"label": "Confirmar repo/app", "done": bool(selected.get("repositories")), "owner": "God Mode"},
            {"label": "Confirmar primeira oferta vendável", "done": bool(selected.get("first_sellable_feature")), "owner": "Oner"},
            {"label": "Fechar MVP mínimo", "done": bool(selected.get("mvp")), "owner": "God Mode"},
            {"label": "Preparar demo/proposta/página", "done": False, "owner": "God Mode"},
            {"label": "Preparar build/deploy ou PDF de entrega", "done": False, "owner": "God Mode"},
            {"label": "Criar checklist comercial final", "done": False, "owner": "Oner"},
        ]
        delivery = {
            "delivery_id": f"money-delivery-{uuid4().hex[:12]}",
            "created_at": self._now(),
            "tenant_id": tenant_id,
            "project_id": selected.get("project_id"),
            "project_name": selected.get("name"),
            "first_sellable_feature": selected.get("first_sellable_feature"),
            "mvp": selected.get("mvp"),
            "revenue_path": selected.get("revenue_path"),
            "blockers": selected.get("blockers", []),
            "checklist": checklist,
            "next_action": selected.get("next_action"),
        }
        self._remember("Money MVP delivery prepared", f"Entrega MVP preparada para {delivery['project_id']}: {delivery['first_sellable_feature']}")
        return {"ok": True, "mode": "money_command_prepare_delivery", "delivery": delivery}

    def build_dashboard(self, tenant_id: str = "owner-andre") -> Dict[str, Any]:
        portfolio = project_portfolio_service.build_dashboard()
        money = self.build_money_matrix()
        revenue = revenue_sprint_planner_service.build_dashboard()
        approvals = mobile_approval_cockpit_v2_service.build_dashboard(tenant_id=tenant_id)
        store = self._load_store()
        report = money.get("report", {}) if money.get("ok") else {}
        return {
            "ok": True,
            "mode": "money_command_center_dashboard",
            "tenant_id": tenant_id,
            "status": self.get_status(),
            "summary": {
                "portfolio_projects": portfolio.get("summary", {}).get("project_count", 0),
                "top_project": (report.get("top_project") or {}).get("project_id"),
                "pending_approvals": approvals.get("pending_approval_count", 0),
                "sprint_count": revenue.get("sprint_count", 0),
                "blocker_count": len(report.get("blockers", [])),
            },
            "top_project": report.get("top_project"),
            "offers": report.get("offers", []),
            "blockers": report.get("blockers", []),
            "latest_sprint": revenue.get("latest_sprint"),
            "latest_tasks": revenue.get("latest_tasks", []),
            "recent_flows": store.get("flows", [])[-20:],
            "quick_buttons": [
                "Ver projeto com maior chance de dinheiro",
                "Criar sprint de receita",
                "Aprovar próximo passo",
                "Ver bloqueios para ganhar dinheiro",
                "Ver primeiro produto vendável por projeto",
                "Preparar entrega MVP",
            ],
            "operator_answer": report.get("operator_answer"),
        }

    def get_blockers(self) -> Dict[str, Any]:
        matrix = self.build_money_matrix()
        if not matrix.get("ok"):
            return matrix
        return {"ok": True, "mode": "money_command_blockers", "blockers": matrix["report"].get("blockers", [])}

    def get_sellable_offers(self) -> Dict[str, Any]:
        matrix = self.build_money_matrix()
        if not matrix.get("ok"):
            return matrix
        return {"ok": True, "mode": "money_command_sellable_offers", "offers": matrix["report"].get("offers", [])}

    def get_package(self) -> Dict[str, Any]:
        return {"ok": True, "mode": "money_command_center_package", "package": {"status": self.get_status(), "dashboard": self.build_dashboard()}}


money_command_center_service = MoneyCommandCenterService()
