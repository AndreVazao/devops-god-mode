from fastapi import APIRouter

from app.services.android_runtime_shell_service import android_runtime_shell_service

router = APIRouter(prefix="/api/mobile-runtime-shell", tags=["mobile-runtime-shell"])


@router.get("/status")
async def mobile_runtime_shell_status():
    shell = android_runtime_shell_service.get_shell_bundle()["shell"]
    return {
        "ok": True,
        "mode": "mobile_runtime_shell_status",
        "shell_id": shell["shell_id"],
        "shell_status": shell["shell_status"],
    }


@router.get("/bundle")
async def mobile_runtime_shell_bundle():
    return android_runtime_shell_service.get_shell_bundle()


@router.get("/pairing-hint")
async def mobile_runtime_shell_pairing_hint():
    return android_runtime_shell_service.get_pairing_hint()
