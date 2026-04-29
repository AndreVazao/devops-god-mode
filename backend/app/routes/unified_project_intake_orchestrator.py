from fastapi import APIRouter
from pydantic import BaseModel

from app.services.unified_project_intake_orchestrator_service import unified_project_intake_orchestrator_service

router = APIRouter(prefix="/api/unified-project-intake", tags=["unified-project-intake"])


class UnifiedProjectIntakeRequest(BaseModel):
    tenant_id: str = "owner-andre"
    requested_project: str = "GOD_MODE"


@router.get('/status')
async def status():
    return unified_project_intake_orchestrator_service.get_status()


@router.post('/status')
async def post_status():
    return unified_project_intake_orchestrator_service.get_status()


@router.get('/plan')
async def plan(tenant_id: str = "owner-andre", requested_project: str = "GOD_MODE"):
    return unified_project_intake_orchestrator_service.build_plan(
        tenant_id=tenant_id,
        requested_project=requested_project,
    )


@router.post('/plan')
async def post_plan(payload: UnifiedProjectIntakeRequest):
    return unified_project_intake_orchestrator_service.build_plan(
        tenant_id=payload.tenant_id,
        requested_project=payload.requested_project,
    )


@router.get('/run-safe')
async def run_safe(tenant_id: str = "owner-andre", requested_project: str = "GOD_MODE"):
    return unified_project_intake_orchestrator_service.run_safe(
        tenant_id=tenant_id,
        requested_project=requested_project,
    )


@router.post('/run-safe')
async def post_run_safe(payload: UnifiedProjectIntakeRequest):
    return unified_project_intake_orchestrator_service.run_safe(
        tenant_id=payload.tenant_id,
        requested_project=payload.requested_project,
    )


@router.get('/package')
async def package():
    return unified_project_intake_orchestrator_service.get_package()


@router.post('/package')
async def post_package():
    return unified_project_intake_orchestrator_service.get_package()
