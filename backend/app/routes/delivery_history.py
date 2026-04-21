from fastapi import APIRouter, HTTPException

from app.services.delivery_history_service import delivery_history_service

router = APIRouter(
    prefix="/api/delivery-history",
    tags=["delivery-history"],
)


@router.get("/status")
async def delivery_history_status():
    histories = delivery_history_service.get_histories()["histories"]
    return {
        "ok": True,
        "mode": "delivery_history_status",
        "histories_count": len(histories),
        "history_status": "delivery_history_ready",
    }


@router.get("/histories")
async def delivery_histories():
    return delivery_history_service.get_histories()


@router.get("/records")
async def delivery_history_records(recovery_project_id: str | None = None):
    return delivery_history_service.get_history_records(recovery_project_id)


@router.get("/package/{recovery_project_id}")
async def delivery_history_package(recovery_project_id: str):
    try:
        return delivery_history_service.get_history_package(recovery_project_id)
    except (ValueError, StopIteration):
        raise HTTPException(status_code=404, detail="recovery_project_not_found")


@router.get("/next-history-action")
async def delivery_history_next_action():
    return delivery_history_service.get_next_history_action()
