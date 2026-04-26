from fastapi import APIRouter
from pydantic import BaseModel

from app.services.end_to_end_operational_drill_service import end_to_end_operational_drill_service

router = APIRouter(prefix="/api/e2e-operational-drill", tags=["e2e-operational-drill"])


class DrillRequest(BaseModel):
    tenant_id: str = "owner-andre"
    project_id: str = "GOD_MODE"
    request_text: str | None = None
    include_offline_bridge: bool = True


@router.get('/status')
async def status():
    return end_to_end_operational_drill_service.get_status()


@router.get('/package')
async def package():
    return end_to_end_operational_drill_service.get_package()


@router.get('/dashboard')
async def dashboard():
    return end_to_end_operational_drill_service.build_dashboard()


@router.get('/latest-report')
async def latest_report():
    return end_to_end_operational_drill_service.latest_report()


@router.post('/run')
async def run(payload: DrillRequest):
    return end_to_end_operational_drill_service.run_drill(
        tenant_id=payload.tenant_id,
        project_id=payload.project_id,
        request_text=payload.request_text,
        include_offline_bridge=payload.include_offline_bridge,
    )
