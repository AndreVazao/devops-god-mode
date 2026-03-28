from typing import Any


class RepoTreeDriftV1:
    def compare(self, latest_snapshot_payload: dict[str, Any]) -> dict[str, Any]:
        snapshot = latest_snapshot_payload.get("snapshot") or {}
        recommendations = snapshot.get("recommendations") or []
        risks = snapshot.get("risks") or []
        frameworks = snapshot.get("frameworks") or []
        repo_types = snapshot.get("repo_types") or []

        drift_sources: list[dict[str, str]] = []
        findings: list[dict[str, str]] = []
        actions: list[dict[str, str]] = []

        if "contract-aware" in repo_types:
            drift_sources.append({
                "source": "OFFICIAL_STUDIO_WEBSITE_CONTRACT.txt",
                "kind": "contract",
                "status": "needs_validation",
            })
            findings.append({
                "key": "contract_present",
                "severity": "medium",
                "message": "Existe contrato oficial Studio-Website e precisa de validação contra a estrutura real e o registry.",
            })
            actions.append({
                "title": "Validar contrato oficial Studio-Website contra registry e árvore real.",
                "priority": "high",
            })

        if any("repository_tree_reference.txt" in rec.lower() for rec in recommendations) or any(r.get("key") == "contract_tree_drift_risk" for r in risks):
            drift_sources.append({
                "source": "REPOSITORY_TREE_REFERENCE.txt",
                "kind": "tree_reference",
                "status": "needs_comparison",
            })
            findings.append({
                "key": "tree_reference_drift_possible",
                "severity": "medium",
                "message": "Existe referência estrutural declarada; convém comparar contra a árvore real persistida.",
            })
            actions.append({
                "title": "Comparar REPOSITORY_TREE_REFERENCE.txt com o snapshot estrutural atual.",
                "priority": "high",
            })

        if "release-channel" in frameworks:
            drift_sources.append({
                "source": "version.remote.json",
                "kind": "release_surface",
                "status": "governance_review",
            })
            findings.append({
                "key": "release_surface_governance",
                "severity": "medium",
                "message": "A superfície de release remota deve manter coerência entre manifesto, canal e políticas do cockpit.",
            })
            actions.append({
                "title": "Rever governança de versionamento remoto e release channel.",
                "priority": "high",
            })

        overall = "clean"
        if any(item["severity"] == "medium" for item in findings):
            overall = "attention_required"
        if len(findings) >= 3:
            overall = "drift_risk_high"

        return {
            "ok": True,
            "mode": "drift",
            "repo_full_name": latest_snapshot_payload.get("repo_full_name"),
            "overall_status": overall,
            "sources": drift_sources,
            "findings": findings,
            "actions": actions,
            "summary": {
                "source_count": len(drift_sources),
                "finding_count": len(findings),
                "action_count": len(actions),
            },
        }


repo_tree_drift_v1 = RepoTreeDriftV1()
