from __future__ import annotations

from typing import Any, Dict, List

from app.services.secret_vault_service import secret_vault_service


class SharedSecretTopologyService:
    def get_status(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "mode": "shared_secret_topology_status",
            "status": "shared_secret_topology_ready",
        }

    def build_topology(self, project_names: List[str]) -> Dict[str, Any]:
        secrets = secret_vault_service.list_secrets().get("secrets", [])
        topology: List[Dict[str, Any]] = []
        for secret in secrets:
            target_refs = secret.get("target_refs", [])
            matching_projects = [project for project in project_names if any(project in ref for ref in target_refs)]
            if not matching_projects:
                continue
            topology.append(
                {
                    "secret_name": secret.get("secret_name"),
                    "provider": secret.get("provider"),
                    "usage_scope": secret.get("usage_scope"),
                    "projects": matching_projects,
                    "shared_across_project_count": len(matching_projects),
                }
            )
        return {
            "ok": True,
            "mode": "shared_secret_topology_result",
            "topology_status": "shared_secret_topology_ready",
            "project_count": len(project_names),
            "shared_secret_count": len(topology),
            "topology": topology,
        }

    def get_package(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "mode": "shared_secret_topology_package",
            "package": {
                "status": self.get_status(),
                "package_status": "shared_secret_topology_ready",
            },
        }


shared_secret_topology_service = SharedSecretTopologyService()
