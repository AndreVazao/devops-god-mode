from fastapi import APIRouter
from pydantic import BaseModel

from app.services.deploy_execution_plan_service import deploy_execution_plan_service

router = APIRouter(prefix="/api/deploy-execution-plan", tags=["deploy-execution-plan"])


class DeployExecutionPlanRequest(BaseModel):
    bundle_id: str
    target_project: str
    environment_name: str


@router.get('/status')
async def status():
    return deploy_execution_plan_service.get_status()


@router.get('/package')
async def package():
    return deploy_execution_plan_service.get_package()


@router.post('/build')
async def build(payload: DeployExecutionPlanRequest):
    return deploy_execution_plan_service.build_plan(
        bundle_id=payload.bundle_id,
        target_project=payload.target_project,
        environment_name=payload.environment_name,
    )
