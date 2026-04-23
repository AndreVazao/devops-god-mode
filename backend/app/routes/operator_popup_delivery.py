from fastapi import APIRouter
from pydantic import BaseModel

from app.services.operator_popup_delivery_service import operator_popup_delivery_service

router = APIRouter(prefix="/api/operator-popup-delivery", tags=["operator-popup-delivery"])


class OperatorPopupDeliveryCreateRequest(BaseModel):
    tenant_id: str
    thread_id: str
    popup_kind: str
    popup_ref_id: str
    title: str
    requires_operator_response: bool = True


class OperatorPopupDeliveryRefRequest(BaseModel):
    delivery_id: str


@router.get('/status')
async def status():
    return operator_popup_delivery_service.get_status()


@router.get('/package')
async def package():
    return operator_popup_delivery_service.get_package()


@router.get('/list')
async def list_deliveries(tenant_id: str | None = None, thread_id: str | None = None):
    return operator_popup_delivery_service.list_deliveries(tenant_id=tenant_id, thread_id=thread_id)


@router.post('/create')
async def create(payload: OperatorPopupDeliveryCreateRequest):
    return operator_popup_delivery_service.create_delivery(
        tenant_id=payload.tenant_id,
        thread_id=payload.thread_id,
        popup_kind=payload.popup_kind,
        popup_ref_id=payload.popup_ref_id,
        title=payload.title,
        requires_operator_response=payload.requires_operator_response,
    )


@router.post('/mark-delivered')
async def mark_delivered(payload: OperatorPopupDeliveryRefRequest):
    return operator_popup_delivery_service.mark_delivered(delivery_id=payload.delivery_id)


@router.post('/reissue')
async def reissue(payload: OperatorPopupDeliveryRefRequest):
    return operator_popup_delivery_service.reissue_pending_delivery(delivery_id=payload.delivery_id)


@router.post('/acknowledge-response')
async def acknowledge_response(payload: OperatorPopupDeliveryRefRequest):
    return operator_popup_delivery_service.acknowledge_response(delivery_id=payload.delivery_id)
