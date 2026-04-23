from fastapi import APIRouter
from pydantic import BaseModel

from app.services.tenant_partition_service import tenant_partition_service

router = APIRouter(prefix="/api/tenant-partition", tags=["tenant-partition"])


class TenantPartitionRequest(BaseModel):
    tenant_id: str
    owner_type: str
    display_name: str
    repo_scope_mode: str
    provider_scope_mode: str
    vault_namespace: str
    notes: str = ""


class TenantPartitionPlanRequest(BaseModel):
    tenant_id: str
    project_name: str
    multirepo_mode: bool = False


@router.get('/status')
async def status():
    return tenant_partition_service.get_status()


@router.get('/package')
async def package():
    return tenant_partition_service.get_package()


@router.get('/list')
async def list_tenants():
    return tenant_partition_service.list_tenants()


@router.post('/upsert')
async def upsert(payload: TenantPartitionRequest):
    return tenant_partition_service.upsert_tenant(
        tenant_id=payload.tenant_id,
        owner_type=payload.owner_type,
        display_name=payload.display_name,
        repo_scope_mode=payload.repo_scope_mode,
        provider_scope_mode=payload.provider_scope_mode,
        vault_namespace=payload.vault_namespace,
        notes=payload.notes,
    )


@router.post('/plan')
async def plan(payload: TenantPartitionPlanRequest):
    return tenant_partition_service.build_partition_plan(
        tenant_id=payload.tenant_id,
        project_name=payload.project_name,
        multirepo_mode=payload.multirepo_mode,
    )
