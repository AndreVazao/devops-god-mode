from fastapi import APIRouter

from app.services.android_progressive_runtime_binding_service import (
    android_progressive_runtime_binding_service,
)

router = APIRouter(prefix="/api/android-progressive-binding", tags=["android-progressive-binding"])


@router.get("/status")
async def android_progressive_binding_status():
    summary = android_progressive_runtime_binding_service.get_summary()["summary"]
    return {
        "ok": True,
        "mode": "android_progressive_binding_status",
        "binding_status": summary["binding_status"],
        "next_stage": summary["next_stage"],
    }


@router.get("/summary")
async def android_progressive_binding_summary():
    return android_progressive_runtime_binding_service.get_summary()


@router.get("/assets")
async def android_progressive_binding_assets():
    return android_progressive_runtime_binding_service.get_assets()


@router.get("/next-step")
async def android_progressive_binding_next_step():
    return android_progressive_runtime_binding_service.get_next_step()
