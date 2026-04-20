from typing import Any, Dict, List

from app.services.project_recovery_execution_service import (
    project_recovery_execution_service,
)
from app.services.project_recovery_local_apply_service import (
    project_recovery_local_apply_service,
)
from app.services.project_recovery_real_write_link_service import (
    project_recovery_real_write_link_service,
)
from app.services.project_recovery_write_guard_service import (
    project_recovery_write_guard_service,
)


class ProjectRecoveryWriteMaterializeService:
    def _risk_from_findings(self, findings: List[Dict[str, Any]]) -> str:
        severities = {item.get("severity", "low") for item in findings}
        if "high" in severities:
            return "high"
        if "medium" in severities:
            return "medium"
        return "low"

    def get_materialize_bridges(self) -> Dict[str, Any]:
        handoffs = project_recovery_real_write_link_service.get_handoffs()["handoffs"]
        bridges: List[Dict[str, Any]] = []
        for handoff in handoffs:
            bridges.append(
                {
                    "recovery_write_materialize_id": f"materialize_{handoff['recovery_project_id']}",
                    "recovery_project_id": handoff["recovery_project_id"],
                    "handoff_id": handoff["handoff_id"],
                    "materialize_target_count": handoff["write_run_candidate_count"],
                    "executor_stack": [
                        "local_code_patch",
                        "patch_apply_preview",
                        "local_file_apply_runtime",
                        "real_local_write",
                    ],
                    "bridge_status": "executor_ready_planned",
                }
            )
        return {"ok": True, "mode": "recovery_write_materialize_bridges", "bridges": bridges}

    def get_materialize_targets(self, recovery_project_id: str | None = None) -> Dict[str, Any]:
        local_targets = project_recovery_local_apply_service.get_local_targets(recovery_project_id)["targets"]
        execution_targets = project_recovery_execution_service.get_target_files(recovery_project_id)["target_files"]
        execution_index = {
            item["recovery_project_id"] + "::" + item["target_path"]: item for item in execution_targets
        }
        findings = project_recovery_write_guard_service.get_findings(recovery_project_id)["findings"]
        findings_by_project: Dict[str, List[Dict[str, Any]]] = {}
        for finding in findings:
            findings_by_project.setdefault(finding["recovery_project_id"], []).append(finding)

        targets: List[Dict[str, Any]] = []
        for target in local_targets:
            root, _, relative_path = target["local_target_path"].rpartition("/")
            if not relative_path:
                root = target["local_target_path"]
                relative_path = ""
            risk_level = self._risk_from_findings(findings_by_project.get(target["recovery_project_id"], []))
            execution_target = execution_index.get(
                target["recovery_project_id"] + "::" + relative_path,
                {},
            )
            targets.append(
                {
                    "recovery_write_materialize_target_id": f"materialize_{target['local_target_id']}",
                    "recovery_project_id": target["recovery_project_id"],
                    "local_repo_path": root,
                    "local_target_file": relative_path,
                    "source_target_file_id": target["source_target_file_id"],
                    "patch_strategy": target["content_strategy"],
                    "risk_level": risk_level,
                    "file_role": execution_target.get("file_role", target["local_role"]),
                    "target_status": "materialize_ready",
                }
            )
        return {"ok": True, "mode": "recovery_write_materialize_targets", "targets": targets}

    def get_materialize_package(self, recovery_project_id: str) -> Dict[str, Any]:
        bridge = next(
            item
            for item in self.get_materialize_bridges()["bridges"]
            if item["recovery_project_id"] == recovery_project_id
        )
        targets = self.get_materialize_targets(recovery_project_id)["targets"]
        findings = project_recovery_write_guard_service.get_findings(recovery_project_id)["findings"]
        patch_requests = []
        preview_requests = []
        apply_run_requests = []
        real_write_requests = []
        for target in targets:
            patch_id = f"patch_request_{target['recovery_write_materialize_target_id']}"
            preview_id = f"preview_request_{target['recovery_write_materialize_target_id']}"
            apply_run_id = f"apply_request_{target['recovery_write_materialize_target_id']}"
            patch_requests.append(
                {
                    "patch_id": patch_id,
                    "repo_full_name": f"recovered/{recovery_project_id}",
                    "target_path": target["local_target_file"],
                    "instruction": f"Materialize recovered content into {target['local_target_file']}",
                    "patch_strategy": target["patch_strategy"],
                    "risk_level": target["risk_level"],
                    "validation_plan": [
                        "create preview from recovered payload",
                        "apply locally with backup",
                        "write through real_local_write after validation",
                    ],
                }
            )
            preview_requests.append(
                {
                    "preview_id": preview_id,
                    "patch_id": patch_id,
                    "apply_mode": "recovery_materialize_preview",
                }
            )
            apply_run_requests.append(
                {
                    "apply_run_id": apply_run_id,
                    "patch_id": patch_id,
                    "preview_id": preview_id,
                    "local_repo_path": target["local_repo_path"],
                    "local_target_file": target["local_target_file"],
                    "execution_mode": "recovery_materialize_apply",
                    "expected_final_status": "applied_locally_pending_validation",
                }
            )
            real_write_requests.append(
                {
                    "apply_run_id": apply_run_id,
                    "write_mode": "real_local_write",
                }
            )
        package = {
            "bridge": bridge,
            "targets": targets,
            "guard_findings": findings,
            "executor_package": {
                "patch_requests": patch_requests,
                "preview_requests": preview_requests,
                "apply_run_requests": apply_run_requests,
                "real_write_requests": real_write_requests,
            },
            "executor_compatibility": {
                "local_code_patch": bool(patch_requests),
                "patch_apply_preview": bool(preview_requests),
                "local_file_apply_runtime": bool(apply_run_requests),
                "real_local_write": bool(real_write_requests),
            },
            "package_status": "executor_ready_planned",
        }
        return {"ok": True, "mode": "project_recovery_write_materialize_package", "package": package}

    def get_next_materialize_action(self) -> Dict[str, Any]:
        bridges = self.get_materialize_bridges()["bridges"]
        next_bridge = bridges[0] if bridges else None
        return {
            "ok": True,
            "mode": "next_project_recovery_write_materialize_action",
            "next_materialize_action": {
                "recovery_write_materialize_id": next_bridge["recovery_write_materialize_id"],
                "recovery_project_id": next_bridge["recovery_project_id"],
                "action": "materialize_executor_requests_for_local_apply_and_real_write",
                "bridge_status": "executor_ready_planned",
            }
            if next_bridge
            else None,
        }


project_recovery_write_materialize_service = ProjectRecoveryWriteMaterializeService()
