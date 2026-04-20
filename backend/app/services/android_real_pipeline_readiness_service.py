from typing import Any, Dict, List

from app.services.mobile_runtime_shell_service import mobile_runtime_shell_service
from app.services.pc_phone_bootstrap_service import pc_phone_bootstrap_service


class AndroidRealPipelineReadinessService:
    def _replacement_steps(self) -> List[Dict[str, Any]]:
        return [
            {
                "step_id": "android_replace_foundation_workflow",
                "phase": "pipeline_replacement",
                "step_summary": "Replace the Android foundation placeholder workflow with a real packaging pipeline aligned to PC + phone topology.",
                "required_artifacts": [
                    "real Android packaging workflow",
                    "mobile runtime shell entrypoint",
                    "pairing-aware build config",
                ],
                "step_status": "planned",
            },
            {
                "step_id": "android_bind_runtime_shell_to_real_build",
                "phase": "runtime_binding",
                "step_summary": "Bind the current mobile runtime shell and pairing assets to a real Android build output.",
                "required_artifacts": [
                    "runtime shell asset",
                    "pairing asset",
                    "Android packaging output",
                ],
                "step_status": "planned",
            },
            {
                "step_id": "android_promote_real_pipeline_to_main",
                "phase": "promotion",
                "step_summary": "Promote the new Android pipeline to replace the historical foundation workflow in the main flow.",
                "required_artifacts": [
                    "validated Android build workflow",
                    "release artifact naming",
                    "replacement migration note",
                ],
                "step_status": "planned",
            },
        ]

    def get_summary(self) -> Dict[str, Any]:
        runtime_shell = mobile_runtime_shell_service.get_runtime_shell_bundle()["runtime_shell"]
        bootstrap = pc_phone_bootstrap_service.get_bootstrap_profile()["profile"]
        blockers = self.get_blockers()["blockers"]
        next_step = self.get_next_step()["next_step"]
        return {
            "ok": True,
            "mode": "android_real_pipeline_readiness",
            "summary": {
                "readiness_id": "android_real_pipeline_readiness_01",
                "target_topology": bootstrap["runtime_mode"],
                "current_pipeline_mode": "legacy_foundation_placeholder",
                "replacement_status": "planned",
                "real_build_readiness": "partial",
                "runtime_shell_status": runtime_shell["shell_status"],
                "blockers": blockers,
                "next_step": next_step["step_id"] if next_step else None,
            },
        }

    def get_blockers(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "mode": "android_real_pipeline_blockers",
            "blockers": [
                "real Android packaging pipeline not implemented yet",
                "mobile runtime shell still represented by foundation assets",
                "foundation workflow still exists as historical coverage",
            ],
        }

    def get_steps(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "mode": "android_real_pipeline_steps",
            "steps": self._replacement_steps(),
        }

    def get_next_step(self) -> Dict[str, Any]:
        steps = self._replacement_steps()
        next_step = next((step for step in steps if step["step_status"] != "completed"), None)
        return {
            "ok": True,
            "mode": "android_real_pipeline_next_step",
            "next_step": next_step,
        }


android_real_pipeline_readiness_service = AndroidRealPipelineReadinessService()
