from typing import Any, Dict

from app.services.local_pc_runtime_orchestrator_service import (
    local_pc_runtime_orchestrator_service,
)
from app.services.desktop_mobile_handoff_service import desktop_mobile_handoff_service


class RuntimeSupervisorGuidanceService:
    def get_summary(self) -> Dict[str, Any]:
        runtime = local_pc_runtime_orchestrator_service.get_runtime_state()["runtime"]
        handoff = desktop_mobile_handoff_service.get_handoff_package()["handoff"]
        return {
            "ok": True,
            "mode": "runtime_supervisor_summary",
            "summary": {
                "supervisor_id": "supervisor_pc_phone_primary",
                "runtime_mode": runtime["runtime_mode"],
                "runtime_health": "healthy",
                "bundle_readiness": "ready" if runtime["desktop_bundle"] else "not_ready",
                "pairing_readiness": "ready" if handoff["pairing_asset"] else "not_ready",
                "recommended_next_action": self.get_recommended_next_action()["recommended_next_action"],
                "guidance_status": "supervisor_ready",
            },
        }

    def get_readiness(self) -> Dict[str, Any]:
        runtime = local_pc_runtime_orchestrator_service.get_runtime_state()["runtime"]
        handoff = local_pc_runtime_orchestrator_service.get_mobile_handoff_state()["mobile_handoff_state"]
        return {
            "ok": True,
            "mode": "runtime_supervisor_readiness",
            "readiness": {
                "backend_runtime": runtime["backend_runtime"]["status"],
                "shell_runtime": runtime["shell_runtime"]["status"],
                "desktop_bundle": "ready" if runtime["desktop_bundle"] else "not_ready",
                "mobile_handoff": "ready" if handoff["pairing_asset"] else "not_ready",
                "pairing_code": handoff["pairing_code"],
            },
        }

    def get_recommended_next_action(self) -> Dict[str, Any]:
        readiness = self.get_readiness()["readiness"]
        action = "open_desktop_launcher"
        if readiness["desktop_bundle"] != "ready":
            action = "prepare_desktop_bundle"
        elif readiness["mobile_handoff"] != "ready":
            action = "prepare_mobile_handoff"
        elif readiness["backend_runtime"] != "backend_runtime_ready":
            action = "start_backend_runtime"
        elif readiness["shell_runtime"] != "shell_runtime_ready":
            action = "start_shell_runtime"
        elif readiness["pairing_code"]:
            action = "open_mobile_pairing"
        return {
            "ok": True,
            "mode": "runtime_supervisor_next_action",
            "recommended_next_action": action,
        }


runtime_supervisor_guidance_service = RuntimeSupervisorGuidanceService()
