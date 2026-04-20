from typing import Any, Dict

from app.services.android_real_pipeline_readiness_service import (
    android_real_pipeline_readiness_service,
)
from app.services.android_runtime_shell_service import android_runtime_shell_service


class AndroidRealBuildPipelineService:
    def get_pipeline_plan(self) -> Dict[str, Any]:
        readiness = android_real_pipeline_readiness_service.get_summary()["summary"]
        shell = android_runtime_shell_service.get_shell_bundle()["shell"]
        return {
            "ok": True,
            "mode": "android_real_build_pipeline_plan",
            "pipeline": {
                "pipeline_id": "android_real_pipeline_01",
                "target_platform": "android_phone",
                "topology": "pc_and_phone_primary",
                "build_mode": "real_pipeline_foundation",
                "packaging_strategy": "android_webview_or_shell_binding",
                "output_type": "apk_foundation",
                "runtime_shell_status": shell["shell_status"],
                "replacement_status": readiness["replacement_status"],
                "readiness_status": "foundation_ready",
            },
        }

    def get_output_artifact(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "mode": "android_real_output_artifact",
            "artifact": {
                "artifact_id": "android_real_artifact_01",
                "artifact_type": "apk_foundation",
                "artifact_name": "GodModeMobileRealFoundation.apk",
                "runtime_binding": "pc_and_phone_primary",
                "pairing_support": "qr_or_code",
                "output_status": "planned",
            },
        }

    def get_replacement_summary(self) -> Dict[str, Any]:
        readiness = android_real_pipeline_readiness_service.get_summary()["summary"]
        return {
            "ok": True,
            "mode": "android_real_pipeline_replacement_summary",
            "replacement": {
                "legacy_workflow": ".github/workflows/android-mobile-build.yml",
                "new_workflow": ".github/workflows/android-real-build-pipeline-foundation.yml",
                "replacement_status": readiness["replacement_status"],
                "target_topology": readiness["target_topology"],
            },
        }


android_real_build_pipeline_service = AndroidRealBuildPipelineService()
