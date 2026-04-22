from typing import Any, Dict

from app.services.continuous_remote_execution_service import (
    continuous_remote_execution_service,
)
from app.services.desktop_mobile_handoff_service import desktop_mobile_handoff_service
from app.services.local_pc_runtime_orchestrator_service import (
    local_pc_runtime_orchestrator_service,
)
from app.services.offline_command_buffering_service import (
    offline_command_buffering_service,
)
from app.services.remote_session_persistence_service import (
    remote_session_persistence_service,
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

    def _autonomy_snapshot(self) -> Dict[str, Any]:
        buffer_package = offline_command_buffering_service.get_buffer_package()["package"]
        session_package = remote_session_persistence_service.get_session_package()["package"]
        execution_package = continuous_remote_execution_service.get_execution_package()["package"]
        return {
            "connectivity": buffer_package["connectivity"],
            "buffer_counts": {
                "total_commands": len(buffer_package["commands"]),
                "phone_buffered": session_package["counts"]["phone_buffered"],
                "pc_ready": session_package["counts"]["pc_ready"],
                "pc_active": session_package["counts"]["pc_active"],
                "completed": session_package["counts"]["completed"],
            },
            "execution_counts": execution_package["counts"],
        }

    def get_summary(self) -> Dict[str, Any]:
        runtime = local_pc_runtime_orchestrator_service.get_runtime_state()["runtime"]
        handoff = desktop_mobile_handoff_service.get_handoff_package()["handoff"]
        readiness = self.get_readiness()["readiness"]
        autonomy = self._autonomy_snapshot()
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
                "link_mode": autonomy["connectivity"]["link_mode"],
                "buffer_counts": autonomy["buffer_counts"],
                "execution_counts": autonomy["execution_counts"],
            },
        }

    def get_readiness(self) -> Dict[str, Any]:
        runtime = local_pc_runtime_orchestrator_service.get_runtime_state()["runtime"]
        handoff = local_pc_runtime_orchestrator_service.get_mobile_handoff_state()["mobile_handoff_state"]
        autonomy = self._autonomy_snapshot()
        return {
            "ok": True,
            "mode": "runtime_supervisor_readiness",
            "readiness": {
                "backend_runtime": runtime["backend_runtime"]["status"],
                "shell_runtime": runtime["shell_runtime"]["status"],
                "desktop_bundle": runtime["desktop_bundle"]["bundle_status"],
                "mobile_handoff": "ready" if handoff["pairing_asset"] else "not_ready",
                "pairing_code": handoff["pairing_code"],
                "link_mode": autonomy["connectivity"]["link_mode"],
                "phone_buffered": autonomy["buffer_counts"]["phone_buffered"],
                "pc_ready": autonomy["buffer_counts"]["pc_ready"],
                "pc_active": autonomy["buffer_counts"]["pc_active"],
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
        elif readiness["phone_buffered"] > 0 and readiness["link_mode"] in {"both_online", "pc_only"}:
            action = "sync_phone_buffer_to_pc"
        elif readiness["pc_active"] > 0:
            action = "monitor_pc_autonomy"
        elif readiness["pc_ready"] > 0:
            action = "continue_pc_execution_queue"
        elif readiness["pairing_code"]:
            action = "open_mobile_pairing"
        return {
            "ok": True,
            "mode": "runtime_supervisor_next_action",
            "recommended_next_action": action,
        }


runtime_supervisor_guidance_service = RuntimeSupervisorGuidanceService()
