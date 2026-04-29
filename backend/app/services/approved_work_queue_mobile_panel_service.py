from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from app.services.approved_work_queue_runner_service import approved_work_queue_runner_service
from app.services.approved_deep_execution_plan_service import approved_deep_execution_plan_service
from app.services.project_intake_priority_handoff_service import project_intake_priority_handoff_service
from app.services.mobile_result_normalizer_service import mobile_result_normalizer_service


class ApprovedWorkQueueMobilePanelService:
    """Mobile-first visual panel for the approved work queue.

    This service does not execute destructive work. It turns queue/readiness/gates
    into compact cards and safe buttons for the APK/Home.
    """

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def build_panel(self, tenant_id: str = "owner-andre") -> Dict[str, Any]:
        readiness = approved_deep_execution_plan_service.readiness(tenant_id=tenant_id)
        queue_status = approved_work_queue_runner_service.get_status()
        current = approved_work_queue_runner_service.current()
        gates = approved_work_queue_runner_service.gates()
        handoff = project_intake_priority_handoff_service.get_status()
        queue = current.get("queue") or {}
        latest_run = current.get("latest_run")
        cards = self._cards(readiness=readiness, queue=queue, gates=gates, latest_run=latest_run, handoff=handoff)
        panel = {
            "ok": True,
            "mode": "approved_work_queue_mobile_panel",
            "created_at": self._now(),
            "tenant_id": tenant_id,
            "headline": self._headline(readiness, queue, gates),
            "traffic_light": self._traffic_light(readiness, queue, gates),
            "cards": cards,
            "safe_buttons": self._safe_buttons(readiness, queue, gates),
            "blocked_actions": self._blocked_actions(gates),
            "latest_run": latest_run,
            "status": {
                "readiness": readiness,
                "handoff": handoff,
                "queue_status": queue_status,
                "queue_id": queue.get("queue_id"),
                "item_count": queue.get("item_count", 0),
                "safe_item_count": queue.get("safe_item_count", 0),
                "gated_item_count": queue.get("gated_item_count", 0),
            },
        }
        return self._normalize_for_mobile(panel)

    def _headline(self, readiness: Dict[str, Any], queue: Dict[str, Any], gates: Dict[str, Any]) -> str:
        if not readiness.get("ok"):
            return "Confirma prioridades antes de executar"
        if not queue:
            return "Fila aprovada ainda não criada"
        if gates.get("gated_count", 0) > 0:
            return "Fila pronta: passos seguros + gates à espera"
        return "Fila aprovada pronta para passos seguros"

    def _traffic_light(self, readiness: Dict[str, Any], queue: Dict[str, Any], gates: Dict[str, Any]) -> Dict[str, str]:
        if not readiness.get("ok"):
            return {"color": "yellow", "label": "Precisa confirmar prioridades", "reason": "priority_handoff_required"}
        if not queue:
            return {"color": "blue", "label": "Criar fila", "reason": "queue_not_created"}
        if gates.get("gated_count", 0) > 0:
            return {"color": "yellow", "label": "Há aprovações pendentes", "reason": "approval_gates_waiting"}
        return {"color": "green", "label": "Pronto para passos seguros", "reason": "safe_queue_ready"}

    def _cards(
        self,
        readiness: Dict[str, Any],
        queue: Dict[str, Any],
        gates: Dict[str, Any],
        latest_run: Optional[Dict[str, Any]],
        handoff: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        items = queue.get("items") or []
        safe_waiting = [item for item in items if item.get("safe_to_auto_run") and item.get("status") == "queued"]
        submitted = [item for item in items if item.get("status") == "submitted_safe"]
        gated = gates.get("gates") or []
        return [
            {
                "id": "priority_handoff",
                "title": "Prioridades",
                "status": "ok" if readiness.get("ok") else "needs_operator_ok",
                "summary": "Execução profunda só desbloqueia depois das prioridades confirmadas.",
                "value": {
                    "active_project": readiness.get("active_project"),
                    "handoff_status": handoff.get("status"),
                    "blocked_reasons": readiness.get("blocked_reasons", []),
                },
                "primary_action": {"label": "Confirmar prioridades", "endpoint": "/api/project-intake-priority-handoff/review"},
            },
            {
                "id": "queue_overview",
                "title": "Fila aprovada",
                "status": queue.get("status") or "not_created",
                "summary": "Fila persistente ordenada por prioridade do operador.",
                "value": {
                    "queue_id": queue.get("queue_id"),
                    "item_count": queue.get("item_count", 0),
                    "safe_item_count": queue.get("safe_item_count", 0),
                    "gated_item_count": queue.get("gated_item_count", 0),
                    "safe_waiting_count": len(safe_waiting),
                    "submitted_safe_count": len(submitted),
                },
                "primary_action": {"label": "Criar/atualizar fila", "endpoint": "/api/approved-work-queue/build"},
            },
            {
                "id": "safe_execution",
                "title": "Execução segura",
                "status": "ready" if safe_waiting else "idle",
                "summary": "Executa apenas passos seguros: leitura, snapshots, resumo e previews.",
                "value": {"next_safe_items": safe_waiting[:5], "latest_run": latest_run},
                "primary_action": {"label": "Executar próximos seguros", "endpoint": "/api/approved-work-queue/run-safe", "method": "POST", "payload": {"tenant_id": "owner-andre", "max_items": 3}},
            },
            {
                "id": "approval_gates",
                "title": "Gates / aprovações",
                "status": "needs_operator_ok" if gated else "clear",
                "summary": "Ações perigosas ficam paradas até aprovação explícita.",
                "value": {"gated_count": len(gated), "gates": gated[:8]},
                "primary_action": {"label": "Ver gates", "endpoint": "/api/approved-work-queue/gates"},
            },
        ]

    def _safe_buttons(self, readiness: Dict[str, Any], queue: Dict[str, Any], gates: Dict[str, Any]) -> List[Dict[str, Any]]:
        buttons: List[Dict[str, Any]] = []
        if not readiness.get("ok"):
            buttons.append({"id": "confirm_priorities", "label": "Confirmar prioridades", "endpoint": "/api/project-intake-priority-handoff/review", "priority": "critical"})
            return buttons
        buttons.append({"id": "build_queue", "label": "Criar fila", "endpoint": "/api/approved-work-queue/build", "priority": "critical"})
        buttons.append({"id": "run_safe", "label": "Executar seguros", "endpoint": "/api/approved-work-queue/run-safe", "method": "POST", "payload": {"tenant_id": "owner-andre", "max_items": 3}, "priority": "critical"})
        buttons.append({"id": "view_gates", "label": "Ver gates", "endpoint": "/api/approved-work-queue/gates", "priority": "high"})
        buttons.append({"id": "current_queue", "label": "Estado da fila", "endpoint": "/api/approved-work-queue/current", "priority": "high"})
        return buttons

    def _blocked_actions(self, gates: Dict[str, Any]) -> List[Dict[str, Any]]:
        blocked = []
        for gate in gates.get("gates") or []:
            blocked.append({
                "item_id": gate.get("item_id"),
                "label": gate.get("label"),
                "project_id": gate.get("project_id"),
                "action_type": gate.get("action_type"),
                "reason": "requires_operator_approval",
            })
        return blocked

    def run_safe_from_panel(self, tenant_id: str = "owner-andre", max_items: int = 3) -> Dict[str, Any]:
        result = approved_work_queue_runner_service.run_safe(tenant_id=tenant_id, max_items=max_items)
        return {
            "ok": result.get("ok", False),
            "mode": "approved_work_queue_mobile_run_safe",
            "result": result,
            "panel": self.build_panel(tenant_id=tenant_id),
        }

    def _normalize_for_mobile(self, panel: Dict[str, Any]) -> Dict[str, Any]:
        try:
            normalized = mobile_result_normalizer_service.normalize_result(
                title=panel.get("headline", "Fila aprovada"),
                result=panel,
                status=panel.get("traffic_light", {}).get("label", "ok"),
            )
            panel["mobile_card"] = normalized
        except Exception as exc:
            panel["mobile_card"] = {"ok": False, "error": exc.__class__.__name__, "detail": str(exc)[:300]}
        return panel

    def get_status(self) -> Dict[str, Any]:
        panel = self.build_panel()
        return {
            "ok": True,
            "mode": "approved_work_queue_mobile_panel_status",
            "headline": panel.get("headline"),
            "traffic_light": panel.get("traffic_light"),
            "card_count": len(panel.get("cards") or []),
            "button_count": len(panel.get("safe_buttons") or []),
        }

    def get_package(self) -> Dict[str, Any]:
        return {"ok": True, "mode": "approved_work_queue_mobile_panel_package", "package": {"status": self.get_status(), "panel": self.build_panel()}}


approved_work_queue_mobile_panel_service = ApprovedWorkQueueMobilePanelService()
