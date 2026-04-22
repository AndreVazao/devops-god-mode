from typing import Any, Dict, List


class LocalProjectApplicationPreparationService:
    def get_preparations(self) -> Dict[str, Any]:
        preparations: List[Dict[str, Any]] = [
            {
                "local_application_preparation_id": "local_application_preparation_godmode_01",
                "target_project": "DevOps God Mode",
                "preparation_mode": "prepare_reconciled_output_for_local_application",
                "prepared_output_kind": "code_patch_and_runtime_follow_up",
                "preparation_status": "ready",
            },
            {
                "local_application_preparation_id": "local_application_preparation_botfarm_01",
                "target_project": "Bot Farm Headless",
                "preparation_mode": "prepare_reconciled_output_for_real_integration_application",
                "prepared_output_kind": "code_file_and_patch_bundle",
                "preparation_status": "ready",
            },
            {
                "local_application_preparation_id": "local_application_preparation_barbudos_01",
                "target_project": "Barbudos Studio Website",
                "preparation_mode": "prepare_reconciled_output_for_repo_alignment_application",
                "prepared_output_kind": "content_and_code_bundle",
                "preparation_status": "ready",
            },
        ]
        return {"ok": True, "mode": "local_project_application_preparations", "preparations": preparations}

    def get_application_items(self, target_project: str | None = None) -> Dict[str, Any]:
        items: List[Dict[str, Any]] = [
            {
                "local_application_item_id": "local_application_item_godmode_01",
                "target_project": "DevOps God Mode",
                "item_kind": "patch",
                "target_path": "backend/main.py",
                "apply_mode": "apply_after_short_review",
                "item_status": "ready",
            },
            {
                "local_application_item_id": "local_application_item_botfarm_01",
                "target_project": "Bot Farm Headless",
                "item_kind": "full_file",
                "target_path": "backend/app/services/headless_integration_module.py",
                "apply_mode": "apply_after_short_review",
                "item_status": "ready",
            },
            {
                "local_application_item_id": "local_application_item_barbudos_01",
                "target_project": "Barbudos Studio Website",
                "item_kind": "operational_follow_up",
                "target_path": "project_root",
                "apply_mode": "queue_for_guided_application",
                "item_status": "ready",
            },
        ]
        if target_project:
            items = [item for item in items if item["target_project"] == target_project]
        return {"ok": True, "mode": "local_application_items", "items": items}

    def get_application_package(self) -> Dict[str, Any]:
        package = {
            "preparations": self.get_preparations()["preparations"],
            "items": self.get_application_items()["items"],
            "mobile_compact": True,
            "package_status": "local_project_application_preparation_ready",
        }
        return {"ok": True, "mode": "local_project_application_preparation_package", "package": package}

    def get_next_application_action(self) -> Dict[str, Any]:
        first_item = self.get_application_items()["items"][0] if self.get_application_items()["items"] else None
        return {
            "ok": True,
            "mode": "next_local_project_application_action",
            "next_application_action": {
                "local_application_item_id": first_item["local_application_item_id"],
                "target_project": first_item["target_project"],
                "action": "prepare_short_review_then_apply_locally",
                "item_status": first_item["item_status"],
            }
            if first_item
            else None,
        }


local_project_application_preparation_service = LocalProjectApplicationPreparationService()
