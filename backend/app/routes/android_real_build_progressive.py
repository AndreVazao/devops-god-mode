from fastapi import APIRouter

from app.services.android_real_build_progressive_service import (
    android_real_build_progressive_service,
)

router = APIRouter(prefix="/api/android-real-build-progressive", tags=["android-real-build-progressive"])


@router.get("/status")
async def android_real_build_progressive_status():
    summary = android_real_build_progressive_service.get_summary()["summary"]
    return {
        "ok": True,
        "mode": "android_real_build_progressive_status",
        "progressive_status": summary["progressive_status"],
        "next_stage": summary["next_stage"],
    }


@router.get("/summary")
async def android_real_build_progressive_summary():
    return android_real_build_progressive_service.get_summary()


@router.get("/stages")
async def android_real_build_progressive_stages():
    return android_real_build_progressive_service.get_stages()


@router.get("/artifacts")
async def android_real_build_progressive_artifacts():
    return android_real_build_progressive_service.get_artifacts()


@router.get("/next-stage")
async def android_real_build_progressive_next_stage():
    return android_real_build_progressive_service.get_next_stage()
