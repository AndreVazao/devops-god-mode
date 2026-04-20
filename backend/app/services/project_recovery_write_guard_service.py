from typing import Any, Dict, List

from app.services.project_recovery_write_dispatch_service import (
    project_recovery_write_dispatch_service,
)


class ProjectRecoveryWriteGuardService:
    def get_guards(self) -> Dict[str, Any]:
        dispatches = project_recovery_write_dispatch_service.get_dispatches()["dispatches"]
        guards: List[Dict[str, Any]] = []
        for dispatch in dispatches:
            guards.append(
                {
                    "recovery_write_guard_id": f"guard_{dispatch['recovery_write_dispatch_id']}",
                    "recovery_project_id": dispatch["recovery_project_id"],
                    "recovery_write_dispatch_id": dispatch["recovery_write_dispatch_id"],
                    "finding_count": dispatch["dispatch_target_count"],
                    "guard_status": "planned",
                }
            )
        return {"ok": True, "mode": "recovery_write_guards", "guards": guards}

    def get_findings(self, recovery_project_id: str | None = None) -> Dict[str, Any]:
        dispatch_targets = project_recovery_write_dispatch_service.get_dispatch_targets(recovery_project_id)["targets"]
        findings: List[Dict[str, Any]] = []
        finding_types = [
            ("indentation_or_syntax_risk", "medium"),
            ("payload_structure_check", "medium"),
            ("target_path_consistency_check", "low"),
        ]
        for index, target in enumerate(dispatch_targets):
            finding_type, severity = finding_types[index % len(finding_types)]
            findings.append(
                {
                    "recovery_write_guard_finding_id": f"guard_{target['recovery_write_dispatch_target_id']}",
                    "recovery_project_id": target["recovery_project_id"],
                    "recovery_write_dispatch_target_id": target["recovery_write_dispatch_target_id"],
                    "finding_type": finding_type,
                    "severity": severity,
                    "finding_status": "planned",
                }
            )
        return {"ok": True, "mode": "recovery_write_guard_findings", "findings": findings}

    def get_guard_package(self, recovery_project_id: str) -> Dict[str, Any]:
        guard = next(
            item for item in self.get_guards()["guards"] if item["recovery_project_id"] == recovery_project_id
        )
        package = {
            "guard": guard,
            "findings": self.get_findings(recovery_project_id)["findings"],
            "guard_mode": "pre_real_local_write_guard",
            "package_status": "planned",
        }
        return {"ok": True, "mode": "project_recovery_write_guard_package", "package": package}

    def get_next_guard_action(self) -> Dict[str, Any]:
        guards = self.get_guards()["guards"]
        next_guard = guards[0] if guards else None
        return {
            "ok": True,
            "mode": "next_project_recovery_write_guard_action",
            "next_guard_action": {
                "recovery_write_guard_id": next_guard["recovery_write_guard_id"],
                "recovery_project_id": next_guard["recovery_project_id"],
                "action": "classify_and_prepare_safe_real_local_write_request",
                "guard_status": "planned",
            }
            if next_guard
            else None,
        }


project_recovery_write_guard_service = ProjectRecoveryWriteGuardService()
