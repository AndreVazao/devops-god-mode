from typing import Any

from app.services.repo_tree_advice_v1 import repo_tree_advice_v1


class RepoTreeCockpitV1:
    def build(self, latest_snapshot_payload: dict[str, Any]) -> dict[str, Any]:
        advice = repo_tree_advice_v1.build(latest_snapshot_payload)
        snapshot = latest_snapshot_payload.get("snapshot") or {}
        risks = snapshot.get("risks") or []

        severity_counts = {"high": 0, "medium": 0, "low": 0}
        for risk in risks:
            severity = (risk.get("severity") or "low").lower()
            if severity not in severity_counts:
                severity_counts[severity] = 0
            severity_counts[severity] += 1

        return {
            "ok": True,
            "mode": "cockpit",
            "repo_full_name": latest_snapshot_payload.get("repo_full_name"),
            "headline": advice.get("top_action"),
            "status": {
                "analysis_status": snapshot.get("analysis_status"),
                "structural_hash": snapshot.get("structural_hash"),
                "updated_at": snapshot.get("updated_at"),
            },
            "tags": advice.get("context_tags") or [],
            "severity_counts": severity_counts,
            "actions": {
                "immediate": advice.get("immediate_actions") or [],
                "short_term": advice.get("short_term_actions") or [],
                "watch": advice.get("watch_items") or [],
            },
            "summary": advice.get("summary") or {},
            "snapshot": {
                "id": snapshot.get("id"),
                "depth": snapshot.get("depth"),
                "frameworks": snapshot.get("frameworks") or [],
                "repo_types": snapshot.get("repo_types") or [],
                "recommendations": snapshot.get("recommendations") or [],
            },
        }


repo_tree_cockpit_v1 = RepoTreeCockpitV1()
