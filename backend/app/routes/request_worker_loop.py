from fastapi import APIRouter
from pydantic import BaseModel

from app.services.request_worker_loop_service import request_worker_loop_service

router = APIRouter(prefix="/api/request-worker", tags=["request-worker"])


class ConfigureRequest(BaseModel):
    enabled: bool | None = None
    max_jobs_per_tick: int | None = None


class TickRequest(BaseModel):
    tenant_id: str = "owner-andre"
    max_jobs: int | None = None


class RunRequest(BaseModel):
    tenant_id: str = "owner-andre"
    ticks: int = 3
    max_jobs_per_tick: int | None = None


@router.get('/status')
async def status():
    return request_worker_loop_service.get_status()


@router.get('/package')
async def package():
    return request_worker_loop_service.get_package()


@router.get('/dashboard')
async def dashboard(tenant_id: str = "owner-andre"):
    return request_worker_loop_service.build_dashboard(tenant_id=tenant_id)


@router.post('/configure')
async def configure(payload: ConfigureRequest):
    return request_worker_loop_service.configure(enabled=payload.enabled, max_jobs_per_tick=payload.max_jobs_per_tick)


@router.post('/tick')
async def tick(payload: TickRequest):
    return request_worker_loop_service.tick(tenant_id=payload.tenant_id, max_jobs=payload.max_jobs)


@router.post('/run')
async def run(payload: RunRequest):
    return request_worker_loop_service.run_for_ticks(
        tenant_id=payload.tenant_id,
        ticks=payload.ticks,
        max_jobs_per_tick=payload.max_jobs_per_tick,
    )
