from fastapi import APIRouter

from app.services.desktop_mobile_handoff_service import desktop_mobile_handoff_service

router = APIRouter(prefix="/api/desktop-mobile-handoff", tags=["desktop-mobile-handoff"])


@router.get("/status")
async def desktop_mobile_handoff_status():
    handoff = desktop_mobile_handoff_service.get_handoff_package()["handoff"]
    return {
        "ok": True,
        "mode": "desktop_mobile_handoff_status",
        "handoff_id": handoff["handoff_id"],
        "handoff_status": handoff["handoff_status"],
    }


@router.get("/package")
async def desktop_mobile_handoff_package():
    return desktop_mobile_handoff_service.get_handoff_package()


@router.get("/install-sequence")
async def desktop_mobile_install_sequence():
    return desktop_mobile_handoff_service.get_install_sequence()


@router.get("/pairing-summary")
async def desktop_mobile_pairing_summary():
    return desktop_mobile_handoff_service.get_pairing_summary()
