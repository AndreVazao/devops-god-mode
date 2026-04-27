from fastapi import APIRouter
from pydantic import BaseModel

from app.services.real_operator_rehearsal_service import real_operator_rehearsal_service

router = APIRouter(prefix="/api/real-operator-rehearsal", tags=["real-operator-rehearsal"])


class RealOperatorRehearsalRequest(BaseModel):
    tenant_id: str = "owner-andre"
    requested_project: str = "GOD_MODE"


@router.get('/status')
async def status():
    return real_operator_rehearsal_service.get_status()


@router.get('/package')
async def package():
    return real_operator_rehearsal_service.get_package()


@router.post('/run')
async def run(payload: RealOperatorRehearsalRequest):
    return real_operator_rehearsal_service.run(
        tenant_id=payload.tenant_id,
        requested_project=payload.requested_project,
    )
