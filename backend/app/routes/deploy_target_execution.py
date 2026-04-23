from fastapi import APIRouter
from pydantic import BaseModel

from app.services.deploy_target_execution_service import deploy_target_execution_service

router = APIRouter(prefix="/api/deploy-target-execution", tags=["deploy-target-execution"])


class DeployTargetExecutionRequest(BaseModel):
    bundle_id: str
    target_project: str
    environment_name: str
    dry_run: bool = True


@router.get('/status')
async def status():
    return deploy_target_execution_service.get_status()


@router.get('/package')
async def package():
    return deploy_target_execution_service.get_package()


@router.post('/execute')
async def execute(payload: DeployTargetExecutionRequest):
    return deploy_target_execution_service.execute_plan(
        bundle_id=payload.bundle_id,
        target_project=payload.target_project,
        environment_name=payload.environment_name,
        dry_run=payload.dry_run,
    )
