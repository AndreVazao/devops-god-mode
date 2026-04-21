from typing import Any, Dict, List


class MultiFileParsingPlacementService:
    def get_parsing_batches(self) -> Dict[str, Any]:
        batches: List[Dict[str, Any]] = [
            {
                "multi_file_parsing_batch_id": "multi_file_parsing_batch_01",
                "source_origin": "deepseek_mixed_output",
                "batch_scope": "multiple_full_files_in_single_response",
                "boundary_detection_mode": "separator_and_code_structure_inference",
                "parsing_status": "parsing_prepared",
            },
            {
                "multi_file_parsing_batch_id": "multi_file_parsing_batch_02",
                "source_origin": "chat_rollover_or_large_provider_response",
                "batch_scope": "large_project_fragment_recovery",
                "boundary_detection_mode": "code_block_and_path_hint_inference",
                "parsing_status": "parsing_prepared",
            },
        ]
        return {"ok": True, "mode": "multi_file_parsing_batches", "batches": batches}

    def get_placement_decisions(self, probable_file_name: str | None = None) -> Dict[str, Any]:
        decisions: List[Dict[str, Any]] = [
            {
                "automatic_placement_decision_id": "automatic_placement_decision_01",
                "probable_file_name": "project_recovery_write_create.py",
                "probable_target_path": "backend/app/routes/project_recovery_write_create.py",
                "placement_mode": "direct_path_match_or_structure_inference",
                "decision_status": "awaiting_short_confirmation",
            },
            {
                "automatic_placement_decision_id": "automatic_placement_decision_02",
                "probable_file_name": "headless_integration_module.py",
                "probable_target_path": "backend/app/services/headless_integration_module.py",
                "placement_mode": "module_role_inference",
                "decision_status": "awaiting_short_confirmation",
            },
            {
                "automatic_placement_decision_id": "automatic_placement_decision_03",
                "probable_file_name": "README.md",
                "probable_target_path": "README.md",
                "placement_mode": "root_document_match",
                "decision_status": "classified",
            },
        ]
        if probable_file_name:
            decisions = [item for item in decisions if item["probable_file_name"] == probable_file_name]
        return {"ok": True, "mode": "automatic_placement_decisions", "decisions": decisions}

    def get_parsing_package(self) -> Dict[str, Any]:
        package = {
            "batches": self.get_parsing_batches()["batches"],
            "decisions": self.get_placement_decisions()["decisions"],
            "mobile_compact": True,
            "package_status": "multi_file_parsing_ready",
        }
        return {"ok": True, "mode": "multi_file_parsing_placement_package", "package": package}

    def get_next_parsing_action(self) -> Dict[str, Any]:
        decisions = self.get_placement_decisions()["decisions"]
        next_decision = next(
            (item for item in decisions if item["decision_status"] == "awaiting_short_confirmation"),
            decisions[0] if decisions else None,
        )
        return {
            "ok": True,
            "mode": "next_multi_file_parsing_action",
            "next_parsing_action": {
                "automatic_placement_decision_id": next_decision["automatic_placement_decision_id"],
                "probable_file_name": next_decision["probable_file_name"],
                "action": "parse_split_and_place_recovered_fragments",
                "decision_status": next_decision["decision_status"],
            }
            if next_decision
            else None,
        }


multi_file_parsing_placement_service = MultiFileParsingPlacementService()
