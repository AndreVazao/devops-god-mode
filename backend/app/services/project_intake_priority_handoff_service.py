from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import uuid4

from app.services.operator_priority_service import operator_priority_service
from app.services.unified_project_intake_orchestrator_service import unified_project_intake_orchestrator_service
from app.utils.atomic_json_store import AtomicJsonStore

DATA_DIR = Path("data")
HANDOFF_FILE = DATA_DIR / "project_intake_priority_handoff.json"
HANDOFF_STORE = AtomicJsonStore(
    HANDOFF_FILE,
    default_factory=lambda: {
        "version": 1,
        "policy": "operator_confirms_intake_before_deep_execution",
        "current_handoff": None,
        "decisions": [],
    },
)


class ProjectIntakePriorityHandoffService:
    """Turn the safe unified intake into an operator priority decision.

    This layer bridges Phase 110 with the existing operator priority engine.
    It does not rename conversations, create repos, send prompts, write project
    files, store credentials, or delete duplicated modules.
    """

    DEFAULT_ORDER = [
        "GOD_MODE",
        "BARIBUDOS_STUDIO",
        "BARIBUDOS_STUDIO_WEBSITE",
        "PROVENTIL",
        "VERBAFORGE",
        "BOT_FACTORY",
        "BOT_LORDS_MOBILE",
        "ECU_REPRO",
        "BUILD_CONTROL_CENTER",
    ]

    GROUP_ALIASES = {
        "baribudos_studio_ecosystem": ["BARIBUDOS_STUDIO", "BARIBUDOS_STUDIO_WEBSITE"],
        "god_mode_core": ["GOD_MODE"],
    }

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def _normalize_project_id(self, value: str) -> str:
        return value.strip().upper().replace("-", "_").replace(" ", "_")

    def _flatten_order(self, values: List[str]) -> List[str]:
        ordered: List[str] = []
        seen = set()
        for raw in values:
            if not raw or not raw.strip():
                continue
            key = raw.strip()
            alias_key = key.lower().replace("-", "_").replace(" ", "_")
            candidates = self.GROUP_ALIASES.get(alias_key, [self._normalize_project_id(key)])
            for candidate in candidates:
                normalized = self._normalize_project_id(candidate)
                if normalized not in seen:
                    ordered.append(normalized)
                    seen.add(normalized)
        for fallback in self.DEFAULT_ORDER:
            if fallback not in seen:
                ordered.append(fallback)
                seen.add(fallback)
        return ordered

    def build_review(self, tenant_id: str = "owner-andre", requested_project: str = "GOD_MODE") -> Dict[str, Any]:
        review_id = f"intake-priority-review-{uuid4().hex[:12]}"
        intake = unified_project_intake_orchestrator_service.run_safe(
            tenant_id=tenant_id,
            requested_project=requested_project,
        )
        priorities = operator_priority_service.get_priorities()
        groups = intake.get("project_groups", [])
        suggested_order = self._suggest_order(groups, priorities)
        review = {
            "ok": True,
            "mode": "project_intake_priority_handoff_review",
            "review_id": review_id,
            "created_at": self._now(),
            "tenant_id": tenant_id,
            "requested_project": requested_project,
            "status": "needs_operator_confirmation",
            "safe_run_id": intake.get("run_id"),
            "intake_status": intake.get("status"),
            "operator_summary": intake.get("operator_summary"),
            "suggested_order": suggested_order,
            "suggested_active_project": suggested_order[0] if suggested_order else "GOD_MODE",
            "project_groups": groups,
            "operator_questions": intake.get("operator_questions", []),
            "confirmation_cards": self._confirmation_cards(groups, suggested_order),
            "approval_gates": intake.get("approval_gates", []),
            "blocked_until_operator_confirms": True,
            "destructive_actions_allowed": False,
            "external_ai_scan_permission_default": "manual_login_only_no_prompt_send",
            "next_actions": [
                {
                    "id": "confirm_suggested_order",
                    "label": "Confirmar ordem sugerida",
                    "endpoint": "/api/project-intake-priority-handoff/confirm-suggested",
                    "safe": True,
                },
                {
                    "id": "confirm_custom_order",
                    "label": "Confirmar ordem personalizada",
                    "endpoint": "/api/project-intake-priority-handoff/confirm",
                    "safe": True,
                },
                {
                    "id": "defer",
                    "label": "Não aplicar prioridades agora",
                    "endpoint": "/api/project-intake-priority-handoff/defer",
                    "safe": True,
                },
            ],
        }
        self._save_review(review)
        return review

    def _suggest_order(self, groups: List[Dict[str, Any]], priorities: Dict[str, Any]) -> List[str]:
        current_state = (priorities.get("state") or {}) if priorities.get("ok") else {}
        current_projects = current_state.get("projects") or []
        current_order = [item.get("project_id") for item in current_projects if item.get("enabled", True)]
        group_order: List[str] = []
        for group in groups:
            handling = group.get("handling")
            if handling in {"main_system_project", "single_project_group_multi_repo"}:
                group_order.extend(group.get("repos") or [])
        merged = ["GOD_MODE", *group_order, *current_order, *self.DEFAULT_ORDER]
        return self._flatten_order([item for item in merged if item])

    def _confirmation_cards(self, groups: List[Dict[str, Any]], suggested_order: List[str]) -> List[Dict[str, Any]]:
        return [
            {
                "id": "priority_order",
                "title": "Ordem dos projetos",
                "status": "needs_operator_ok",
                "summary": "Define quais projetos o God Mode deve tratar primeiro. A prioridade vem do operador, não do dinheiro.",
                "suggested_value": suggested_order,
                "requires_confirmation": True,
            },
            {
                "id": "repo_groups",
                "title": "Grupos de repos relacionados",
                "status": "needs_operator_ok",
                "summary": "Confirma se repos separados pertencem ao mesmo ecossistema/projeto.",
                "suggested_value": groups,
                "requires_confirmation": True,
            },
            {
                "id": "external_ai_scan_permission",
                "title": "Permissão para preparar leitura de chats externos",
                "status": "needs_operator_ok",
                "summary": "Permite preparar leitura/scroll com login manual quando necessário. Não envia prompts e não guarda credenciais.",
                "suggested_value": "manual_login_only_no_prompt_send",
                "requires_confirmation": True,
            },
        ]

    def _save_review(self, review: Dict[str, Any]) -> None:
        def mutate(state: Dict[str, Any]) -> Dict[str, Any]:
            state.setdefault("version", 1)
            state.setdefault("policy", "operator_confirms_intake_before_deep_execution")
            state["current_handoff"] = review
            state.setdefault("decisions", [])
            return state

        HANDOFF_STORE.update(mutate)

    def get_current(self) -> Dict[str, Any]:
        state = HANDOFF_STORE.load()
        current = state.get("current_handoff")
        if not current:
            current = self.build_review()
        return {"ok": True, "mode": "project_intake_priority_handoff_current", "current_handoff": current}

    def confirm_suggested(self, tenant_id: str = "owner-andre", note: Optional[str] = None) -> Dict[str, Any]:
        current = self.get_current().get("current_handoff") or self.build_review(tenant_id=tenant_id)
        return self.confirm(
            ordered_project_ids=current.get("suggested_order") or self.DEFAULT_ORDER,
            active_project=current.get("suggested_active_project") or "GOD_MODE",
            tenant_id=tenant_id,
            confirmed_project_groups=current.get("project_groups") or [],
            external_ai_scan_permission="manual_login_only_no_prompt_send",
            note=note or "confirmed suggested intake priority handoff",
        )

    def confirm(
        self,
        ordered_project_ids: List[str],
        active_project: Optional[str] = None,
        tenant_id: str = "owner-andre",
        confirmed_project_groups: Optional[List[Dict[str, Any]]] = None,
        external_ai_scan_permission: str = "manual_login_only_no_prompt_send",
        note: Optional[str] = None,
    ) -> Dict[str, Any]:
        clean_order = self._flatten_order(ordered_project_ids)
        clean_active = self._normalize_project_id(active_project or clean_order[0])
        if clean_active not in clean_order:
            clean_order.insert(0, clean_active)
        priority_result = operator_priority_service.set_order(
            ordered_project_ids=clean_order,
            active_project=clean_active,
            note=note or "operator confirmed intake priority handoff",
        )
        decision = {
            "decision_id": f"intake-priority-decision-{uuid4().hex[:12]}",
            "created_at": self._now(),
            "tenant_id": tenant_id,
            "ordered_project_ids": clean_order,
            "active_project": clean_active,
            "confirmed_project_groups": confirmed_project_groups or [],
            "external_ai_scan_permission": external_ai_scan_permission,
            "destructive_actions_allowed": False,
            "deep_execution_unlocked": True,
            "note": note or "operator confirmed intake priority handoff",
        }

        def mutate(state: Dict[str, Any]) -> Dict[str, Any]:
            state.setdefault("version", 1)
            state.setdefault("policy", "operator_confirms_intake_before_deep_execution")
            state.setdefault("decisions", [])
            state["decisions"].append(decision)
            state["decisions"] = state["decisions"][-100:]
            current = state.get("current_handoff") or {}
            current["status"] = "confirmed"
            current["confirmed_decision_id"] = decision["decision_id"]
            current["blocked_until_operator_confirms"] = False
            state["current_handoff"] = current
            return state

        state = HANDOFF_STORE.update(mutate)
        return {
            "ok": True,
            "mode": "project_intake_priority_handoff_confirmed",
            "decision": decision,
            "priority_result": priority_result,
            "state": state,
            "operator_next": {
                "label": "Avançar para plano de execução profunda aprovado",
                "endpoint": "/api/unified-project-intake/run-safe",
                "route": "/app/home",
            },
        }

    def defer(self, tenant_id: str = "owner-andre", reason: str = "operator_deferred") -> Dict[str, Any]:
        decision = {
            "decision_id": f"intake-priority-defer-{uuid4().hex[:12]}",
            "created_at": self._now(),
            "tenant_id": tenant_id,
            "event": "defer",
            "reason": reason,
            "deep_execution_unlocked": False,
        }

        def mutate(state: Dict[str, Any]) -> Dict[str, Any]:
            state.setdefault("decisions", [])
            state["decisions"].append(decision)
            state["decisions"] = state["decisions"][-100:]
            current = state.get("current_handoff") or {}
            current["status"] = "deferred"
            current["blocked_until_operator_confirms"] = True
            state["current_handoff"] = current
            return state

        state = HANDOFF_STORE.update(mutate)
        return {"ok": True, "mode": "project_intake_priority_handoff_deferred", "decision": decision, "state": state}

    def get_status(self) -> Dict[str, Any]:
        state = HANDOFF_STORE.load()
        current = state.get("current_handoff") or {}
        return {
            "ok": True,
            "mode": "project_intake_priority_handoff_status",
            "status": current.get("status") or "no_review_yet",
            "blocked_until_operator_confirms": current.get("blocked_until_operator_confirms", True),
            "decision_count": len(state.get("decisions") or []),
            "destructive_actions_allowed": False,
            "deep_execution_unlocked": bool((state.get("decisions") or [{}])[-1].get("deep_execution_unlocked", False)) if state.get("decisions") else False,
        }

    def get_package(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "mode": "project_intake_priority_handoff_package",
            "package": {
                "status": self.get_status(),
                "current": self.get_current(),
                "priorities": operator_priority_service.get_priorities(),
            },
        }


project_intake_priority_handoff_service = ProjectIntakePriorityHandoffService()
