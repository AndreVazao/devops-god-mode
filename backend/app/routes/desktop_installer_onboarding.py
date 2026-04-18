from fastapi import APIRouter

from app.services.desktop_installer_onboarding_service import (
    desktop_installer_onboarding_service,
)

router = APIRouter(prefix="/api/desktop-installer", tags=["desktop-installer"])


@router.get("/status")
async def desktop_installer_status():
    manifest = desktop_installer_onboarding_service.get_installer_manifest()["manifest"]
    return {
        "ok": True,
        "mode": "desktop_installer_status",
        "installer_id": manifest["installer_id"],
        "installer_status": manifest["installer_status"],
    }


@router.get("/manifest")
async def desktop_installer_manifest():
    return desktop_installer_onboarding_service.get_installer_manifest()


@router.get("/onboarding")
async def desktop_installer_onboarding():
    return desktop_installer_onboarding_service.get_onboarding_bundle()
