from fastapi import APIRouter

from app.services.android_real_build_progressive_service import (
    android_real_build_progressive_service,
)

router = APIRouter(
    prefix="/api/android-real-build-progressive",
    tags=["android-real-build-progressive"],
)


@router.get("/status")
async def android_real_build_progressive_status():
    summary = android_real_build_progressive_service.get_summary()["summary"]
    package = android_real_build_progressive_service.get_package()["package"]
    return {
        "ok": True,
        "mode": "android_real_build_progressive_status",
        "progressive_status": summary["progressive_status"],
        "artifact_truth": summary["artifact_truth"],
        "next_stage": summary["next_stage"],
        "artifacts_count": len(package["artifacts"]),
        "workflow_role": package["workflow_role"],
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


@router.get("/package")
async def android_real_build_progressive_package():
    return android_real_build_progressive_service.get_package()


@router.get("/next-stage")
async def android_real_build_progressive_next_stage():
    return android_real_build_progressive_service.get_next_stage()
