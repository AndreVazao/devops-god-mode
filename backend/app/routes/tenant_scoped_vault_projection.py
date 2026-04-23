from fastapi import APIRouter
from pydantic import BaseModel

from app.services.tenant_scoped_vault_projection_service import tenant_scoped_vault_projection_service

router = APIRouter(prefix="/api/tenant-scoped-vault-projection", tags=["tenant-scoped-vault-projection"])


class TenantScopedVaultProjectionRequest(BaseModel):
    tenant_id: str


@router.get('/status')
async def status():
    return tenant_scoped_vault_projection_service.get_status()


@router.get('/package')
async def package():
    return tenant_scoped_vault_projection_service.get_package()


@router.post('/build')
async def build(payload: TenantScopedVaultProjectionRequest):
    return tenant_scoped_vault_projection_service.build_projection(tenant_id=payload.tenant_id)
