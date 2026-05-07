from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List
from uuid import uuid4

from app.services.external_lab_snapshot_reader_service import SNAPSHOT_READER_STORE, external_lab_snapshot_reader_service
from app.services.mobile_approval_cockpit_v2_service import mobile_approval_cockpit_v2_service
from app.services.module_registry_snapshot_service import module_registry_snapshot_service
from app.utils.atomic_json_store import AtomicJsonStore

DATA_DIR = Path("data")
ADOPTION_QUEUE_FILE = DATA_DIR / "native_skills_adoption_queue.json"
ADOPTION_QUEUE_STORE = AtomicJsonStore(
    ADOPTION_QUEUE_FILE,
    default_factory=lambda: {
        "version": 1,
        "adoption_queue_items": [],
        "implementation_plans": [],
        "review_cards": [],
        "decision_log": [],
    },
)

ALLOWED_STATUSES = {
    "proposed",
    "needs_review",
    "approved_for_planning",
    "planned",
    "rejected",
    "quarantined",
}

STATUS_TRANSITIONS = {
    "proposed": {"needs_review", "approved_for_planning", "rejected", "quarantined"},
    "needs_review": {"approved_for_planning", "rejected", "quarantined"},
    "approved_for_planning": {"planned", "needs_review", "rejected", "quarantined"},
    "planned": {"needs_review", "rejected", "quarantined"},
    "rejected": {"needs_review"},
    "quarantined": {"needs_review", "rejected"},
}


class NativeSkillsAdoptionQueueService:
    SERVICE_ID = "native_skills_adoption_queue"
    VERSION = "phase_201_v1"

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def status(self) -> Dict[str, Any]:
        state = ADOPTION_QUEUE_STORE.load()
        return {
            "ok": True,
            "service": self.SERVICE_ID,
            "version": self.VERSION,
            "generated_at": self._now(),
            "store_file": str(ADOPTION_QUEUE_FILE),
            "queue_item_count": len(state.get("adoption_queue_items", [])),
            "implementation_plan_count": len(state.get("implementation_plans", [])),
            "review_card_count": len(state.get("review_cards", [])),
            "allowed_statuses": sorted(ALLOWED_STATUSES),
            "can_apply_code_without_gate": False,
            "can_merge_without_oner_approval": False,
            "requires_actions_validation_before_merge": True,
        }

    def policy(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "policy": {
                "principle": "Native skill candidates can be promoted into an adoption queue for planning, but this queue never applies code directly.",
                "allowed": [
                    "promote native_skill_candidate into adoption_queue_item",
                    "review and classify adoption status",
                    "create implementation plan skeleton based on candidate risk/domain",
                    "create mobile review cards",
                    "prepare future PR through gated GitHub flow",
                ],
                "blocked": [
                    "apply code directly from a candidate",
                    "blind copy from lab/upstream",
                    "merge without green Actions and Oner approval",
                    "release/deploy/browser automation/paid API without Oner approval",
                    "store raw secrets",
                ],
                "statuses": sorted(ALLOWED_STATUSES),
                "status_transitions": {key: sorted(value) for key, value in STATUS_TRANSITIONS.items()},
            },
        }

    def promote_candidate(
        self,
        candidate_id: str,
        target_project: str = "GOD_MODE",
        priority: str = "normal",
        operator_note: str = "",
        tenant_id: str = "owner-andre",
    ) -> Dict[str, Any]:
        candidate = self._find_candidate(candidate_id)
        if not candidate:
            return {"ok": False, "mode": "promote_candidate", "error": "candidate_not_found", "candidate_id": candidate_id}
        existing = self._find_queue_item_by_candidate(candidate_id)
        if existing:
            return {"ok": True, "mode": "promote_candidate", "already_exists": True, "adoption_queue_item": existing}
        status = "quarantined" if candidate.get("risk") == "high_risk" or candidate.get("reuse_mode") == "quarantine_review" else "proposed"
        item = {
            "adoption_queue_item_id": f"adoption-queue-item-{uuid4().hex[:12]}",
            "candidate_id": candidate_id,
            "created_at": self._now(),
            "updated_at": self._now(),
            "tenant_id": tenant_id,
            "target_project": target_project,
            "priority": priority if priority in {"low", "normal", "high", "urgent"} else "normal",
            "status": status,
            "operator_note": operator_note[:1000],
            "candidate": candidate,
            "domain": candidate.get("target_domain"),
            "risk": candidate.get("risk"),
            "reuse_mode": candidate.get("reuse_mode"),
            "next_recommended_action": self._next_action(status, candidate),
            "can_apply_code_directly": False,
            "requires_pr": True,
            "requires_tests": True,
            "requires_oner_approval_for": candidate.get("requires_oner_approval_for", ["merge", "release"]),
        }
        self._store("adoption_queue_items", item)
        self._log("promote_candidate", item["adoption_queue_item_id"], status, operator_note, tenant_id)
        card = self._create_queue_card(item, tenant_id)
        return {"ok": True, "mode": "promote_candidate", "adoption_queue_item": item, "review_card": card}

    def promote_candidates_by_filter(
        self,
        domain: str | None = None,
        risk: str | None = None,
        limit: int = 25,
        target_project: str = "GOD_MODE",
        tenant_id: str = "owner-andre",
    ) -> Dict[str, Any]:
        candidates = external_lab_snapshot_reader_service.list_candidates(domain=domain, risk=risk, limit=limit).get("native_skill_candidates", [])
        promoted = []
        for candidate in candidates:
            result = self.promote_candidate(
                candidate_id=candidate.get("candidate_id", ""),
                target_project=target_project,
                priority="high" if candidate.get("risk") == "high_risk" else "normal",
                operator_note="Promoted by filter from Native Skills Adoption Queue.",
                tenant_id=tenant_id,
            )
            if result.get("ok"):
                promoted.append(result.get("adoption_queue_item"))
        return {"ok": True, "mode": "promote_candidates_by_filter", "count": len(promoted), "adoption_queue_items": promoted}

    def list_queue(self, status: str | None = None, domain: str | None = None, risk: str | None = None, limit: int = 100) -> Dict[str, Any]:
        limit = max(1, min(int(limit), 500))
        items = list(ADOPTION_QUEUE_STORE.load().get("adoption_queue_items", []))
        if status:
            items = [item for item in items if item.get("status") == status]
        if domain:
            items = [item for item in items if item.get("domain") == domain]
        if risk:
            items = [item for item in items if item.get("risk") == risk]
        items.sort(key=lambda item: item.get("updated_at", item.get("created_at", "")), reverse=True)
        return {"ok": True, "mode": "native_skills_adoption_queue_list", "count": len(items[:limit]), "adoption_queue_items": items[:limit]}

    def update_status(
        self,
        adoption_queue_item_id: str,
        new_status: str,
        reason: str = "",
        tenant_id: str = "owner-andre",
    ) -> Dict[str, Any]:
        if new_status not in ALLOWED_STATUSES:
            return {"ok": False, "mode": "update_status", "error": "invalid_status", "allowed_statuses": sorted(ALLOWED_STATUSES)}
        state = ADOPTION_QUEUE_STORE.load()
        items = state.get("adoption_queue_items", [])
        found = None
        for item in items:
            if item.get("adoption_queue_item_id") == adoption_queue_item_id:
                found = item
                break
        if not found:
            return {"ok": False, "mode": "update_status", "error": "queue_item_not_found", "adoption_queue_item_id": adoption_queue_item_id}
        old_status = found.get("status", "proposed")
        if new_status != old_status and new_status not in STATUS_TRANSITIONS.get(old_status, set()):
            return {"ok": False, "mode": "update_status", "error": "transition_not_allowed", "from": old_status, "to": new_status, "allowed_next": sorted(STATUS_TRANSITIONS.get(old_status, set()))}
        found["status"] = new_status
        found["updated_at"] = self._now()
        found["status_reason"] = reason[:1000]
        found["next_recommended_action"] = self._next_action(new_status, found.get("candidate", {}))
        ADOPTION_QUEUE_STORE.update(lambda _state: {**state, "adoption_queue_items": items})
        self._log("update_status", adoption_queue_item_id, f"{old_status}->{new_status}", reason, tenant_id)
        return {"ok": True, "mode": "update_status", "adoption_queue_item": found}

    def create_implementation_plan(
        self,
        adoption_queue_item_id: str,
        target_module_hint: str = "",
        tenant_id: str = "owner-andre",
    ) -> Dict[str, Any]:
        item = self._find_queue_item(adoption_queue_item_id)
        if not item:
            return {"ok": False, "mode": "create_implementation_plan", "error": "queue_item_not_found", "adoption_queue_item_id": adoption_queue_item_id}
        candidate = item.get("candidate", {})
        registry_search = module_registry_snapshot_service.search_modules(target_module_hint or str(candidate.get("target_domain") or "skill"), limit=20)
        high_risk = item.get("risk") == "high_risk" or item.get("status") == "quarantined"
        plan = {
            "implementation_plan_id": f"native-skill-implementation-plan-{uuid4().hex[:12]}",
            "adoption_queue_item_id": adoption_queue_item_id,
            "candidate_id": item.get("candidate_id"),
            "created_at": self._now(),
            "tenant_id": tenant_id,
            "target_project": item.get("target_project", "GOD_MODE"),
            "target_module_hint": target_module_hint[:300],
            "candidate_summary": {
                "name": candidate.get("candidate_name"),
                "domain": candidate.get("target_domain"),
                "source_path": candidate.get("source_path"),
                "lab_repo_full_name": candidate.get("lab_repo_full_name"),
                "upstream": candidate.get("upstream"),
                "risk": candidate.get("risk"),
                "reuse_mode": candidate.get("reuse_mode"),
            },
            "reuse_first_evidence": registry_search,
            "steps": self._implementation_steps(item, registry_search, high_risk),
            "gates": {
                "apply_code": "blocked_until_PR_plan_is_approved",
                "branch_and_PR": "allowed_through_approved_github_flow",
                "tests": "phase_smoke_plus_universal_android_windows_required",
                "merge": "requires_green_actions_and_explicit_oner_approval",
                "release": "requires_explicit_oner_approval",
                "browser_credentials_paid_actions": "blocked_without_specific_high_risk_gate",
            },
            "can_apply_code_directly": False,
            "ready_for_pr_planning": item.get("status") in {"approved_for_planning", "planned"} and not high_risk,
        }
        self._store("implementation_plans", plan)
        self.update_status(adoption_queue_item_id, "planned" if item.get("status") == "approved_for_planning" else item.get("status", "needs_review"), reason="Implementation plan created", tenant_id=tenant_id)
        return {"ok": True, "mode": "create_implementation_plan", "implementation_plan": plan}

    def dashboard(self) -> Dict[str, Any]:
        state = ADOPTION_QUEUE_STORE.load()
        return {
            "ok": True,
            "mode": "native_skills_adoption_queue_dashboard",
            "status": self.status(),
            "policy": self.policy(),
            "queue": state.get("adoption_queue_items", [])[-200:],
            "implementation_plans": state.get("implementation_plans", [])[-100:],
            "review_cards": state.get("review_cards", [])[-100:],
            "decision_log": state.get("decision_log", [])[-150:],
        }

    def package(self) -> Dict[str, Any]:
        return self.dashboard()

    def _find_candidate(self, candidate_id: str) -> Dict[str, Any] | None:
        return next((item for item in SNAPSHOT_READER_STORE.load().get("native_skill_candidates", []) if item.get("candidate_id") == candidate_id), None)

    def _find_queue_item(self, item_id: str) -> Dict[str, Any] | None:
        return next((item for item in ADOPTION_QUEUE_STORE.load().get("adoption_queue_items", []) if item.get("adoption_queue_item_id") == item_id), None)

    def _find_queue_item_by_candidate(self, candidate_id: str) -> Dict[str, Any] | None:
        return next((item for item in ADOPTION_QUEUE_STORE.load().get("adoption_queue_items", []) if item.get("candidate_id") == candidate_id), None)

    def _next_action(self, status: str, candidate: Dict[str, Any]) -> str:
        if status == "quarantined":
            return "Review high-risk scope before planning; no browser/credential/session automation."
        if status == "rejected":
            return "No action unless Oner reopens for review."
        if status == "approved_for_planning":
            return "Create native implementation plan; keep PR/tests/approval gates."
        if status == "planned":
            return "Prepare future PR only after Oner approves the implementation plan."
        if candidate.get("confidence", 0) >= 6:
            return "Review for approval_for_planning; candidate has useful signal."
        return "Needs human review before planning."

    def _implementation_steps(self, item: Dict[str, Any], registry_search: Dict[str, Any], high_risk: bool) -> List[str]:
        steps = [
            "Confirm candidate origin and intended use from lab snapshot evidence.",
            "Check reuse-first module registry results before creating new files.",
            "Design a native God Mode adapter/service/page only if no existing module fits.",
            "Keep lab/upstream as reference; do not add it as central dependency.",
            "Prepare code only in a branch/PR through gated flow.",
            "Run Phase 201 smoke, Universal Total Test, Android APK Build and Windows EXE Build.",
            "Merge only after green checks and explicit Oner approval.",
            "Update AndreOS memory after merge.",
        ]
        if high_risk:
            steps.insert(1, "Stop for quarantine review; implementation is not ready for PR planning.")
        if not registry_search.get("matches"):
            steps.insert(2, "No matching existing module found by hint; still inspect nearby orchestration/lab modules manually.")
        return steps

    def _create_queue_card(self, item: Dict[str, Any], tenant_id: str) -> Dict[str, Any]:
        result = mobile_approval_cockpit_v2_service.create_card(
            title=f"Native skill em fila: {item.get('candidate', {}).get('candidate_name', item.get('candidate_id'))}",
            body=f"Estado={item.get('status')} | domínio={item.get('domain')} | risco={item.get('risk')} | próximo={item.get('next_recommended_action')}. Não aplica código sem PR/gates.",
            card_type="native_skill_adoption_queue_item",
            project_id=item.get("target_project", "GOD_MODE"),
            tenant_id=tenant_id,
            priority="high" if item.get("risk") == "high_risk" else item.get("priority", "normal"),
            requires_approval=False,
            actions=[{"action_id": "review-native-skill-adoption", "label": "Rever adoção", "decision": "review"}],
            source_ref={"type": "native_skill_adoption_queue", "adoption_queue_item_id": item.get("adoption_queue_item_id"), "candidate_id": item.get("candidate_id")},
            metadata={"status": item.get("status"), "can_apply_code_directly": False},
        )
        card = result.get("card")
        if card:
            self._store("review_cards", card)
        return result

    def _log(self, action: str, item_id: str, decision: str, reason: str, tenant_id: str) -> None:
        self._store("decision_log", {"created_at": self._now(), "tenant_id": tenant_id, "action": action, "adoption_queue_item_id": item_id, "decision": decision, "reason": reason[:1000]})

    def _store(self, bucket: str, item: Dict[str, Any]) -> None:
        def mutate(state: Dict[str, Any]) -> Dict[str, Any]:
            state.setdefault(bucket, []).append(item)
            state[bucket] = state.get(bucket, [])[-1500:]
            return state
        ADOPTION_QUEUE_STORE.update(mutate)


native_skills_adoption_queue_service = NativeSkillsAdoptionQueueService()
