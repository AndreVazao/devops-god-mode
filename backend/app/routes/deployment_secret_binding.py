from fastapi import APIRouter
from pydantic import BaseModel

from app.services.deployment_secret_binding_service import deployment_secret_binding_service

router = APIRouter(prefix="/api/deployment-secret-binding", tags=["deployment-secret-binding"])


class DeploymentSecretBindRequest(BaseModel):
    target_name: str
    environment_name: str
    secret_name: str
    inject_as: str


@router.get('/status')
async def status():
    return deployment_secret_binding_service.get_status()


@router.get('/package')
async def package():
    return deployment_secret_binding_service.get_package()


@router.get('/plan/{target_name}/{environment_name}')
async def plan(target_name: str, environment_name: str):
    return deployment_secret_binding_service.build_deploy_secret_plan(target_name=target_name, environment_name=environment_name)


@router.post('/bind')
async def bind(payload: DeploymentSecretBindRequest):
    return deployment_secret_binding_service.bind_secret(
        target_name=payload.target_name,
        environment_name=payload.environment_name,
        secret_name=payload.secret_name,
        inject_as=payload.inject_as,
    )
