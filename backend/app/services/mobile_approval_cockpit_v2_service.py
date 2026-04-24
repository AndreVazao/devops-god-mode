from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List
from uuid import uuid4

from app.services.operator_command_intake_service import operator_command_intake_service
from app.services.vault_deploy_env_planner_service import vault_deploy_env_planner_service

DATA_DIR = Path("data")
MOBILE_APPROVAL_FILE = DATA_DIR / "mobile_approval_cockpit_v2.json"

SAFE_CARD_TYPES = {
    "operator_command",
    "secret_binding_approval",
    "provider_login_request",
    "destructive_action_guard",
    "deploy_env_sync_approval",
    "pr_write_approval",
    "progress_update",
}


class MobileApprovalCockpitV2Service:
    """Mobile-first approval cockpit for PC local brain operations.

    This layer creates chat-style cards for the phone. The PC can keep working
    locally and ask for approval, credentials, provider login or destructive
    action confirmation without exposing secret values.
    """

    def get_status(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "mode": "mobile_approval_cockpit_v2_status",
            "status": "mobile_approval_cockpit_v2_ready",
            "store_file": str(MOBILE_APPROVAL_FILE),
        }

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def _load_store(self) -> Dict[str, Any]:
        if not MOBILE_APPROVAL_FILE.exists():
            return {"cards": [], "threads": {}}
        try:
            loaded = json.loads(MOBILE_APPROVAL_FILE.read_text(encoding="utf-8"))
            if not isinstance(loaded, dict):
                return {"cards": [], "threads": {}}
            loaded.setdefault("cards", [])
            loaded.setdefault("threads", {})
            return loaded
        except json.JSONDecodeError:
            return {"cards": [], "threads": {}}

    def _save_store(self, store: Dict[str, Any]) -> None:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        MOBILE_APPROVAL_FILE.write_text(json.dumps(store, ensure_ascii=False, indent=2), encoding="utf-8")

    def create_card(
        self,
        title: str,
        body: str,
        card_type: str = "progress_update",
        project_id: str = "general-intake",
        tenant_id: str = "owner-andre",
        priority: str = "medium",
        requires_approval: bool = False,
        actions: List[Dict[str, Any]] | None = None,
        source_ref: Dict[str, Any] | None = None,
        metadata: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        normalized_type = card_type if card_type in SAFE_CARD_TYPES else "progress_update"
        card_id = f"card-{uuid4().hex[:12]}"
        created_at = self._now()
        card = {
            "card_id": card_id,
            "tenant_id": tenant_id,
            "project_id": project_id,
            "title": title.strip() or "God Mode update",
            "body": body.strip(),
            "card_type": normalized_type,
            "priority": priority,
            "requires_approval": requires_approval,
            "status": "pending_approval" if requires_approval else "open",
            "actions": actions or [],
            "source_ref": source_ref or {},
            "metadata": metadata or {},
            "created_at": created_at,
            "updated_at": created_at,
            "decision": None,
        }
        store = self._load_store()
        store["cards"].append(card)
        thread = store["threads"].setdefault(project_id, {"project_id": project_id, "card_ids": [], "last_seen_at": created_at})
        thread["card_ids"].append(card_id)
        thread["last_seen_at"] = created_at
        store["cards"] = store["cards"][-1000:]
        self._save_store(store)
        return {"ok": True, "mode": "mobile_approval_card_create", "card": card}

    def decide_card(
        self,
        card_id: str,
        decision: str,
        operator_note: str = "",
        tenant_id: str = "owner-andre",
    ) -> Dict[str, Any]:
        normalized = decision.lower().strip()
        if normalized not in {"approved", "rejected", "needs_changes", "acknowledged"}:
            return {"ok": False, "error": "invalid_decision", "allowed": ["approved", "rejected", "needs_changes", "acknowledged"]}
        store = self._load_store()
        for card in store.get("cards", []):
            if card.get("card_id") == card_id and card.get("tenant_id") == tenant_id:
                card["status"] = normalized
                card["decision"] = {"decision": normalized, "operator_note": operator_note, "decided_at": self._now()}
                card["updated_at"] = self._now()
                self._save_store(store)
                return {"ok": True, "mode": "mobile_approval_card_decision", "card": card}
        return {"ok": False, "error": "card_not_found", "card_id": card_id}

    def list_cards(
        self,
        tenant_id: str = "owner-andre",
        project_id: str | None = None,
        status: str | None = None,
        limit: int = 100,
    ) -> Dict[str, Any]:
        store = self._load_store()
        cards = [item for item in store.get("cards", []) if item.get("tenant_id") == tenant_id]
        if project_id:
            cards = [item for item in cards if item.get("project_id") == project_id]
        if status:
            cards = [item for item in cards if item.get("status") == status]
        cards = cards[-max(min(limit, 300), 1):]
        return {"ok": True, "mode": "mobile_approval_card_list", "card_count": len(cards), "cards": cards}

    def seed_from_latest_operator_command(self, tenant_id: str = "owner-andre") -> Dict[str, Any]:
        commands = operator_command_intake_service.list_commands(tenant_id=tenant_id, limit=1).get("commands", [])
        if not commands:
            return {"ok": False, "error": "no_operator_commands"}
        command = commands[-1]
        project_id = command.get("project", {}).get("project_id", "general-intake")
        steps = command.get("execution_plan", [])
        actions = [
            {"action_id": "approve-plan", "label": "Aprovar plano", "decision": "approved"},
            {"action_id": "reject-plan", "label": "Rejeitar", "decision": "rejected"},
            {"action_id": "needs-changes", "label": "Pedir alterações", "decision": "needs_changes"},
        ]
        return self.create_card(
            title=f"Plano pronto: {command.get('intent', 'comando')}",
            body=f"Projeto: {project_id}. Passos planeados: {len(steps)}. Prioridade: {command.get('priority')}. Confirma se o PC pode avançar para a próxima fase segura.",
            card_type="operator_command",
            project_id=project_id,
            tenant_id=tenant_id,
            priority=command.get("priority", "medium"),
            requires_approval=True,
            actions=actions,
            source_ref={"type": "operator_command", "command_id": command.get("command_id")},
            metadata={"execution_plan": steps},
        )

    def seed_from_deploy_readiness(self, project_id: str, tenant_id: str = "owner-andre") -> Dict[str, Any]:
        report_result = vault_deploy_env_planner_service.build_readiness_report(project_id=project_id, tenant_id=tenant_id)
        if not report_result.get("ok"):
            return report_result
        report = report_result["report"]
        blocked = report.get("status") != "ready_for_env_binding"
        actions = [
            {"action_id": "approve-env-binding", "label": "Aprovar env binding", "decision": "approved"},
            {"action_id": "hold-env-binding", "label": "Aguardar", "decision": "rejected"},
        ]
        body = f"Readiness {report.get('readiness_score')}%. Secrets presentes: {report.get('present_secret_count')}. Em falta: {report.get('missing_secret_count')}."
        if blocked:
            body += " Existem blockers; não sincronizar providers ainda."
        return self.create_card(
            title=f"Deploy/env readiness: {report.get('project_name')}",
            body=body,
            card_type="deploy_env_sync_approval",
            project_id=project_id,
            tenant_id=tenant_id,
            priority="high" if blocked else "medium",
            requires_approval=not blocked,
            actions=actions if not blocked else [{"action_id": "ack-blockers", "label": "Ok, vi blockers", "decision": "acknowledged"}],
            source_ref={"type": "deploy_readiness_report", "report_id": report.get("report_id")},
            metadata={"status": report.get("status"), "blockers": report.get("blockers", [])},
        )

    def build_dashboard(self, tenant_id: str = "owner-andre") -> Dict[str, Any]:
        cards = self.list_cards(tenant_id=tenant_id, limit=300).get("cards", [])
        pending = [item for item in cards if item.get("status") == "pending_approval"]
        high_priority = [item for item in cards if item.get("priority") in {"high", "critical"}]
        return {
            "ok": True,
            "mode": "mobile_approval_cockpit_v2_dashboard",
            "tenant_id": tenant_id,
            "card_count": len(cards),
            "pending_approval_count": len(pending),
            "high_priority_count": len(high_priority),
            "recent_cards": cards[-50:],
        }

    def get_package(self) -> Dict[str, Any]:
        return {"ok": True, "mode": "mobile_approval_cockpit_v2_package", "package": {"status": self.get_status(), "dashboard": self.build_dashboard()}}


mobile_approval_cockpit_v2_service = MobileApprovalCockpitV2Service()
