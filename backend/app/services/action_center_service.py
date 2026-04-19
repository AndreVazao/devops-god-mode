from typing import Any, Dict, List

from app.services.runtime_supervisor_guidance_service import (
    runtime_supervisor_guidance_service,
)


class ActionCenterService:
    def _build_quick_actions(self) -> List[str]:
        readiness = runtime_supervisor_guidance_service.get_readiness()["readiness"]
        actions: List[str] = []

        if readiness["backend_runtime"] != "backend_runtime_ready":
            actions.append("start_backend_runtime")
        if readiness["shell_runtime"] != "shell_runtime_ready":
            actions.append("start_shell_runtime")

        actions.extend(
            [
                "open_desktop_launcher",
                "open_mobile_pairing",
                "refresh_runtime_summary",
            ]
        )
        return actions

    def get_summary(self) -> Dict[str, Any]:
        recommended = runtime_supervisor_guidance_service.get_recommended_next_action()[
            "recommended_next_action"
        ]
        quick_actions = self._build_quick_actions()
        return {
            "ok": True,
            "mode": "action_center_summary",
            "action_center": {
                "action_center_id": "action_center_pc_phone_primary",
                "runtime_mode": "pc_and_phone_primary",
                "quick_actions": quick_actions,
                "blocked_actions": [],
                "recommended_action": recommended,
                "action_center_status": "action_center_ready",
            },
        }

    def get_quick_actions(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "mode": "action_center_quick_actions",
            "quick_actions": self._build_quick_actions(),
        }

    def get_recommended_action(self) -> Dict[str, Any]:
        return runtime_supervisor_guidance_service.get_recommended_next_action()


action_center_service = ActionCenterService()
