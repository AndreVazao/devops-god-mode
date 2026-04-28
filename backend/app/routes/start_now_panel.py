from fastapi import APIRouter
from pydantic import BaseModel

from app.services.start_now_panel_service import start_now_panel_service

router = APIRouter(prefix="/api/start-now", tags=["start-now-panel"])


class StartNowRequest(BaseModel):
    tenant_id: str = "owner-andre"
    requested_project: str = "GOD_MODE"


@router.get('/status')
async def status(tenant_id: str = "owner-andre"):
    return start_now_panel_service.get_status(tenant_id=tenant_id)


@router.get('/panel')
async def panel(tenant_id: str = "owner-andre", requested_project: str = "GOD_MODE"):
    return start_now_panel_service.build_panel(
        tenant_id=tenant_id,
        requested_project=requested_project,
    )


@router.post('/panel')
async def post_panel(payload: StartNowRequest):
    return start_now_panel_service.build_panel(
        tenant_id=payload.tenant_id,
        requested_project=payload.requested_project,
    )


@router.get('/package')
async def package(tenant_id: str = "owner-andre", requested_project: str = "GOD_MODE"):
    return start_now_panel_service.get_package(
        tenant_id=tenant_id,
        requested_project=requested_project,
    )
