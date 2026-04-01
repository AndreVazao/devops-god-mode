from typing import Any

from app.services.repo_tree_advice_v1 import repo_tree_advice_v1
from app.services.repo_tree_drift_v1 import repo_tree_drift_v1


class RepoTreeActionPlanV1:
    def build(self, latest_snapshot_payload: dict[str, Any]) -> dict[str, Any]:
        advice = repo_tree_advice_v1.build(latest_snapshot_payload)
        drift = repo_tree_drift_v1.compare(latest_snapshot_payload)

        plan_items: list[dict[str, Any]] = []

        for item in drift.get("actions", []):
            plan_items.append(
                {
                    "title": item.get("title"),
                    "priority": item.get("priority", "medium"),
                    "decision": "altera",
                    "reason": "Drift documental/estrutural identificado pelo motor de drift.",
                    "approval_required": True,
                }
            )

        for item in advice.get("immediate_actions", []):
            title = item.get("title") or item.get("message")
            if not title:
                continue
            plan_items.append(
                {
                    "title": title,
                    "priority": "high",
                    "decision": "altera",
                    "reason": "Ação imediata derivada da análise estrutural persistida.",
                    "approval_required": True,
                }
            )

        for item in advice.get("short_term_actions", []):
            title = item.get("title") or item.get("message")
            if not title:
                continue
            plan_items.append(
                {
                    "title": title,
                    "priority": "medium",
                    "decision": "ok",
                    "reason": "Ação de curto prazo recomendada para alinhamento progressivo.",
                    "approval_required": True,
                }
            )

        for item in advice.get("watch_items", []):
            title = item.get("title") or item.get("message")
            if not title:
                continue
            plan_items.append(
                {
                    "title": title,
                    "priority": "low",
                    "decision": "rejeita",
                    "reason": "Item de vigilância, sem ação destrutiva imediata.",
                    "approval_required": False,
                }
            )

        deduped: list[dict[str, Any]] = []
        seen_titles: set[str] = set()
        for item in plan_items:
            title = item["title"]
            if title in seen_titles:
                continue
            seen_titles.add(title)
            deduped.append(item)

        headline = deduped[0]["title"] if deduped else "Sem plano de ação prioritário neste momento."

        return {
            "ok": True,
            "mode": "action_plan",
            "repo_full_name": latest_snapshot_payload.get("repo_full_name"),
            "headline": headline,
            "items": deduped,
            "summary": {
                "total": len(deduped),
                "high": len([x for x in deduped if x["priority"] == "high"]),
                "medium": len([x for x in deduped if x["priority"] == "medium"]),
                "low": len([x for x in deduped if x["priority"] == "low"]),
                "approval_required": len([x for x in deduped if x["approval_required"]]),
            },
        }


repo_tree_action_plan_v1 = RepoTreeActionPlanV1()
