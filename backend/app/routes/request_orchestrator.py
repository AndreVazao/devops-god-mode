from fastapi import APIRouter
from pydantic import BaseModel

from app.services.request_orchestrator_service import request_orchestrator_service

router = APIRouter(prefix="/api/request-orchestrator", tags=["request-orchestrator"])


class SubmitRequest(BaseModel):
    request: str
    tenant_id: str = "owner-andre"
    project_id: str = "GOD_MODE"
    thread_id: str | None = None
    auto_run: bool = True


class ResumeRequest(BaseModel):
    job_id: str
    tenant_id: str = "owner-andre"
    operator_note: str = ""


@router.get('/status')
async def status():
    return request_orchestrator_service.get_status()


@router.get('/package')
async def package():
    return request_orchestrator_service.get_package()


@router.get('/dashboard')
async def dashboard(tenant_id: str = "owner-andre"):
    return request_orchestrator_service.build_dashboard(tenant_id=tenant_id)


@router.get('/jobs')
async def jobs(tenant_id: str = "owner-andre", status: str | None = None, limit: int = 100):
    return request_orchestrator_service.list_jobs(tenant_id=tenant_id, status=status, limit=limit)


@router.get('/job/{job_id}')
async def job(job_id: str, tenant_id: str = "owner-andre"):
    return request_orchestrator_service.get_job(job_id=job_id, tenant_id=tenant_id)


@router.post('/submit')
async def submit(payload: SubmitRequest):
    return request_orchestrator_service.submit_request(
        request=payload.request,
        tenant_id=payload.tenant_id,
        project_id=payload.project_id,
        thread_id=payload.thread_id,
        auto_run=payload.auto_run,
    )


@router.post('/resume')
async def resume(payload: ResumeRequest):
    return request_orchestrator_service.resume_job(
        job_id=payload.job_id,
        tenant_id=payload.tenant_id,
        operator_note=payload.operator_note,
    )


@router.post('/run/{job_id}')
async def run(job_id: str, tenant_id: str = "owner-andre"):
    return request_orchestrator_service.run_until_blocked(job_id=job_id, tenant_id=tenant_id)
