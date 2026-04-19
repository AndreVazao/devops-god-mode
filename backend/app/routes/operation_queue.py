from fastapi import APIRouter

from app.services.operation_queue_service import operation_queue_service

router = APIRouter(prefix="/api/operation-queue", tags=["operation-queue"])


@router.get("/status")
async def operation_queue_status():
    next_intent = operation_queue_service.get_next_intent()["next_intent"]
    return {
        "ok": True,
        "mode": "operation_queue_status",
        "next_intent_id": next_intent["intent_id"] if next_intent else None,
        "queue_status": "operation_queue_ready",
    }


@router.get("/queue")
async def operation_queue_full():
    return operation_queue_service.get_queue()


@router.get("/next-intent")
async def operation_queue_next_intent():
    return operation_queue_service.get_next_intent()


@router.get("/preview")
async def operation_queue_preview():
    return operation_queue_service.get_preview()
