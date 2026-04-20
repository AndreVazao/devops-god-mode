from typing import Any, Dict, List

from app.services.browser_conversation_intake_service import (
    browser_conversation_intake_service,
)
from app.services.conversation_organization_service import (
    conversation_organization_service,
)
from app.services.script_extraction_reuse_service import script_extraction_reuse_service


class MultiAiIntakeAndScriptRepairService:
    def get_sources(self) -> Dict[str, Any]:
        next_focus = conversation_organization_service.get_next_focus()["next_focus"]
        next_session = browser_conversation_intake_service.get_next_session()["next_session"]
        sources: List[Dict[str, Any]] = [
            {
                "source_id": "source_chatgpt_primary",
                "source_platform": "chatgpt",
                "source_type": "conversation_source",
                "source_priority": "high",
                "intake_status": "active",
                "notes": "Primary AI source for project continuation and script extraction.",
            },
            {
                "source_id": "source_other_ai_secondary",
                "source_platform": "multi_ai_external",
                "source_type": "conversation_source",
                "source_priority": "medium",
                "intake_status": "planned",
                "notes": "Secondary AI source for cross-checking, recovery and script comparison.",
            },
        ]
        if next_focus:
            sources[0]["notes"] = (
                f"Primary AI source aligned to focus {next_focus.get('project_key')}"
            )
        if next_session:
            sources[1]["notes"] = (
                f"Secondary AI source can support intake around session {next_session.get('session_id')}"
            )
        return {"ok": True, "mode": "multi_ai_sources", "sources": sources}

    def get_broken_scripts(self) -> Dict[str, Any]:
        scripts = script_extraction_reuse_service.get_extracted_scripts()["scripts"]
        issues: List[Dict[str, Any]] = []
        for script in scripts[:3]:
            failure_type = "integration_gap" if "backend" in script.get("script_name", "") else "reuse_alignment_gap"
            detection_reason = (
                "script extracted from conversation but still needs alignment with current module layout"
            )
            issues.append(
                {
                    "script_issue_id": f"issue_{script['script_id']}",
                    "script_id": script["script_id"],
                    "failure_type": failure_type,
                    "severity": "high" if failure_type == "integration_gap" else "medium",
                    "detection_reason": detection_reason,
                    "repair_status": "planned",
                }
            )
        return {"ok": True, "mode": "broken_script_issues", "issues": issues}

    def get_repair_plan(self) -> Dict[str, Any]:
        issues = self.get_broken_scripts()["issues"]
        steps: List[Dict[str, Any]] = []
        for issue in issues:
            steps.append(
                {
                    "repair_step_id": f"repair_step_{issue['script_id']}",
                    "script_issue_id": issue["script_issue_id"],
                    "repair_action": "normalize_imports_and_realign_context",
                    "expected_fix": "script aligns with current project layout and can re-enter execution flow",
                    "confirmation_required": True,
                    "step_status": "planned",
                }
            )
        return {"ok": True, "mode": "script_repair_plan", "repair_steps": steps}

    def get_next_repair(self) -> Dict[str, Any]:
        issues = self.get_broken_scripts()["issues"]
        next_issue = issues[0] if issues else None
        return {
            "ok": True,
            "mode": "next_script_repair",
            "next_repair": next_issue,
        }


multi_ai_intake_and_script_repair_service = MultiAiIntakeAndScriptRepairService()
