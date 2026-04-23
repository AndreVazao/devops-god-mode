from fastapi import APIRouter
from pydantic import BaseModel

from app.services.provider_deploy_execution_service import provider_deploy_execution_service

router = APIRouter(prefix="/api/provider-deploy-execution", tags=["provider-deploy-execution"])


class ProviderDeployExecutionRequest(BaseModel):
    bundle_id: str
    target_project: str
    environment_name: str
    provider_name: str
    dry_run: bool = True


@router.get('/status')
async def status():
    return provider_deploy_execution_service.get_status()


@router.get('/package')
async def package():
    return provider_deploy_execution_service.get_package()


@router.post('/execute')
async def execute(payload: ProviderDeployExecutionRequest):
    return provider_deploy_execution_service.execute_provider_plan(
        bundle_id=payload.bundle_id,
        target_project=payload.target_project,
        environment_name=payload.environment_name,
        provider_name=payload.provider_name,
        dry_run=payload.dry_run,
    )
