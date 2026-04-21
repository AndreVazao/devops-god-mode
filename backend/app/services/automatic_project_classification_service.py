from typing import Any, Dict, List


class AutomaticProjectClassificationService:
    def get_classifications(self) -> Dict[str, Any]:
        classifications: List[Dict[str, Any]] = [
            {
                "automatic_project_classification_id": "auto_project_classification_repo_01",
                "source_kind": "repository",
                "source_name": "devops-god-mode",
                "probable_project_type": "devops_orchestration_platform",
                "classification_status": "classified",
            },
            {
                "automatic_project_classification_id": "auto_project_classification_chat_01",
                "source_kind": "conversation_provider",
                "source_name": "chatgpt",
                "probable_project_type": "primary_project_development_context",
                "classification_status": "classified",
            },
            {
                "automatic_project_classification_id": "auto_project_classification_deepseek_01",
                "source_kind": "conversation_provider",
                "source_name": "deepseek",
                "probable_project_type": "blocked_part_continuation_context",
                "classification_status": "classified",
            },
        ]
        return {"ok": True, "mode": "automatic_project_classifications", "classifications": classifications}

    def get_grouping_decisions(self, source_kind: str | None = None) -> Dict[str, Any]:
        decisions: List[Dict[str, Any]] = [
            {
                "project_grouping_decision_id": "project_grouping_decision_01",
                "source_kind": "conversation_provider",
                "probable_project_name": "Bot Farm Headless",
                "grouping_action": "attach_to_existing_project",
                "confidence_band": "high",
                "decision_status": "awaiting_short_confirmation",
            },
            {
                "project_grouping_decision_id": "project_grouping_decision_02",
                "source_kind": "repository",
                "probable_project_name": "DevOps God Mode",
                "grouping_action": "mark_as_primary_project_repo",
                "confidence_band": "high",
                "decision_status": "classified",
            },
            {
                "project_grouping_decision_id": "project_grouping_decision_03",
                "source_kind": "conversation_provider",
                "probable_project_name": "Barbudos Studio Website",
                "grouping_action": "prepare_multi_chat_rollover_chain",
                "confidence_band": "medium",
                "decision_status": "awaiting_short_confirmation",
            },
        ]
        if source_kind:
            decisions = [item for item in decisions if item["source_kind"] == source_kind]
        return {"ok": True, "mode": "project_grouping_decisions", "decisions": decisions}

    def get_classification_package(self) -> Dict[str, Any]:
        package = {
            "classifications": self.get_classifications()["classifications"],
            "decisions": self.get_grouping_decisions()["decisions"],
            "mobile_compact": True,
            "package_status": "automatic_project_classification_ready",
        }
        return {"ok": True, "mode": "automatic_project_classification_package", "package": package}

    def get_next_classification_action(self) -> Dict[str, Any]:
        decisions = self.get_grouping_decisions()["decisions"]
        next_decision = next(
            (item for item in decisions if item["decision_status"] == "awaiting_short_confirmation"),
            decisions[0] if decisions else None,
        )
        return {
            "ok": True,
            "mode": "next_automatic_project_classification_action",
            "next_classification_action": {
                "project_grouping_decision_id": next_decision["project_grouping_decision_id"],
                "source_kind": next_decision["source_kind"],
                "action": "confirm_or_auto_group_project_fragments",
                "decision_status": next_decision["decision_status"],
            }
            if next_decision
            else None,
        }


automatic_project_classification_service = AutomaticProjectClassificationService()
