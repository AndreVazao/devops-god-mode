from fastapi import APIRouter
from pydantic import BaseModel

from app.services.pro_operator_bridge_service import pro_operator_bridge_service

router = APIRouter(prefix="/api/pro-operator", tags=["pro-operator"])


class ProOperatorTextRequest(BaseModel):
    text: str
    tenant_id: str = "owner-andre"
    requested_project: str = "GOD_MODE"


class ProOperatorRunRequest(BaseModel):
    text: str
    tenant_id: str = "owner-andre"
    requested_project: str = "GOD_MODE"
    approve: bool = False


@router.get('/status')
async def status(tenant_id: str = "owner-andre"):
    return pro_operator_bridge_service.get_status(tenant_id=tenant_id)


@router.get('/panel')
async def panel(tenant_id: str = "owner-andre", requested_project: str = "GOD_MODE"):
    return pro_operator_bridge_service.build_panel(
        tenant_id=tenant_id,
        requested_project=requested_project,
    )


@router.post('/analyze')
async def analyze(payload: ProOperatorTextRequest):
    return pro_operator_bridge_service.analyze(
        text=payload.text,
        tenant_id=payload.tenant_id,
        requested_project=payload.requested_project,
    )


@router.post('/run')
async def run(payload: ProOperatorRunRequest):
    return pro_operator_bridge_service.run(
        text=payload.text,
        tenant_id=payload.tenant_id,
        requested_project=payload.requested_project,
        approve=payload.approve,
    )


@router.get('/package')
async def package(tenant_id: str = "owner-andre", requested_project: str = "GOD_MODE"):
    return pro_operator_bridge_service.get_package(
        tenant_id=tenant_id,
        requested_project=requested_project,
    )
