from fastapi import APIRouter
from pydantic import BaseModel

from app.services.tenant_multirepo_linkage_service import tenant_multirepo_linkage_service

router = APIRouter(prefix="/api/tenant-multirepo-linkage", tags=["tenant-multirepo-linkage"])


class TenantMultirepoLinkageRequest(BaseModel):
    tenant_id: str
    project_name: str
    frontend_runtime: str
    backend_runtime: str


@router.get('/status')
async def status():
    return tenant_multirepo_linkage_service.get_status()


@router.get('/package')
async def package():
    return tenant_multirepo_linkage_service.get_package()


@router.post('/build')
async def build(payload: TenantMultirepoLinkageRequest):
    return tenant_multirepo_linkage_service.build_linkage(
        tenant_id=payload.tenant_id,
        project_name=payload.project_name,
        frontend_runtime=payload.frontend_runtime,
        backend_runtime=payload.backend_runtime,
    )
