from typing import Any, Dict, List


class PcMobileRuntimeTopologyService:
    def get_topologies(self) -> Dict[str, Any]:
        topologies: List[Dict[str, Any]] = [
            {
                "runtime_topology_id": "runtime_topology_pc_mobile_01",
                "primary_brain_node": "local_pc",
                "remote_cockpit_node": "mobile_apk",
                "cloud_runtime_role": "optional_non_blocking_support_only",
                "topology_status": "ready",
            },
            {
                "runtime_topology_id": "runtime_topology_pc_mobile_offline_01",
                "primary_brain_node": "local_pc",
                "remote_cockpit_node": "mobile_apk_with_buffered_commands",
                "cloud_runtime_role": "disabled_during_offline_operation",
                "topology_status": "ready",
            },
        ]
        return {"ok": True, "mode": "pc_mobile_runtime_topologies", "topologies": topologies}

    def get_cloud_policies(self, target_stack: str | None = None) -> Dict[str, Any]:
        policies: List[Dict[str, Any]] = [
            {
                "cloud_dependency_policy_id": "cloud_dependency_policy_pc_mobile_01",
                "target_stack": "devops_god_mode_runtime",
                "policy_mode": "cloud_optional_local_first",
                "cloud_providers": ["render", "supabase"],
                "policy_status": "ready",
            },
            {
                "cloud_dependency_policy_id": "cloud_dependency_policy_pc_mobile_02",
                "target_stack": "devops_god_mode_runtime",
                "policy_mode": "render_disabled_supabase_non_central",
                "cloud_providers": ["render", "supabase"],
                "policy_status": "ready",
            },
            {
                "cloud_dependency_policy_id": "cloud_dependency_policy_pc_mobile_03",
                "target_stack": "mobile_cockpit_runtime",
                "policy_mode": "pc_link_primary_cloud_not_required",
                "cloud_providers": ["render", "supabase"],
                "policy_status": "ready",
            },
        ]
        if target_stack:
            policies = [item for item in policies if item["target_stack"] == target_stack]
        return {"ok": True, "mode": "cloud_dependency_policies", "policies": policies}

    def get_topology_package(self) -> Dict[str, Any]:
        package = {
            "topologies": self.get_topologies()["topologies"],
            "policies": self.get_cloud_policies()["policies"],
            "mobile_compact": True,
            "package_status": "pc_mobile_runtime_topology_ready",
        }
        return {"ok": True, "mode": "pc_mobile_runtime_topology_package", "package": package}

    def get_next_topology_action(self) -> Dict[str, Any]:
        first_policy = self.get_cloud_policies()["policies"][0] if self.get_cloud_policies()["policies"] else None
        return {
            "ok": True,
            "mode": "next_pc_mobile_runtime_topology_action",
            "next_topology_action": {
                "cloud_dependency_policy_id": first_policy["cloud_dependency_policy_id"],
                "target_stack": first_policy["target_stack"],
                "action": "consolidate_pc_mobile_runtime_and_demote_cloud_dependencies",
                "policy_status": first_policy["policy_status"],
            }
            if first_policy
            else None,
        }


pc_mobile_runtime_topology_service = PcMobileRuntimeTopologyService()
