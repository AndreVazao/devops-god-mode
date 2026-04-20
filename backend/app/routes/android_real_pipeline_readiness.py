from fastapi import APIRouter

from app.services.android_real_pipeline_readiness_service import (
    android_real_pipeline_readiness_service,
)

router = APIRouter(prefix="/api/android-real-pipeline", tags=["android-real-pipeline"])


@router.get("/status")
async def android_real_pipeline_status():
    summary = android_real_pipeline_readiness_service.get_summary()["summary"]
    return {
        "ok": True,
        "mode": "android_real_pipeline_status",
        "replacement_status": summary["replacement_status"],
        "real_build_readiness": summary["real_build_readiness"],
    }


@router.get("/summary")
async def android_real_pipeline_summary():
    return android_real_pipeline_readiness_service.get_summary()


@router.get("/blockers")
async def android_real_pipeline_blockers():
    return android_real_pipeline_readiness_service.get_blockers()


@router.get("/steps")
async def android_real_pipeline_steps():
    return android_real_pipeline_readiness_service.get_steps()


@router.get("/next-step")
async def android_real_pipeline_next_step():
    return android_real_pipeline_readiness_service.get_next_step()
