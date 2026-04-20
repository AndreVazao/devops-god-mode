from typing import Any, Dict, List

from app.services.project_recovery_execution_service import (
    project_recovery_execution_service,
)


class ProjectRecoveryLocalApplyService:
    def get_local_apply_bundles(self) -> Dict[str, Any]:
        execution_bundles = project_recovery_execution_service.get_execution_bundles()["bundles"]
        bundles: List[Dict[str, Any]] = []
        for bundle in execution_bundles:
            windows_root = f"C:/GodMode/recovered/{bundle['repo_name']}"
            bundles.append(
                {
                    "local_apply_bundle_id": f"local_apply_{bundle['repo_name']}_01",
                    "recovery_project_id": bundle["recovery_project_id"],
                    "target_root": windows_root,
                    "local_target_count": bundle["file_count"],
                    "apply_mode": "assisted_local_materialization",
                    "apply_status": "planned",
                    "write_ready_bundle_id": f"write_ready_{bundle['repo_name']}_01",
                    "write_target_count": bundle["file_count"],
                    "write_status": "planned",
                }
            )
        return {"ok": True, "mode": "recovery_local_apply_bundles", "bundles": bundles}

    def get_local_targets(self, recovery_project_id: str | None = None) -> Dict[str, Any]:
        target_files = project_recovery_execution_service.get_target_files(recovery_project_id)[
            "target_files"
        ]
        bundles = self.get_local_apply_bundles()["bundles"]
        root_by_project = {
            item["recovery_project_id"]: item["target_root"] for item in bundles
        }
        targets: List[Dict[str, Any]] = []
        for target in target_files:
            root = root_by_project.get(target["recovery_project_id"], "C:/GodMode/recovered")
            targets.append(
                {
                    "local_target_id": f"local_{target['target_file_id']}",
                    "recovery_project_id": target["recovery_project_id"],
                    "local_target_path": f"{root}/{target['target_path']}",
                    "source_target_file_id": target["target_file_id"],
                    "local_role": target["file_role"],
                    "local_status": "planned",
                    "content_strategy": "recovered_script_payload",
                    "write_target_status": "planned",
                }
            )
        return {"ok": True, "mode": "recovery_local_targets", "targets": targets}

    def get_local_apply_package(self, recovery_project_id: str) -> Dict[str, Any]:
        bundle = next(
            (
                item
                for item in self.get_local_apply_bundles()["bundles"]
                if item["recovery_project_id"] == recovery_project_id
            ),
            None,
        )
        if not bundle:
            raise ValueError("recovery_project_not_found")
        targets = self.get_local_targets(recovery_project_id)["targets"]
        package = {
            "bundle": bundle,
            "targets": targets,
            "package_status": "planned",
            "apply_ready": True,
            "write_ready": True,
        }
        return {"ok": True, "mode": "project_recovery_local_apply_package", "package": package}

    def get_write_ready_package(self, recovery_project_id: str) -> Dict[str, Any]:
        package = self.get_local_apply_package(recovery_project_id)["package"]
        write_targets = [
            {
                "recovery_write_target_id": f"write_{target['local_target_id']}",
                "recovery_project_id": target["recovery_project_id"],
                "local_target_id": target["local_target_id"],
                "write_target_path": target["local_target_path"],
                "content_strategy": target["content_strategy"],
                "write_target_status": "planned",
            }
            for target in package["targets"]
        ]
        write_bundle = {
            "recovery_write_bundle_id": package["bundle"]["write_ready_bundle_id"],
            "recovery_project_id": package["bundle"]["recovery_project_id"],
            "local_apply_bundle_id": package["bundle"]["local_apply_bundle_id"],
            "write_target_count": len(write_targets),
            "write_mode": "prepared_for_real_local_write",
            "write_status": "planned",
        }
        return {
            "ok": True,
            "mode": "project_recovery_write_ready_package",
            "package": {
                "write_bundle": write_bundle,
                "write_targets": write_targets,
                "next_layer": "real_local_write",
                "package_status": "planned",
            },
        }

    def get_next_local_action(self) -> Dict[str, Any]:
        bundles = self.get_local_apply_bundles()["bundles"]
        next_bundle = bundles[0] if bundles else None
        return {
            "ok": True,
            "mode": "next_project_recovery_local_action",
            "next_local_action": {
                "local_apply_bundle_id": next_bundle["local_apply_bundle_id"],
                "recovery_project_id": next_bundle["recovery_project_id"],
                "action": "prepare_local_recovered_tree",
                "apply_status": "planned",
            }
            if next_bundle
            else None,
        }

    def get_next_write_ready_action(self) -> Dict[str, Any]:
        bundles = self.get_local_apply_bundles()["bundles"]
        next_bundle = bundles[0] if bundles else None
        return {
            "ok": True,
            "mode": "next_project_recovery_write_ready_action",
            "next_write_ready_action": {
                "recovery_write_bundle_id": next_bundle["write_ready_bundle_id"],
                "recovery_project_id": next_bundle["recovery_project_id"],
                "action": "prepare_payload_for_real_local_write",
                "write_status": "planned",
            }
            if next_bundle
            else None,
        }


project_recovery_local_apply_service = ProjectRecoveryLocalApplyService()
