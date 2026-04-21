from fastapi import APIRouter, HTTPException

from app.services.final_delivery_service import final_delivery_service

router = APIRouter(
    prefix="/api/final-delivery",
    tags=["final-delivery"],
)


@router.get("/status")
async def final_delivery_status():
    deliveries = final_delivery_service.get_deliveries()["deliveries"]
    return {
        "ok": True,
        "mode": "final_delivery_status",
        "deliveries_count": len(deliveries),
        "delivery_status": "final_delivery_ready",
    }


@router.get("/deliveries")
async def final_deliveries():
    return final_delivery_service.get_deliveries()


@router.get("/actions")
async def final_delivery_actions(recovery_project_id: str | None = None):
    return final_delivery_service.get_delivery_actions(recovery_project_id)


@router.get("/package/{recovery_project_id}")
async def final_delivery_package(recovery_project_id: str):
    try:
        return final_delivery_service.get_delivery_package(recovery_project_id)
    except (ValueError, StopIteration):
        raise HTTPException(status_code=404, detail="recovery_project_not_found")


@router.get("/next-delivery-action")
async def final_delivery_next_action():
    return final_delivery_service.get_next_delivery_action()
