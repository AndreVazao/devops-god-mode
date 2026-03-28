from typing import Any


class RepoTreeAdviceV1:
    def build(self, snapshot_payload: dict[str, Any]) -> dict[str, Any]:
        snapshot = snapshot_payload.get("snapshot") or {}
        risks = snapshot.get("risks") or []
        recommendations = snapshot.get("recommendations") or []
        frameworks = snapshot.get("frameworks") or []
        repo_types = snapshot.get("repo_types") or []

        immediate_actions: list[dict[str, str]] = []
        short_term_actions: list[dict[str, str]] = []
        watch_items: list[dict[str, str]] = []

        for risk in risks:
            severity = risk.get("severity", "low")
            message = risk.get("message", "")
            key = risk.get("key", "unknown_risk")
            item = {
                "key": key,
                "severity": severity,
                "message": message,
            }
            if severity == "medium":
                immediate_actions.append(item)
            else:
                watch_items.append(item)

        for rec in recommendations:
            normalized = rec.lower()
            item = {
                "title": rec,
                "type": "recommendation",
            }
            if "validar" in normalized or "alinhar" in normalized:
                immediate_actions.append(item)
            elif "comparar" in normalized or "rever" in normalized or "ler" in normalized:
                short_term_actions.append(item)
            else:
                watch_items.append(item)

        context_tags = sorted(set(frameworks + repo_types))

        top_action = None
        if immediate_actions:
            first = immediate_actions[0]
            top_action = first.get("title") or first.get("message")
        elif short_term_actions:
            top_action = short_term_actions[0].get("title")
        else:
            top_action = "Continuar análise progressiva e abrir o preview da árvore quando necessário."

        return {
            "ok": True,
            "mode": "advice",
            "repo_full_name": snapshot_payload.get("repo_full_name"),
            "context_tags": context_tags,
            "top_action": top_action,
            "immediate_actions": immediate_actions,
            "short_term_actions": short_term_actions,
            "watch_items": watch_items,
            "summary": {
                "framework_count": len(frameworks),
                "repo_type_count": len(repo_types),
                "immediate_count": len(immediate_actions),
                "short_term_count": len(short_term_actions),
                "watch_count": len(watch_items),
            },
        }


repo_tree_advice_v1 = RepoTreeAdviceV1()
