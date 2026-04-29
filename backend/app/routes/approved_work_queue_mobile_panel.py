from fastapi import APIRouter
from pydantic import BaseModel

from app.services.approved_work_queue_mobile_panel_service import approved_work_queue_mobile_panel_service

router = APIRouter(prefix="/api/approved-work-queue-mobile", tags=["approved-work-queue-mobile"])


class MobilePanelRequest(BaseModel):
    tenant_id: str = "owner-andre"


class MobileRunSafeRequest(BaseModel):
    tenant_id: str = "owner-andre"
    max_items: int = 3


@router.get('/status')
async def status():
    return approved_work_queue_mobile_panel_service.get_status()


@router.post('/status')
async def post_status():
    return approved_work_queue_mobile_panel_service.get_status()


@router.get('/panel')
async def panel(tenant_id: str = "owner-andre"):
    return approved_work_queue_mobile_panel_service.build_panel(tenant_id=tenant_id)


@router.post('/panel')
async def post_panel(payload: MobilePanelRequest):
    return approved_work_queue_mobile_panel_service.build_panel(tenant_id=payload.tenant_id)


@router.post('/run-safe')
async def run_safe(payload: MobileRunSafeRequest):
    return approved_work_queue_mobile_panel_service.run_safe_from_panel(
        tenant_id=payload.tenant_id,
        max_items=payload.max_items,
    )


@router.get('/package')
async def package():
    return approved_work_queue_mobile_panel_service.get_package()


@router.post('/package')
async def post_package():
    return approved_work_queue_mobile_panel_service.get_package()
