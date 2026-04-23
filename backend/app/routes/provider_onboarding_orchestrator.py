from fastapi import APIRouter
from pydantic import BaseModel

from app.services.provider_onboarding_orchestrator_service import provider_onboarding_orchestrator_service

router = APIRouter(prefix="/api/provider-onboarding-orchestrator", tags=["provider-onboarding-orchestrator"])


class ProviderOnboardingRequest(BaseModel):
    project_name: str
    providers: list[str]
    multirepo_mode: bool = False


@router.get('/status')
async def status():
    return provider_onboarding_orchestrator_service.get_status()


@router.get('/package')
async def package():
    return provider_onboarding_orchestrator_service.get_package()


@router.post('/build')
async def build(payload: ProviderOnboardingRequest):
    return provider_onboarding_orchestrator_service.build_first_run_plan(
        project_name=payload.project_name,
        providers=payload.providers,
        multirepo_mode=payload.multirepo_mode,
    )
