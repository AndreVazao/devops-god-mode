from fastapi import APIRouter

from app.services.first_run_bundle_service import first_run_bundle_service

router = APIRouter(prefix="/api/first-run-bundle", tags=["first-run-bundle"])


@router.get("/status")
async def first_run_bundle_status():
    bundle = first_run_bundle_service.get_bundle()
    return {
        "ok": True,
        "mode": bundle["mode"],
        "bundle_id": bundle["bundle"]["bundle_id"],
        "final_status": bundle["bundle"]["final_status"],
    }


@router.get("/bundle")
async def first_run_bundle_full():
    return first_run_bundle_service.get_bundle()


@router.get("/pairing-asset")
async def first_run_pairing_asset():
    return first_run_bundle_service.get_pairing_asset()
