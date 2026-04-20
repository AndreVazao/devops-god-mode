from typing import Any, Dict, List

from app.services.project_recovery_service import project_recovery_service


class ProjectRecoveryExecutionService:
    def get_execution_bundles(self) -> Dict[str, Any]:
        projects = project_recovery_service.get_projects()["projects"]
        bundles: List[Dict[str, Any]] = []
        for project in projects:
            scripts = project_recovery_service.get_scripts(project["recovery_project_id"])["scripts"]
            bundles.append(
                {
                    "execution_bundle_id": f"bundle_{project['project_key']}_01",
                    "recovery_project_id": project["recovery_project_id"],
                    "repo_name": project["project_key"],
                    "target_root": f"./recovered/{project['project_key']}",
                    "file_count": len(scripts),
                    "execution_status": "planned",
                }
            )
        return {"ok": True, "mode": "recovery_execution_bundles", "bundles": bundles}

    def get_target_files(self, recovery_project_id: str | None = None) -> Dict[str, Any]:
        projects = project_recovery_service.get_projects()["projects"]
        target_files: List[Dict[str, Any]] = []
        for project in projects:
            if recovery_project_id and project["recovery_project_id"] != recovery_project_id:
                continue
            scripts = project_recovery_service.get_scripts(project["recovery_project_id"])["scripts"]
            default_paths = [
                "backend/main.py",
                "backend/app/services/recovered_service.py",
                "backend/contracts/recovered_contract.json",
                "docs/recovered-notes.md",
            ]
            for index, script in enumerate(scripts):
                target_files.append(
                    {
                        "target_file_id": f"target_{script['script_id']}",
                        "recovery_project_id": project["recovery_project_id"],
                        "target_path": default_paths[index % len(default_paths)],
                        "file_role": script.get("script_role", "project_file"),
                        "source_script_id": script["script_id"],
                        "target_status": "planned",
                    }
                )
        return {"ok": True, "mode": "recovery_target_files", "target_files": target_files}

    def get_materialization_plan(self, recovery_project_id: str) -> Dict[str, Any]:
        blueprint = project_recovery_service.get_repo_blueprint(recovery_project_id)["blueprint"]
        target_files = self.get_target_files(recovery_project_id)["target_files"]
        bundle = next(
            (
                item
                for item in self.get_execution_bundles()["bundles"]
                if item["recovery_project_id"] == recovery_project_id
            ),
            None,
        )
        return {
            "ok": True,
            "mode": "project_recovery_materialization_plan",
            "plan": {
                "bundle": bundle,
                "repo_tree": blueprint["tree"],
                "target_files": target_files,
                "plan_status": "planned",
            },
        }

    def get_next_execution(self) -> Dict[str, Any]:
        bundles = self.get_execution_bundles()["bundles"]
        next_bundle = bundles[0] if bundles else None
        return {
            "ok": True,
            "mode": "next_project_recovery_execution",
            "next_execution": {
                "execution_bundle_id": next_bundle["execution_bundle_id"],
                "recovery_project_id": next_bundle["recovery_project_id"],
                "execution_action": "prepare_recovered_repo_bundle",
                "execution_status": "planned",
            }
            if next_bundle
            else None,
        }


project_recovery_execution_service = ProjectRecoveryExecutionService()
