from fastapi import APIRouter
from pydantic import BaseModel

from app.services.tenant_browser_onboarding_executor_service import tenant_browser_onboarding_executor_service

router = APIRouter(prefix="/api/tenant-browser-onboarding-executor", tags=["tenant-browser-onboarding-executor"])


class TenantBrowserOnboardingExecutorRequest(BaseModel):
    tenant_id: str
    project_name: str
    provider_name: str
    account_label: str
    multirepo_mode: bool = False


@router.get('/status')
async def status():
    return tenant_browser_onboarding_executor_service.get_status()


@router.get('/package')
async def package():
    return tenant_browser_onboarding_executor_service.get_package()


@router.post('/execute-first-run-capture')
async def execute_first_run_capture(payload: TenantBrowserOnboardingExecutorRequest):
    return tenant_browser_onboarding_executor_service.execute_first_run_capture(
        tenant_id=payload.tenant_id,
        project_name=payload.project_name,
        provider_name=payload.provider_name,
        account_label=payload.account_label,
        multirepo_mode=payload.multirepo_mode,
    )
