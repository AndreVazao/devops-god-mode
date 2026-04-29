from typing import Optional

from fastapi import APIRouter
from pydantic import BaseModel

from app.services.approved_deep_execution_plan_service import approved_deep_execution_plan_service

router = APIRouter(prefix="/api/approved-deep-execution", tags=["approved-deep-execution"])


class ApprovedExecutionRequest(BaseModel):
    tenant_id: str = "owner-andre"
    requested_project: Optional[str] = None


@router.get('/status')
async def status():
    return approved_deep_execution_plan_service.get_status()


@router.post('/status')
async def post_status():
    return approved_deep_execution_plan_service.get_status()


@router.get('/readiness')
async def readiness(tenant_id: str = "owner-andre"):
    return approved_deep_execution_plan_service.readiness(tenant_id=tenant_id)


@router.post('/readiness')
async def post_readiness(payload: ApprovedExecutionRequest):
    return approved_deep_execution_plan_service.readiness(tenant_id=payload.tenant_id)


@router.get('/plan')
async def plan(tenant_id: str = "owner-andre", requested_project: Optional[str] = None):
    return approved_deep_execution_plan_service.build_plan(
        tenant_id=tenant_id,
        requested_project=requested_project,
    )


@router.post('/plan')
async def post_plan(payload: ApprovedExecutionRequest):
    return approved_deep_execution_plan_service.build_plan(
        tenant_id=payload.tenant_id,
        requested_project=payload.requested_project,
    )


@router.post('/approval-cards')
async def approval_cards(payload: ApprovedExecutionRequest):
    return approved_deep_execution_plan_service.create_approval_cards(
        tenant_id=payload.tenant_id,
        requested_project=payload.requested_project,
    )


@router.post('/start-safe')
async def start_safe(payload: ApprovedExecutionRequest):
    return approved_deep_execution_plan_service.submit_safe_start_command(
        tenant_id=payload.tenant_id,
        requested_project=payload.requested_project,
    )


@router.get('/latest')
async def latest():
    return approved_deep_execution_plan_service.latest()


@router.post('/latest')
async def post_latest():
    return approved_deep_execution_plan_service.latest()


@router.get('/package')
async def package():
    return approved_deep_execution_plan_service.get_package()


@router.post('/package')
async def post_package():
    return approved_deep_execution_plan_service.get_package()
