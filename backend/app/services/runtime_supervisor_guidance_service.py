from typing import Any, Dict

from app.services.desktop_mobile_handoff_service import desktop_mobile_handoff_service
from app.services.local_pc_runtime_orchestrator_service import (
    local_pc_runtime_orchestrator_service,
)


class RuntimeSupervisorGuidanceService:
    def _runtime_health(self, readiness: Dict[str, Any]) -> str:
        backend_ok = readiness["backend_runtime"] == "runtime_reachable"
        shell_ok = readiness["shell_runtime"] == "runtime_reachable"
        pairing_ok = readiness["mobile_handoff"] == "ready"
        if backend_ok and shell_ok and pairing_ok:
            return "healthy"
        if backend_ok or shell_ok:
            return "partial"
        return "waiting_local_runtime"

    def get_summary(self) -> Dict[str, Any]:
        runtime = local_pc_runtime_orchestrator_service.get_runtime_state()["runtime"]
        handoff = desktop_mobile_handoff_service.get_handoff_package()["handoff"]
        readiness = self.get_readiness()["readiness"]
        return {
            "ok": True,
            "mode": "runtime_supervisor_summary",
            "summary": {
                "supervisor_id": "supervisor_pc_phone_primary",
                "runtime_mode": runtime["runtime_mode"],
                "runtime_health": self._runtime_health(readiness),
                "bundle_readiness": readiness["desktop_bundle"],
                "pairing_readiness": "ready" if handoff["pairing_asset"] else "not_ready",
                "recommended_next_action": self.get_recommended_next_action()["recommended_next_action"],
                "guidance_status": runtime["orchestrator_status"],
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
                "desktop_bundle": runtime["desktop_bundle"]["bundle_status"],
                "mobile_handoff": "ready" if handoff["pairing_asset"] else "not_ready",
                "pairing_code": handoff["pairing_code"],
            },
        }

    def get_recommended_next_action(self) -> Dict[str, Any]:
        readiness = self.get_readiness()["readiness"]
        action = "open_desktop_launcher"
        if readiness["desktop_bundle"] != "bundle_manifest_ready":
            action = "prepare_desktop_bundle"
        elif readiness["backend_runtime"] != "runtime_reachable":
            action = "start_backend_runtime"
        elif readiness["shell_runtime"] != "runtime_reachable":
            action = "start_shell_runtime"
        elif readiness["mobile_handoff"] != "ready":
            action = "prepare_mobile_handoff"
        elif readiness["pairing_code"]:
            action = "open_mobile_pairing"
        return {
            "ok": True,
            "mode": "runtime_supervisor_next_action",
            "recommended_next_action": action,
        }


runtime_supervisor_guidance_service = RuntimeSupervisorGuidanceService()
