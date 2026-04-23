from fastapi import APIRouter
from pydantic import BaseModel

from app.services.provider_secret_sync_service import provider_secret_sync_service

router = APIRouter(prefix="/api/provider-secret-sync", tags=["provider-secret-sync"])


class ProviderSecretSyncRequest(BaseModel):
    target_project: str
    environment_name: str
    provider_name: str


@router.get('/status')
async def status():
    return provider_secret_sync_service.get_status()


@router.get('/package')
async def package():
    return provider_secret_sync_service.get_package()


@router.post('/build')
async def build(payload: ProviderSecretSyncRequest):
    return provider_secret_sync_service.build_sync_plan(
        target_project=payload.target_project,
        environment_name=payload.environment_name,
        provider_name=payload.provider_name,
    )
