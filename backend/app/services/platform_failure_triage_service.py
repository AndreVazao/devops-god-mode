from typing import Any, Dict, List


class PlatformFailureTriageService:
    def get_failures(self) -> Dict[str, Any]:
        failures: List[Dict[str, Any]] = [
            {
                "platform_failure_id": "platform_failure_vercel_rate_limit_01",
                "platform_name": "vercel",
                "failure_type": "rate_limit",
                "impact_level": "non_blocking",
                "continuation_policy": "continue_main_flow_and_revisit_later",
                "failure_status": "classified",
            },
            {
                "platform_failure_id": "platform_failure_github_validation_01",
                "platform_name": "github_actions",
                "failure_type": "canonical_validation_failure",
                "impact_level": "blocking",
                "continuation_policy": "fix_required_before_merge",
                "failure_status": "classified",
            },
            {
                "platform_failure_id": "platform_failure_remote_link_01",
                "platform_name": "pc_link",
                "failure_type": "temporary_connectivity_loss",
                "impact_level": "deferred",
                "continuation_policy": "buffer_commands_and_resume_when_link_returns",
                "failure_status": "classified",
            },
        ]
        return {"ok": True, "mode": "platform_failures", "failures": failures}

    def get_continuation_decisions(self, target_project: str | None = None) -> Dict[str, Any]:
        decisions: List[Dict[str, Any]] = [
            {
                "continuation_decision_id": "continuation_decision_botfarm_01",
                "target_project": "Bot Farm Headless",
                "decision_type": "continue_without_immediate_fix",
                "decision_reason": "Current external failure does not block project code flow",
                "requires_immediate_fix": False,
                "decision_status": "ready",
            },
            {
                "continuation_decision_id": "continuation_decision_godmode_01",
                "target_project": "DevOps God Mode",
                "decision_type": "fix_before_merge",
                "decision_reason": "Canonical validation failure blocks repository progression",
                "requires_immediate_fix": True,
                "decision_status": "ready",
            },
            {
                "continuation_decision_id": "continuation_decision_remote_01",
                "target_project": "Remote PC Session",
                "decision_type": "continue_locally_and_sync_later",
                "decision_reason": "Temporary link loss does not block current local task",
                "requires_immediate_fix": False,
                "decision_status": "ready",
            },
        ]
        if target_project:
            decisions = [item for item in decisions if item["target_project"] == target_project]
        return {"ok": True, "mode": "continuation_decisions", "decisions": decisions}

    def get_triage_package(self) -> Dict[str, Any]:
        package = {
            "failures": self.get_failures()["failures"],
            "decisions": self.get_continuation_decisions()["decisions"],
            "mobile_compact": True,
            "package_status": "platform_failure_triage_ready",
        }
        return {"ok": True, "mode": "platform_failure_triage_package", "package": package}

    def get_next_triage_action(self) -> Dict[str, Any]:
        blocking_failure = next(
            (item for item in self.get_failures()["failures"] if item["impact_level"] == "blocking"),
            None,
        )
        if blocking_failure:
            return {
                "ok": True,
                "mode": "next_platform_failure_triage_action",
                "next_triage_action": {
                    "platform_failure_id": blocking_failure["platform_failure_id"],
                    "platform_name": blocking_failure["platform_name"],
                    "action": "fix_blocking_failure_before_merge",
                    "failure_status": blocking_failure["failure_status"],
                },
            }

        first_failure = self.get_failures()["failures"][0] if self.get_failures()["failures"] else None
        return {
            "ok": True,
            "mode": "next_platform_failure_triage_action",
            "next_triage_action": {
                "platform_failure_id": first_failure["platform_failure_id"],
                "platform_name": first_failure["platform_name"],
                "action": "continue_main_flow_and_revisit_later",
                "failure_status": first_failure["failure_status"],
            }
            if first_failure
            else None,
        }


platform_failure_triage_service = PlatformFailureTriageService()
