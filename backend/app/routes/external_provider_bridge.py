from fastapi import APIRouter
from pydantic import BaseModel

from app.services.external_provider_bridge_service import external_provider_bridge_service

router = APIRouter(prefix="/api/external-provider-bridge", tags=["external-provider-bridge"])


class ExternalProviderBridgeRequest(BaseModel):
    provider_name: str
    target_project: str
    environment_name: str


@router.get('/status')
async def status():
    return external_provider_bridge_service.get_status()


@router.get('/package')
async def package():
    return external_provider_bridge_service.get_package()


@router.post('/build')
async def build(payload: ExternalProviderBridgeRequest):
    return external_provider_bridge_service.build_bridge_plan(
        provider_name=payload.provider_name,
        target_project=payload.target_project,
        environment_name=payload.environment_name,
    )
