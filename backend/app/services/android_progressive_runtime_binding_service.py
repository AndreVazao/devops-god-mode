from typing import Any, Dict

from app.services.android_real_build_progressive_service import (
    android_real_build_progressive_service,
)
from app.services.android_runtime_shell_service import android_runtime_shell_service


class AndroidProgressiveRuntimeBindingService:
    def get_summary(self) -> Dict[str, Any]:
        shell = android_runtime_shell_service.get_shell_bundle()["shell"]
        next_stage = android_real_build_progressive_service.get_next_stage()["next_stage"]
        return {
            "ok": True,
            "mode": "android_progressive_runtime_binding_summary",
            "summary": {
                "binding_id": "android_progressive_binding_01",
                "runtime_mode": shell["runtime_mode"],
                "shell_status": shell["shell_status"],
                "pairing_mode": shell["pairing_payload"]["pairing_mode"],
                "binding_status": "planned",
                "output_target": "GodModeMobileProgressive.apk",
                "next_stage": next_stage["stage_id"] if next_stage else None,
            },
        }

    def get_assets(self) -> Dict[str, Any]:
        shell = android_runtime_shell_service.get_shell_bundle()["shell"]
        return {
            "ok": True,
            "mode": "android_progressive_runtime_binding_assets",
            "assets": [
                {
                    "asset_id": "android_progressive_runtime_01",
                    "asset_name": "android-progressive-runtime.json",
                    "asset_role": "runtime_binding",
                    "topology_binding": shell["runtime_mode"],
                    "asset_status": "planned",
                },
                {
                    "asset_id": "android_progressive_pairing_01",
                    "asset_name": "android-progressive-pairing.json",
                    "asset_role": "pairing_binding",
                    "topology_binding": shell["runtime_mode"],
                    "asset_status": "planned",
                },
            ],
        }

    def get_next_step(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "mode": "android_progressive_runtime_binding_next_step",
            "next_step": {
                "step_id": "android_bind_progressive_runtime_and_pairing",
                "step_summary": "Bind runtime shell and pairing assets directly into the progressive Android output bundle.",
                "step_status": "planned",
            },
        }


android_progressive_runtime_binding_service = AndroidProgressiveRuntimeBindingService()
