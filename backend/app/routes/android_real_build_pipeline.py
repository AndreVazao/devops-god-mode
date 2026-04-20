from fastapi import APIRouter

from app.services.android_real_build_pipeline_service import (
    android_real_build_pipeline_service,
)

router = APIRouter(prefix="/api/android-real-build", tags=["android-real-build"])


@router.get("/status")
async def android_real_build_status():
    pipeline = android_real_build_pipeline_service.get_pipeline_plan()["pipeline"]
    return {
        "ok": True,
        "mode": "android_real_build_status",
        "pipeline_id": pipeline["pipeline_id"],
        "readiness_status": pipeline["readiness_status"],
    }


@router.get("/pipeline")
async def android_real_build_pipeline():
    return android_real_build_pipeline_service.get_pipeline_plan()


@router.get("/artifact")
async def android_real_build_artifact():
    return android_real_build_pipeline_service.get_output_artifact()


@router.get("/replacement-summary")
async def android_real_build_replacement_summary():
    return android_real_build_pipeline_service.get_replacement_summary()
