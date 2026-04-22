from typing import Any, Dict, List

from app.services.android_real_build_pipeline_service import (
    android_real_build_pipeline_service,
)


class AndroidRealBuildProgressiveService:
    def _stages(self) -> List[Dict[str, Any]]:
        return [
            {
                "stage_id": "android_stage_prepare_progressive_output",
                "stage_name": "prepare_progressive_output",
                "stage_order": 1,
                "stage_summary": "Prepare placeholder Android output structure and config assets.",
                "expected_outputs": [
                    "android-progressive-manifest.json",
                    "android-progressive-config.json",
                    "GodModeMobile.apk",
                ],
                "stage_status": "placeholder",
            },
            {
                "stage_id": "android_stage_bind_runtime_and_pairing",
                "stage_name": "bind_runtime_and_pairing",
                "stage_order": 2,
                "stage_summary": "Bind runtime shell and pairing support into the placeholder Android output.",
                "expected_outputs": [
                    "android-progressive-runtime.json",
                    "android-progressive-pairing.json",
                ],
                "stage_status": "placeholder",
            },
            {
                "stage_id": "android_stage_prepare_release_candidate",
                "stage_name": "prepare_release_candidate",
                "stage_order": 3,
                "stage_summary": "Prepare the Android placeholder package until the real build lands.",
                "expected_outputs": ["android-progressive-release-note.txt"],
                "stage_status": "placeholder",
            },
        ]

    def _artifacts(self) -> List[Dict[str, Any]]:
        return [
            {
                "artifact_id": "android_progressive_artifact_01",
                "artifact_name": "GodModeMobile.apk",
                "artifact_role": "placeholder_pipeline_output",
                "topology_binding": "pc_and_phone_primary",
                "artifact_status": "placeholder",
                "artifact_truth": "not_a_real_apk_yet",
            },
            {
                "artifact_id": "android_progressive_manifest_01",
                "artifact_name": "android-progressive-manifest.json",
                "artifact_role": "progressive_manifest",
                "topology_binding": "pc_and_phone_primary",
                "artifact_status": "placeholder",
                "artifact_truth": "describes_placeholder_pipeline",
            },
        ]

    def get_summary(self) -> Dict[str, Any]:
        pipeline = android_real_build_pipeline_service.get_pipeline_plan()["pipeline"]
        next_stage = self.get_next_stage()["next_stage"]
        return {
            "ok": True,
            "mode": "android_real_build_progressive_summary",
            "summary": {
                "pipeline_id": pipeline["pipeline_id"],
                "topology": pipeline["topology"],
                "build_mode": "placeholder_pipeline_progressive",
                "foundation_status": pipeline["readiness_status"],
                "progressive_status": "placeholder_only",
                "artifact_truth": "not_a_real_apk_yet",
                "next_stage": next_stage["stage_id"] if next_stage else None,
            },
        }

    def get_stages(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "mode": "android_real_build_progressive_stages",
            "stages": self._stages(),
        }

    def get_artifacts(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "mode": "android_real_build_progressive_artifacts",
            "artifacts": self._artifacts(),
        }

    def get_package(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "mode": "android_real_build_progressive_package",
            "package": {
                "summary": self.get_summary()["summary"],
                "stages": self._stages(),
                "artifacts": self._artifacts(),
                "workflow_role": "generic_placeholder_android_pipeline",
                "package_status": "placeholder_ready",
            },
        }

    def get_next_stage(self) -> Dict[str, Any]:
        stages = self._stages()
        next_stage = next(
            (stage for stage in stages if stage["stage_status"] != "completed"), None
        )
        return {
            "ok": True,
            "mode": "android_real_build_progressive_next_stage",
            "next_stage": next_stage,
        }


android_real_build_progressive_service = AndroidRealBuildProgressiveService()
