from fastapi import APIRouter
from pydantic import BaseModel

from app.services.provider_session_partition_service import provider_session_partition_service

router = APIRouter(prefix="/api/provider-session-partition", tags=["provider-session-partition"])


class ProviderSessionPartitionRequest(BaseModel):
    tenant_id: str
    provider_name: str
    account_label: str
    session_scope: str
    access_mode: str
    notes: str = ""


@router.get('/status')
async def status():
    return provider_session_partition_service.get_status()


@router.get('/package')
async def package():
    return provider_session_partition_service.get_package()


@router.get('/list')
async def list_sessions(tenant_id: str | None = None):
    return provider_session_partition_service.list_sessions(tenant_id=tenant_id)


@router.post('/upsert')
async def upsert(payload: ProviderSessionPartitionRequest):
    return provider_session_partition_service.upsert_session(
        tenant_id=payload.tenant_id,
        provider_name=payload.provider_name,
        account_label=payload.account_label,
        session_scope=payload.session_scope,
        access_mode=payload.access_mode,
        notes=payload.notes,
    )
