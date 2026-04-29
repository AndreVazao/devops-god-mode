from typing import Optional

from fastapi import APIRouter
from pydantic import BaseModel

from app.services.approved_work_queue_runner_service import approved_work_queue_runner_service

router = APIRouter(prefix="/api/approved-work-queue", tags=["approved-work-queue"])


class BuildQueueRequest(BaseModel):
    tenant_id: str = "owner-andre"
    requested_project: Optional[str] = None


class RunSafeRequest(BaseModel):
    tenant_id: str = "owner-andre"
    queue_id: Optional[str] = None
    max_items: int = 3


@router.get('/status')
async def status():
    return approved_work_queue_runner_service.get_status()


@router.post('/status')
async def post_status():
    return approved_work_queue_runner_service.get_status()


@router.get('/build')
async def build(tenant_id: str = "owner-andre", requested_project: Optional[str] = None):
    return approved_work_queue_runner_service.build_queue(
        tenant_id=tenant_id,
        requested_project=requested_project,
    )


@router.post('/build')
async def post_build(payload: BuildQueueRequest):
    return approved_work_queue_runner_service.build_queue(
        tenant_id=payload.tenant_id,
        requested_project=payload.requested_project,
    )


@router.get('/current')
async def current():
    return approved_work_queue_runner_service.current()


@router.post('/current')
async def post_current():
    return approved_work_queue_runner_service.current()


@router.get('/gates')
async def gates(queue_id: Optional[str] = None):
    return approved_work_queue_runner_service.gates(queue_id=queue_id)


@router.post('/gates')
async def post_gates(queue_id: Optional[str] = None):
    return approved_work_queue_runner_service.gates(queue_id=queue_id)


@router.post('/run-safe')
async def run_safe(payload: RunSafeRequest):
    return approved_work_queue_runner_service.run_safe(
        tenant_id=payload.tenant_id,
        queue_id=payload.queue_id,
        max_items=payload.max_items,
    )


@router.get('/package')
async def package():
    return approved_work_queue_runner_service.get_package()


@router.post('/package')
async def post_package():
    return approved_work_queue_runner_service.get_package()
