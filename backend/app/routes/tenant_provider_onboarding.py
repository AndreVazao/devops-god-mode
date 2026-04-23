from fastapi import APIRouter
from pydantic import BaseModel

from app.services.tenant_provider_onboarding_service import tenant_provider_onboarding_service

router = APIRouter(prefix="/api/tenant-provider-onboarding", tags=["tenant-provider-onboarding"])


class TenantProviderOnboardingRequest(BaseModel):
    tenant_id: str
    project_name: str
    providers: list[str]
    multirepo_mode: bool = False


class TenantProviderSessionMaterializeRequest(BaseModel):
    tenant_id: str
    provider_name: str
    account_label: str
    notes: str = ""


@router.get('/status')
async def status():
    return tenant_provider_onboarding_service.get_status()


@router.get('/package')
async def package():
    return tenant_provider_onboarding_service.get_package()


@router.post('/build')
async def build(payload: TenantProviderOnboardingRequest):
    return tenant_provider_onboarding_service.build_plan(
        tenant_id=payload.tenant_id,
        project_name=payload.project_name,
        providers=payload.providers,
        multirepo_mode=payload.multirepo_mode,
    )


@router.post('/materialize-session-preview')
async def materialize_session_preview(payload: TenantProviderSessionMaterializeRequest):
    return tenant_provider_onboarding_service.materialize_session_preview(
        tenant_id=payload.tenant_id,
        provider_name=payload.provider_name,
        account_label=payload.account_label,
        notes=payload.notes,
    )
