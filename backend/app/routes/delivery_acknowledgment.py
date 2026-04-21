from fastapi import APIRouter, HTTPException

from app.services.delivery_acknowledgment_service import delivery_acknowledgment_service

router = APIRouter(
    prefix="/api/delivery-acknowledgment",
    tags=["delivery-acknowledgment"],
)


@router.get("/status")
async def delivery_acknowledgment_status():
    acknowledgments = delivery_acknowledgment_service.get_acknowledgments()["acknowledgments"]
    return {
        "ok": True,
        "mode": "delivery_acknowledgment_status",
        "acknowledgments_count": len(acknowledgments),
        "acknowledgment_status": "delivery_acknowledgment_ready",
    }


@router.get("/acknowledgments")
async def delivery_acknowledgments():
    return delivery_acknowledgment_service.get_acknowledgments()


@router.get("/events")
async def delivery_ack_events(recovery_project_id: str | None = None):
    return delivery_acknowledgment_service.get_ack_events(recovery_project_id)


@router.get("/package/{recovery_project_id}")
async def delivery_ack_package(recovery_project_id: str):
    try:
        return delivery_acknowledgment_service.get_ack_package(recovery_project_id)
    except (ValueError, StopIteration):
        raise HTTPException(status_code=404, detail="recovery_project_not_found")


@router.get("/next-ack-action")
async def delivery_ack_next_action():
    return delivery_acknowledgment_service.get_next_ack_action()
