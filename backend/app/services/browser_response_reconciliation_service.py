from typing import Any, Dict, List


class BrowserResponseReconciliationService:
    def get_response_captures(self) -> Dict[str, Any]:
        captures: List[Dict[str, Any]] = [
            {
                "browser_response_capture_id": "browser_response_capture_godmode_01",
                "target_project": "DevOps God Mode",
                "source_provider": "chatgpt",
                "source_execution_id": "browser_continuation_execution_godmode_01",
                "capture_mode": "capture_latest_provider_response_after_continuation",
                "capture_status": "ready",
            },
            {
                "browser_response_capture_id": "browser_response_capture_botfarm_01",
                "target_project": "Bot Farm Headless",
                "source_provider": "deepseek",
                "source_execution_id": "browser_continuation_execution_botfarm_01",
                "capture_mode": "capture_latest_provider_response_after_handoff",
                "capture_status": "ready",
            },
            {
                "browser_response_capture_id": "browser_response_capture_barbudos_01",
                "target_project": "Barbudos Studio Website",
                "source_provider": "chatgpt",
                "source_execution_id": "browser_continuation_execution_barbudos_01",
                "capture_mode": "capture_latest_provider_response_after_rollover",
                "capture_status": "ready",
            },
        ]
        return {"ok": True, "mode": "browser_response_captures", "captures": captures}

    def get_reconciliations(self, target_project: str | None = None) -> Dict[str, Any]:
        reconciliations: List[Dict[str, Any]] = [
            {
                "project_reconciliation_id": "project_reconciliation_godmode_01",
                "target_project": "DevOps God Mode",
                "reconciliation_mode": "classify_and_prepare_output_for_project_integration",
                "extracted_output_kind": "code_and_operational_follow_up",
                "reconciliation_status": "ready",
            },
            {
                "project_reconciliation_id": "project_reconciliation_botfarm_01",
                "target_project": "Bot Farm Headless",
                "reconciliation_mode": "classify_and_prepare_output_for_real_integration_follow_up",
                "extracted_output_kind": "code_and_patch_actions",
                "reconciliation_status": "ready",
            },
            {
                "project_reconciliation_id": "project_reconciliation_barbudos_01",
                "target_project": "Barbudos Studio Website",
                "reconciliation_mode": "classify_and_prepare_output_for_repo_alignment",
                "extracted_output_kind": "content_and_code_follow_up",
                "reconciliation_status": "ready",
            },
        ]
        if target_project:
            reconciliations = [item for item in reconciliations if item["target_project"] == target_project]
        return {"ok": True, "mode": "project_reconciliations", "reconciliations": reconciliations}

    def get_reconciliation_package(self) -> Dict[str, Any]:
        package = {
            "captures": self.get_response_captures()["captures"],
            "reconciliations": self.get_reconciliations()["reconciliations"],
            "mobile_compact": True,
            "package_status": "browser_response_reconciliation_ready",
        }
        return {"ok": True, "mode": "browser_response_reconciliation_package", "package": package}

    def get_next_reconciliation_action(self) -> Dict[str, Any]:
        first_reconciliation = self.get_reconciliations()["reconciliations"][0] if self.get_reconciliations()["reconciliations"] else None
        return {
            "ok": True,
            "mode": "next_browser_response_reconciliation_action",
            "next_reconciliation_action": {
                "project_reconciliation_id": first_reconciliation["project_reconciliation_id"],
                "target_project": first_reconciliation["target_project"],
                "action": "classify_and_prepare_response_for_project_application",
                "reconciliation_status": first_reconciliation["reconciliation_status"],
            }
            if first_reconciliation
            else None,
        }


browser_response_reconciliation_service = BrowserResponseReconciliationService()
