from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List
from uuid import uuid4

from app.services.artifacts_center_service import artifacts_center_service
from app.services.first_pc_install_ready_pack_service import first_pc_install_ready_pack_service
from app.services.first_pc_runtime_verification_service import first_pc_runtime_verification_service
from app.services.god_mode_global_state_service import god_mode_global_state_service
from app.services.mobile_approval_cockpit_v2_service import mobile_approval_cockpit_v2_service
from app.services.module_registry_snapshot_service import module_registry_snapshot_service
from app.services.native_skills_adoption_queue_service import native_skills_adoption_queue_service
from app.utils.atomic_json_store import AtomicJsonStore

DATA_DIR = Path("data")
SELF_DIAGNOSIS_FILE = DATA_DIR / "god_mode_self_diagnosis_mission_control.json"
SELF_DIAGNOSIS_STORE = AtomicJsonStore(
    SELF_DIAGNOSIS_FILE,
    default_factory=lambda: {"version": 1, "diagnostic_runs": [], "self_fix_queue": [], "review_cards": [], "decision_log": []},
)

SEVERITY_ORDER = {"blocker": 4, "high": 3, "medium": 2, "low": 1}
FIX_STATUSES = {"open", "needs_review", "approved_for_planning", "planned", "blocked", "done", "dismissed"}


class GodModeSelfDiagnosisMissionControlService:
    SERVICE_ID = "god_mode_self_diagnosis_mission_control"
    VERSION = "phase_203_v1"

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def status(self) -> Dict[str, Any]:
        state = SELF_DIAGNOSIS_STORE.load()
        return {
            "ok": True,
            "service": self.SERVICE_ID,
            "version": self.VERSION,
            "generated_at": self._now(),
            "store_file": str(SELF_DIAGNOSIS_FILE),
            "diagnostic_run_count": len(state.get("diagnostic_runs", [])),
            "self_fix_queue_count": len(state.get("self_fix_queue", [])),
            "can_apply_fix_without_gate": False,
            "can_merge_without_oner_approval": False,
            "purpose": "Diagnose what is still missing for God Mode to become real, installable and self-improvable through gated PRs.",
        }

    def policy(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "policy": {
                "principle": "Self diagnosis may create prioritized self-fix queue items, but it does not patch, merge, release or deploy by itself.",
                "allowed": [
                    "aggregate readiness/install/runtime/artifact/global-state evidence",
                    "detect missing or weak modules",
                    "create self_fix_queue_item records",
                    "prioritize install blockers before future improvements",
                    "create mobile review cards",
                    "prepare future PR planning inputs",
                ],
                "blocked": [
                    "apply code without PR",
                    "merge without Oner approval",
                    "release/deploy/update-final without Oner approval",
                    "store raw secrets",
                    "browser automation against private sessions",
                ],
                "fix_statuses": sorted(FIX_STATUSES),
            },
        }

    def run_diagnosis(self, tenant_id: str = "owner-andre", focus: str = "install_first_then_self_evolve") -> Dict[str, Any]:
        evidence = self._collect_evidence()
        gaps = self._detect_gaps(evidence, focus)
        gaps.sort(key=lambda item: (SEVERITY_ORDER.get(item.get("severity", "low"), 0), item.get("priority", 0)), reverse=True)
        run = {
            "diagnostic_run_id": f"self-diagnosis-run-{uuid4().hex[:12]}",
            "created_at": self._now(),
            "tenant_id": tenant_id,
            "focus": focus,
            "gap_count": len(gaps),
            "blocker_count": len([gap for gap in gaps if gap.get("severity") == "blocker"]),
            "high_count": len([gap for gap in gaps if gap.get("severity") == "high"]),
            "evidence_summary": self._evidence_summary(evidence),
            "gaps": gaps,
            "can_apply_fix_without_gate": False,
        }
        self._store("diagnostic_runs", run)
        queue_items = [self._queue_item_from_gap(run, gap, tenant_id) for gap in gaps]
        for item in queue_items:
            self._upsert_queue_item(item)
        card = self._create_review_card(run, queue_items, tenant_id)
        return {"ok": True, "mode": "god_mode_self_diagnosis", "diagnostic_run": run, "self_fix_queue_items": queue_items, "review_card": card}

    def list_queue(self, status: str | None = None, severity: str | None = None, install_blocker: bool | None = None, limit: int = 100) -> Dict[str, Any]:
        limit = max(1, min(int(limit), 500))
        items = list(SELF_DIAGNOSIS_STORE.load().get("self_fix_queue", []))
        if status:
            items = [item for item in items if item.get("status") == status]
        if severity:
            items = [item for item in items if item.get("severity") == severity]
        if install_blocker is not None:
            items = [item for item in items if bool(item.get("install_blocker")) is install_blocker]
        items.sort(key=lambda item: (SEVERITY_ORDER.get(item.get("severity", "low"), 0), item.get("created_at", "")), reverse=True)
        return {"ok": True, "mode": "self_fix_queue_list", "count": len(items[:limit]), "self_fix_queue": items[:limit]}

    def update_queue_item(self, self_fix_queue_item_id: str, status: str, note: str = "", tenant_id: str = "owner-andre") -> Dict[str, Any]:
        if status not in FIX_STATUSES:
            return {"ok": False, "mode": "update_self_fix_queue_item", "error": "invalid_status", "allowed_statuses": sorted(FIX_STATUSES)}
        state = SELF_DIAGNOSIS_STORE.load()
        items = state.get("self_fix_queue", [])
        found = None
        for item in items:
            if item.get("self_fix_queue_item_id") == self_fix_queue_item_id:
                found = item
                break
        if not found:
            return {"ok": False, "mode": "update_self_fix_queue_item", "error": "self_fix_queue_item_not_found", "self_fix_queue_item_id": self_fix_queue_item_id}
        found["status"] = status
        found["updated_at"] = self._now()
        found["operator_note"] = note[:1000]
        SELF_DIAGNOSIS_STORE.update(lambda _state: {**state, "self_fix_queue": items})
        self._log("update_queue_item", self_fix_queue_item_id, status, note, tenant_id)
        return {"ok": True, "mode": "update_self_fix_queue_item", "self_fix_queue_item": found}

    def create_pr_planning_brief(self, self_fix_queue_item_id: str, tenant_id: str = "owner-andre") -> Dict[str, Any]:
        item = self._find_queue_item(self_fix_queue_item_id)
        if not item:
            return {"ok": False, "mode": "self_fix_pr_planning_brief", "error": "self_fix_queue_item_not_found", "self_fix_queue_item_id": self_fix_queue_item_id}
        brief = {
            "brief_id": f"self-fix-pr-brief-{uuid4().hex[:12]}",
            "created_at": self._now(),
            "tenant_id": tenant_id,
            "self_fix_queue_item_id": self_fix_queue_item_id,
            "title": item.get("title"),
            "severity": item.get("severity"),
            "target_module": item.get("target_module"),
            "reason": item.get("reason"),
            "recommended_next_step": item.get("recommended_next_step"),
            "reuse_first_query": item.get("reuse_first_query"),
            "required_gates": ["branch", "PR", "phase smoke", "Universal Total Test", "Android APK Build", "Windows EXE Build", "Oner approval before merge"],
            "blocked_actions": ["direct merge", "release", "deploy", "secret storage", "browser automation"],
            "can_apply_code_directly": False,
        }
        self._log("create_pr_planning_brief", self_fix_queue_item_id, "brief_created", brief["title"], tenant_id)
        return {"ok": True, "mode": "self_fix_pr_planning_brief", "brief": brief}

    def dashboard(self) -> Dict[str, Any]:
        state = SELF_DIAGNOSIS_STORE.load()
        latest = state.get("diagnostic_runs", [])[-1:] or []
        return {
            "ok": True,
            "mode": "god_mode_self_diagnosis_dashboard",
            "status": self.status(),
            "policy": self.policy(),
            "latest_diagnostic_run": latest[0] if latest else None,
            "self_fix_queue": self.list_queue(limit=200).get("self_fix_queue", []),
            "review_cards": state.get("review_cards", [])[-100:],
            "decision_log": state.get("decision_log", [])[-150:],
        }

    def package(self) -> Dict[str, Any]:
        return self.dashboard()

    def _collect_evidence(self) -> Dict[str, Any]:
        return {
            "global_state": self._safe_call(god_mode_global_state_service.package),
            "install_ready_pack": self._safe_call(first_pc_install_ready_pack_service.package),
            "runtime_verification": self._safe_call(first_pc_runtime_verification_service.package),
            "artifacts": self._safe_call(artifacts_center_service.build_dashboard),
            "module_registry": self._safe_call(module_registry_snapshot_service.package),
            "native_skills_queue": self._safe_call(native_skills_adoption_queue_service.package),
        }

    def _detect_gaps(self, evidence: Dict[str, Any], focus: str) -> List[Dict[str, Any]]:
        gaps: List[Dict[str, Any]] = []
        install_status = evidence.get("install_ready_pack", {}).get("status", {})
        if install_status.get("ready_for_first_pc_install") is not True:
            gaps.append(self._gap("pc_install_not_fully_ready", "blocker", "first_pc_install_ready_pack", "First PC install readiness is not fully green.", "Fix install/artifact/readiness blockers first.", True, 100))
        artifacts = evidence.get("artifacts", {})
        if artifacts.get("status") not in {"ready", None}:
            gaps.append(self._gap("artifacts_not_ready", "blocker", "artifacts_center", "Windows/Android artifacts are not reported ready.", "Inspect artifact workflows and expose direct operator download path.", True, 95))
        global_status = evidence.get("global_state", {}).get("status", {})
        if int(global_status.get("current_phase") or 0) < 202:
            gaps.append(self._gap("global_state_stale", "high", "god_mode_global_state", "Global state does not reflect the latest install-ready phase.", "Update global state and memory alignment.", True, 90))
        native_queue = evidence.get("native_skills_queue", {}).get("queue", []) or evidence.get("native_skills_queue", {}).get("self_fix_queue", [])
        if not native_queue:
            gaps.append(self._gap("self_evolution_queue_empty", "medium", "native_skills_adoption_queue", "No native self-evolution queue items are active yet.", "Seed or promote candidates after first PC run.", False, 70))
        module_registry_status = evidence.get("module_registry", {}).get("status", {})
        if module_registry_status.get("official_tree_present") is False:
            gaps.append(self._gap("project_tree_missing", "medium", "module_registry_snapshot", "Official GOD_MODE tree is missing until autorefresh runs.", "Run project tree autorefresh after next main push.", False, 60))
        gaps.append(self._gap("first_real_pc_feedback_missing", "high", "first_pc_install_ready_pack", "No real PC first-run feedback has been recorded yet.", "Install/run GodModeDesktop.exe and record first-run outcome in the cockpit.", True, 85))
        gaps.append(self._gap("candidate_to_pr_generator_missing", "medium", "self_evolution", "Adoption queue can plan, but does not yet generate PR-ready patch plans automatically.", "Build Candidate-to-PR Plan Generator after first PC install path is proven.", False, 50))
        return gaps

    def _gap(self, gap_id: str, severity: str, target_module: str, reason: str, next_step: str, install_blocker: bool, priority: int) -> Dict[str, Any]:
        return {
            "gap_id": gap_id,
            "severity": severity,
            "target_module": target_module,
            "reason": reason,
            "recommended_next_step": next_step,
            "install_blocker": install_blocker,
            "priority": priority,
            "reuse_first_query": target_module.replace("_", " "),
        }

    def _queue_item_from_gap(self, run: Dict[str, Any], gap: Dict[str, Any], tenant_id: str) -> Dict[str, Any]:
        status = "open" if gap.get("severity") in {"blocker", "high"} else "needs_review"
        return {
            "self_fix_queue_item_id": f"self-fix-{gap['gap_id']}",
            "diagnostic_run_id": run.get("diagnostic_run_id"),
            "created_at": self._now(),
            "updated_at": self._now(),
            "tenant_id": tenant_id,
            "title": gap["gap_id"].replace("_", " ").title(),
            "status": status,
            "severity": gap.get("severity"),
            "install_blocker": bool(gap.get("install_blocker")),
            "target_module": gap.get("target_module"),
            "reason": gap.get("reason"),
            "recommended_next_step": gap.get("recommended_next_step"),
            "priority": gap.get("priority"),
            "reuse_first_query": gap.get("reuse_first_query"),
            "can_apply_fix_directly": False,
            "requires_pr": True,
            "requires_tests": True,
        }

    def _upsert_queue_item(self, item: Dict[str, Any]) -> None:
        def mutate(state: Dict[str, Any]) -> Dict[str, Any]:
            bucket = state.setdefault("self_fix_queue", [])
            for index, existing in enumerate(bucket):
                if existing.get("self_fix_queue_item_id") == item.get("self_fix_queue_item_id"):
                    merged = {**existing, **item, "created_at": existing.get("created_at", item.get("created_at"))}
                    bucket[index] = merged
                    return state
            bucket.append(item)
            state["self_fix_queue"] = bucket[-1500:]
            return state
        SELF_DIAGNOSIS_STORE.update(mutate)

    def _find_queue_item(self, item_id: str) -> Dict[str, Any] | None:
        return next((item for item in SELF_DIAGNOSIS_STORE.load().get("self_fix_queue", []) if item.get("self_fix_queue_item_id") == item_id), None)

    def _create_review_card(self, run: Dict[str, Any], queue_items: List[Dict[str, Any]], tenant_id: str) -> Dict[str, Any]:
        blockers = [item for item in queue_items if item.get("install_blocker")]
        result = mobile_approval_cockpit_v2_service.create_card(
            title="God Mode self-diagnosis ready",
            body=f"{len(queue_items)} lacunas criadas; {len(blockers)} bloqueiam instalação/uso real. Nada corrige sem PR/gates.",
            card_type="god_mode_self_diagnosis",
            project_id="GOD_MODE",
            tenant_id=tenant_id,
            priority="high" if blockers else "normal",
            requires_approval=False,
            actions=[{"action_id": "review-self-fix-queue", "label": "Rever lacunas", "decision": "review"}],
            source_ref={"type": "god_mode_self_diagnosis", "diagnostic_run_id": run.get("diagnostic_run_id")},
            metadata={"gap_count": len(queue_items), "install_blocker_count": len(blockers), "can_apply_fix_directly": False},
        )
        card = result.get("card")
        if card:
            self._store("review_cards", card)
        return result

    def _evidence_summary(self, evidence: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "current_phase": evidence.get("global_state", {}).get("status", {}).get("current_phase"),
            "ready_for_first_pc_install": evidence.get("install_ready_pack", {}).get("status", {}).get("ready_for_first_pc_install"),
            "artifact_status": evidence.get("artifacts", {}).get("status"),
            "official_tree_present": evidence.get("module_registry", {}).get("status", {}).get("official_tree_present"),
        }

    def _safe_call(self, fn) -> Dict[str, Any]:
        try:
            result = fn()
            return result if isinstance(result, dict) else {"ok": True, "value": result}
        except Exception as exc:  # pragma: no cover
            return {"ok": False, "error": str(exc), "function": getattr(fn, "__name__", "unknown")}

    def _store(self, bucket: str, item: Dict[str, Any]) -> None:
        def mutate(state: Dict[str, Any]) -> Dict[str, Any]:
            state.setdefault(bucket, []).append(item)
            state[bucket] = state.get(bucket, [])[-1500:]
            return state
        SELF_DIAGNOSIS_STORE.update(mutate)

    def _log(self, action: str, item_id: str, decision: str, reason: str, tenant_id: str) -> None:
        self._store("decision_log", {"created_at": self._now(), "tenant_id": tenant_id, "action": action, "self_fix_queue_item_id": item_id, "decision": decision, "reason": reason[:1000]})


god_mode_self_diagnosis_mission_control_service = GodModeSelfDiagnosisMissionControlService()
