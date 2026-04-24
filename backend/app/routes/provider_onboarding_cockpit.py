from fastapi import APIRouter
from pydantic import BaseModel

from app.services.provider_onboarding_cockpit_service import provider_onboarding_cockpit_service

router = APIRouter(prefix="/api/provider-onboarding-cockpit", tags=["provider-onboarding-cockpit"])


class ProviderOnboardingCockpitRequest(BaseModel):
    tenant_id: str = "owner-andre"
    project_name: str = "godmode-project"
    providers: list[str] = ["github", "vercel", "supabase", "render"]
    multirepo_mode: bool = True


@router.get('/status')
async def status():
    return provider_onboarding_cockpit_service.get_status()


@router.get('/package')
async def package():
    return provider_onboarding_cockpit_service.get_package()


@router.get('/dashboard')
async def dashboard(
    tenant_id: str = 'owner-andre',
    project_name: str = 'godmode-project',
    providers: str = 'github,vercel,supabase,render',
    multirepo_mode: bool = True,
):
    provider_list = [item.strip() for item in providers.split(',') if item.strip()]
    return provider_onboarding_cockpit_service.build_dashboard(
        tenant_id=tenant_id,
        project_name=project_name,
        providers=provider_list,
        multirepo_mode=multirepo_mode,
    )


@router.post('/dashboard')
async def dashboard_post(payload: ProviderOnboardingCockpitRequest):
    return provider_onboarding_cockpit_service.build_dashboard(
        tenant_id=payload.tenant_id,
        project_name=payload.project_name,
        providers=payload.providers,
        multirepo_mode=payload.multirepo_mode,
    )
