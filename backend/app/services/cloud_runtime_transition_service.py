from typing import Any, Dict, List


class CloudRuntimeTransitionService:
    def get_legacy_stacks(self) -> Dict[str, Any]:
        legacy_stacks: List[Dict[str, Any]] = [
            {
                "cloud_legacy_retirement_id": "cloud_legacy_retirement_render_01",
                "legacy_stack": "render",
                "retirement_mode": "remove_from_primary_runtime_path",
                "runtime_role_after_retirement": "disabled_for_primary_flow",
                "retirement_status": "ready",
            },
            {
                "cloud_legacy_retirement_id": "cloud_legacy_retirement_supabase_01",
                "legacy_stack": "supabase",
                "retirement_mode": "demote_to_optional_non_central_support",
                "runtime_role_after_retirement": "optional_support_only",
                "retirement_status": "ready",
            },
        ]
        return {"ok": True, "mode": "cloud_legacy_stacks", "legacy_stacks": legacy_stacks}

    def get_cutover_actions(self, target_runtime: str | None = None) -> Dict[str, Any]:
        actions: List[Dict[str, Any]] = [
            {
                "local_first_cutover_action_id": "local_first_cutover_action_pc_runtime_01",
                "target_runtime": "devops_god_mode_runtime",
                "action_type": "promote_local_pc_to_primary_brain",
                "target_component": "runtime_orchestration_core",
                "cutover_status": "ready",
            },
            {
                "local_first_cutover_action_id": "local_first_cutover_action_mobile_01",
                "target_runtime": "mobile_cockpit_runtime",
                "action_type": "bind_mobile_as_remote_cockpit_only",
                "target_component": "mobile_control_surface",
                "cutover_status": "ready",
            },
            {
                "local_first_cutover_action_id": "local_first_cutover_action_cloud_01",
                "target_runtime": "cloud_support_role",
                "action_type": "demote_cloud_to_optional_non_blocking_support",
                "target_component": "render_and_supabase_legacy_stack",
                "cutover_status": "ready",
            },
        ]
        if target_runtime:
            actions = [item for item in actions if item["target_runtime"] == target_runtime]
        return {"ok": True, "mode": "local_first_cutover_actions", "actions": actions}

    def get_transition_package(self) -> Dict[str, Any]:
        package = {
            "legacy_stacks": self.get_legacy_stacks()["legacy_stacks"],
            "actions": self.get_cutover_actions()["actions"],
            "mobile_compact": True,
            "package_status": "cloud_runtime_transition_ready",
        }
        return {"ok": True, "mode": "cloud_runtime_transition_package", "package": package}

    def get_next_transition_action(self) -> Dict[str, Any]:
        first_action = self.get_cutover_actions()["actions"][0] if self.get_cutover_actions()["actions"] else None
        return {
            "ok": True,
            "mode": "next_cloud_runtime_transition_action",
            "next_transition_action": {
                "local_first_cutover_action_id": first_action["local_first_cutover_action_id"],
                "target_runtime": first_action["target_runtime"],
                "action": first_action["action_type"],
                "cutover_status": first_action["cutover_status"],
            }
            if first_action
            else None,
        }


cloud_runtime_transition_service = CloudRuntimeTransitionService()
