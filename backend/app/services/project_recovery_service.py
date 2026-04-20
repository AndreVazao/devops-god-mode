from typing import Any, Dict, List

from app.services.conversation_organization_service import (
    conversation_organization_service,
)
from app.services.multi_ai_intake_and_script_repair_service import (
    multi_ai_intake_and_script_repair_service,
)
from app.services.script_extraction_reuse_service import script_extraction_reuse_service


class ProjectRecoveryService:
    def _source_templates(self) -> List[Dict[str, Any]]:
        return multi_ai_intake_and_script_repair_service.get_sources()["sources"]

    def _recoverable_projects(self) -> List[Dict[str, Any]]:
        groups = conversation_organization_service.get_groups()["groups"]
        scripts = script_extraction_reuse_service.get_extracted_scripts()["scripts"]
        projects: List[Dict[str, Any]] = []
        for group in groups:
            project_scripts = [
                script
                for script in scripts
                if script.get("project_key") == group["project_key"]
            ]
            source_count = 2 if group["project_key"] == "devops_god_mode" else 1
            projects.append(
                {
                    "recovery_project_id": f"recovery_{group['project_key']}_01",
                    "project_key": group["project_key"],
                    "project_name": group["project_key"].replace("_", " ").title(),
                    "source_count": source_count,
                    "recoverable_script_count": len(project_scripts),
                    "recovery_status": "planned",
                    "recovery_summary": f"Project can be reconstructed from grouped conversations and recoverable scripts for {group['project_key']}.",
                }
            )
        return projects

    def get_projects(self) -> Dict[str, Any]:
        projects = sorted(
            self._recoverable_projects(),
            key=lambda item: (
                item["project_key"] != "devops_god_mode",
                -item["recoverable_script_count"],
            ),
        )
        return {"ok": True, "mode": "recoverable_projects", "projects": projects}

    def get_sources(self, recovery_project_id: str | None = None) -> Dict[str, Any]:
        projects = self._recoverable_projects()
        templates = self._source_templates()
        sources: List[Dict[str, Any]] = []
        for project in projects:
            if recovery_project_id and project["recovery_project_id"] != recovery_project_id:
                continue
            primary_platform = "chatgpt"
            secondary_platform = "multi_ai_external"
            sources.append(
                {
                    "recovery_source_id": f"source_{project['project_key']}_chatgpt",
                    "recovery_project_id": project["recovery_project_id"],
                    "source_platform": primary_platform,
                    "conversation_hint": f"{project['project_name']} primary recovery thread",
                    "source_role": "primary_recovery_source",
                    "recovery_priority": "high",
                    "source_status": "planned",
                }
            )
            if project["source_count"] > 1:
                sources.append(
                    {
                        "recovery_source_id": f"source_{project['project_key']}_secondary",
                        "recovery_project_id": project["recovery_project_id"],
                        "source_platform": secondary_platform,
                        "conversation_hint": f"{project['project_name']} secondary AI thread",
                        "source_role": "secondary_recovery_source",
                        "recovery_priority": "medium",
                        "source_status": "planned",
                    }
                )
        if templates and sources:
            sources[0]["source_platform"] = templates[0]["source_platform"]
        return {"ok": True, "mode": "project_recovery_sources", "sources": sources}

    def get_scripts(self, recovery_project_id: str | None = None) -> Dict[str, Any]:
        projects = {item["project_key"]: item for item in self._recoverable_projects()}
        scripts = script_extraction_reuse_service.get_extracted_scripts()["scripts"]
        recoverable: List[Dict[str, Any]] = []
        for script in scripts:
            project_key = script.get("project_key")
            project = projects.get(project_key)
            if not project:
                continue
            if recovery_project_id and project["recovery_project_id"] != recovery_project_id:
                continue
            recoverable.append(
                {
                    "recoverable_script_id": f"recoverable_{script['script_id']}",
                    "recovery_project_id": project["recovery_project_id"],
                    "script_id": script["script_id"],
                    "script_role": script.get("script_type", "project_script"),
                    "source_platform": "chatgpt",
                    "recovery_confidence": 0.93 if project_key == "devops_god_mode" else 0.81,
                    "script_status": "recoverable",
                }
            )
        return {"ok": True, "mode": "recoverable_scripts", "scripts": recoverable}

    def get_repo_blueprint(self, recovery_project_id: str) -> Dict[str, Any]:
        projects = self._recoverable_projects()
        project = next(
            (item for item in projects if item["recovery_project_id"] == recovery_project_id),
            None,
        )
        if not project:
            raise ValueError("recovery_project_not_found")
        blueprint = {
            "repo_name": project["project_key"],
            "tree": [
                "backend/",
                "backend/app/",
                "backend/contracts/",
                "docs/",
                "desktop/",
                "mobile/",
            ],
            "recovered_from": self.get_sources(recovery_project_id)["sources"],
            "recoverable_scripts": self.get_scripts(recovery_project_id)["scripts"],
        }
        return {"ok": True, "mode": "project_recovery_blueprint", "blueprint": blueprint}

    def get_next_recovery(self) -> Dict[str, Any]:
        projects = self.get_projects()["projects"]
        next_project = projects[0] if projects else None
        return {
            "ok": True,
            "mode": "next_project_recovery",
            "next_recovery": next_project,
        }


project_recovery_service = ProjectRecoveryService()
