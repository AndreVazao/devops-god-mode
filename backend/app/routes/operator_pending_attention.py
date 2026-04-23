from fastapi import APIRouter

from app.services.operator_pending_attention_service import operator_pending_attention_service

router = APIRouter(prefix="/api/operator-pending-attention", tags=["operator-pending-attention"])


@router.get('/status')
async def status():
    return operator_pending_attention_service.get_status()


@router.get('/package')
async def package():
    return operator_pending_attention_service.get_package()


@router.get('/feed')
async def feed(tenant_id: str | None = None):
    return operator_pending_attention_service.build_attention_feed(tenant_id=tenant_id)
