from fastapi import APIRouter
from pydantic import BaseModel

from app.services.provider_real_execution_guard_service import provider_real_execution_guard_service

router = APIRouter(prefix="/api/provider-real-execution-guard", tags=["provider-real-execution-guard"])


class ProviderRealExecutionGuardRequest(BaseModel):
    provider_name: str
    target_project: str
    environment_name: str


@router.get('/status')
async def status():
    return provider_real_execution_guard_service.get_status()


@router.get('/package')
async def package():
    return provider_real_execution_guard_service.get_package()


@router.post('/build')
async def build(payload: ProviderRealExecutionGuardRequest):
    return provider_real_execution_guard_service.build_guard(
        provider_name=payload.provider_name,
        target_project=payload.target_project,
        environment_name=payload.environment_name,
    )
