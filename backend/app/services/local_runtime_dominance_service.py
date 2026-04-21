from typing import Any, Dict, List


class LocalRuntimeDominanceService:
    def get_dominance_surfaces(self) -> Dict[str, Any]:
        surfaces: List[Dict[str, Any]] = [
            {
                "local_runtime_dominance_id": "local_runtime_dominance_01",
                "dominant_runtime": "pc_primary_runtime",
                "remote_client_mode": "apk_thin_remote_cockpit",
                "support_cloud_mode": "optional_support_only",
                "dominance_status": "local_runtime_dominant_ready",
            },
            {
                "local_runtime_dominance_id": "local_runtime_dominance_02",
                "dominant_runtime": "pc_primary_runtime",
                "remote_client_mode": "desktop_secondary_surface",
                "support_cloud_mode": "relay_or_test_only",
                "dominance_status": "secondary_surface_ready",
            },
        ]
        return {"ok": True, "mode": "local_runtime_dominance_surfaces", "surfaces": surfaces}

    def get_runtime_actions(self, runtime_area: str | None = None) -> Dict[str, Any]:
        actions: List[Dict[str, Any]] = [
            {
                "local_runtime_action_id": "local_runtime_action_01",
                "runtime_area": "brain_execution",
                "action_type": "route_primary_execution_to_pc",
                "action_label": "Executar cérebro principal no PC",
                "execution_path": "pc_only_primary",
                "action_status": "planned",
            },
            {
                "local_runtime_action_id": "local_runtime_action_02",
                "runtime_area": "voice_path",
                "action_type": "capture_on_apk_interpret_on_pc",
                "action_label": "Captar voz no APK e interpretar no PC",
                "execution_path": "apk_to_pc",
                "action_status": "planned",
            },
            {
                "local_runtime_action_id": "local_runtime_action_03",
                "runtime_area": "cloud_support",
                "action_type": "keep_cloud_as_support_only",
                "action_label": "Manter cloud apenas como apoio opcional",
                "execution_path": "support_only",
                "action_status": "planned",
            },
        ]
        if runtime_area:
            actions = [item for item in actions if item["runtime_area"] == runtime_area]
        return {"ok": True, "mode": "local_runtime_actions", "actions": actions}

    def get_dominance_package(self) -> Dict[str, Any]:
        package = {
            "surfaces": self.get_dominance_surfaces()["surfaces"],
            "actions": self.get_runtime_actions()["actions"],
            "mobile_compact": True,
            "package_status": "local_runtime_dominant_ready",
        }
        return {"ok": True, "mode": "local_runtime_dominance_package", "package": package}

    def get_next_runtime_action(self) -> Dict[str, Any]:
        actions = self.get_runtime_actions()["actions"]
        next_action = actions[0] if actions else None
        return {
            "ok": True,
            "mode": "next_local_runtime_action",
            "next_runtime_action": {
                "local_runtime_action_id": next_action["local_runtime_action_id"],
                "runtime_area": next_action["runtime_area"],
                "action": "advance_local_runtime_as_primary_path",
                "action_status": next_action["action_status"],
            }
            if next_action
            else None,
        }


local_runtime_dominance_service = LocalRuntimeDominanceService()
