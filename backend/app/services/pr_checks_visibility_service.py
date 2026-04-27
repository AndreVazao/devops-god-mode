from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List


class PRChecksVisibilityService:
    """Classify PR/check visibility before merge decisions.

    The GitHub connector sometimes returns a mergeable PR while no workflow runs
    or statuses are visible for the head SHA. This service gives God Mode a
    deterministic classification instead of treating missing checks as green.
    """

    GREEN = {"success", "completed", "passed"}
    RED = {"failure", "failed", "error", "cancelled", "timed_out", "action_required"}
    PENDING = {"pending", "queued", "in_progress", "requested", "waiting"}

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def classify(self, pr: Dict[str, Any], workflow_runs: List[Dict[str, Any]] | None = None, statuses: List[Dict[str, Any]] | None = None) -> Dict[str, Any]:
        workflow_runs = workflow_runs or []
        statuses = statuses or []
        signals = self._normalize_signals(workflow_runs, statuses)
        mergeable = pr.get("mergeable") is True
        state = pr.get("state")
        if not signals:
            classification = "no_checks_reported"
            allowed = False
            reason = "GitHub reported no workflow runs or statuses for this PR head. Do not treat as green."
        elif any(signal["state"] in self.RED for signal in signals):
            classification = "red"
            allowed = False
            reason = "At least one check failed."
        elif any(signal["state"] in self.PENDING for signal in signals):
            classification = "pending"
            allowed = False
            reason = "At least one check is still pending."
        elif all(signal["state"] in self.GREEN for signal in signals):
            classification = "green"
            allowed = mergeable and state == "open"
            reason = "All visible checks are green." if allowed else "Checks are green but PR is not mergeable/open."
        else:
            classification = "unknown"
            allowed = False
            reason = "Checks have unknown states."
        return {
            "ok": True,
            "mode": "pr_checks_visibility_classification",
            "created_at": self._now(),
            "classification": classification,
            "merge_allowed": allowed,
            "reason": reason,
            "pr": {
                "number": pr.get("number"),
                "state": state,
                "mergeable": mergeable,
                "head_sha": pr.get("head_sha"),
                "title": pr.get("title"),
            },
            "signal_count": len(signals),
            "signals": signals,
            "operator_next": self._operator_next(classification),
        }

    def _normalize_signals(self, workflow_runs: List[Dict[str, Any]], statuses: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        signals: List[Dict[str, Any]] = []
        for run in workflow_runs:
            name = run.get("name") or run.get("display_title") or run.get("workflow_name") or "workflow"
            conclusion = run.get("conclusion")
            status = run.get("status")
            if conclusion:
                state = str(conclusion).lower()
            elif status:
                state = str(status).lower()
            else:
                state = "unknown"
            signals.append({"source": "workflow_run", "name": name, "state": state, "url": run.get("html_url") or run.get("display_url")})
        for status in statuses:
            context = status.get("context") or status.get("name") or "status"
            state = str(status.get("state") or status.get("conclusion") or "unknown").lower()
            signals.append({"source": "commit_status", "name": context, "state": state, "url": status.get("target_url") or status.get("url")})
        return signals

    def _operator_next(self, classification: str) -> Dict[str, Any]:
        if classification == "green":
            return {"label": "Pode fazer merge", "kind": "merge"}
        if classification == "no_checks_reported":
            return {"label": "Disparar/confirmar checks antes de merge", "kind": "checks_missing"}
        if classification == "pending":
            return {"label": "Aguardar checks", "kind": "wait"}
        if classification == "red":
            return {"label": "Abrir logs e corrigir", "kind": "fix"}
        return {"label": "Investigar estado dos checks", "kind": "investigate"}

    def demo_scenarios(self) -> Dict[str, Any]:
        base_pr = {"number": 1, "state": "open", "mergeable": True, "head_sha": "demo", "title": "Demo PR"}
        return {
            "ok": True,
            "mode": "pr_checks_visibility_demo",
            "scenarios": {
                "green": self.classify(base_pr, workflow_runs=[{"name": "Universal", "conclusion": "success"}, {"name": "APK", "conclusion": "success"}]),
                "red": self.classify(base_pr, workflow_runs=[{"name": "Universal", "conclusion": "success"}, {"name": "APK", "conclusion": "failure"}]),
                "pending": self.classify(base_pr, workflow_runs=[{"name": "Universal", "status": "in_progress"}]),
                "no_checks_reported": self.classify(base_pr, workflow_runs=[], statuses=[]),
            },
        }

    def get_status(self) -> Dict[str, Any]:
        demo = self.demo_scenarios()["scenarios"]
        return {
            "ok": True,
            "mode": "pr_checks_visibility_status",
            "supported_classifications": ["green", "red", "pending", "no_checks_reported", "unknown"],
            "no_checks_blocks_merge": demo["no_checks_reported"]["merge_allowed"] is False,
            "green_allows_merge": demo["green"]["merge_allowed"] is True,
        }

    def get_package(self) -> Dict[str, Any]:
        return {"ok": True, "mode": "pr_checks_visibility_package", "package": {"status": self.get_status(), "demo": self.demo_scenarios()}}


pr_checks_visibility_service = PRChecksVisibilityService()
