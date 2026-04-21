from typing import Any, Dict, List


class PlatformControlHardeningService:
    def get_control_surfaces(self) -> Dict[str, Any]:
        surfaces: List[Dict[str, Any]] = [
            {
                "platform_control_id": "platform_control_github_01",
                "platform_name": "github",
                "control_scope": ["repos", "prs", "actions", "artifacts"],
                "readiness_status": "connected_ready",
                "priority_action_count": 2,
            },
            {
                "platform_control_id": "platform_control_vercel_01",
                "platform_name": "vercel",
                "control_scope": ["projects", "deployments", "domains"],
                "readiness_status": "planned_connector_or_api_link",
                "priority_action_count": 1,
            },
            {
                "platform_control_id": "platform_control_render_01",
                "platform_name": "render",
                "control_scope": ["services", "deploys", "env"],
                "readiness_status": "planned_connector_or_api_link",
                "priority_action_count": 1,
            },
            {
                "platform_control_id": "platform_control_supabase_01",
                "platform_name": "supabase",
                "control_scope": ["projects", "database", "auth", "storage"],
                "readiness_status": "planned_connector_or_api_link",
                "priority_action_count": 1,
            },
        ]
        return {"ok": True, "mode": "platform_control_surfaces", "surfaces": surfaces}

    def get_platform_actions(self, platform_name: str | None = None) -> Dict[str, Any]:
        actions: List[Dict[str, Any]] = [
            {
                "platform_control_action_id": "platform_action_github_01",
                "platform_name": "github",
                "action_type": "manage_repo_and_pr_flow",
                "action_label": "Gerir repos, PRs, Actions e artefactos",
                "action_status": "ready",
                "capability_state": "connected_ready",
            },
            {
                "platform_control_action_id": "platform_action_vercel_01",
                "platform_name": "vercel",
                "action_type": "inspect_project_linkage",
                "action_label": "Ver estado do projeto principal no Vercel",
                "action_status": "pending",
                "capability_state": "planned_connector_or_api_link",
            },
            {
                "platform_control_action_id": "platform_action_render_01",
                "platform_name": "render",
                "action_type": "inspect_service_linkage",
                "action_label": "Ver estado do serviço principal no Render",
                "action_status": "pending",
                "capability_state": "planned_connector_or_api_link",
            },
            {
                "platform_control_action_id": "platform_action_supabase_01",
                "platform_name": "supabase",
                "action_type": "inspect_project_linkage",
                "action_label": "Ver estado do projeto principal no Supabase",
                "action_status": "pending",
                "capability_state": "planned_connector_or_api_link",
            },
        ]
        if platform_name:
            actions = [item for item in actions if item["platform_name"] == platform_name]
        return {"ok": True, "mode": "platform_control_actions", "actions": actions}

    def get_control_package(self, platform_name: str) -> Dict[str, Any]:
        surface = next(
            item for item in self.get_control_surfaces()["surfaces"] if item["platform_name"] == platform_name
        )
        package = {
            "surface": surface,
            "actions": self.get_platform_actions(platform_name)["actions"],
            "mobile_compact": True,
            "package_status": surface["readiness_status"],
        }
        return {"ok": True, "mode": "platform_control_package", "package": package}

    def get_next_platform_action(self) -> Dict[str, Any]:
        surfaces = self.get_control_surfaces()["surfaces"]
        next_surface = next(
            (item for item in surfaces if item["readiness_status"] != "connected_ready"),
            surfaces[0] if surfaces else None,
        )
        return {
            "ok": True,
            "mode": "next_platform_control_action",
            "next_platform_action": {
                "platform_control_id": next_surface["platform_control_id"],
                "platform_name": next_surface["platform_name"],
                "action": "prepare_real_platform_linkage_without_bloating_cockpit",
                "readiness_status": next_surface["readiness_status"],
            }
            if next_surface
            else None,
        }


platform_control_hardening_service = PlatformControlHardeningService()
