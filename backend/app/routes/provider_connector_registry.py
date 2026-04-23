from fastapi import APIRouter

from app.services.provider_connector_registry_service import provider_connector_registry_service

router = APIRouter(prefix="/api/provider-connector-registry", tags=["provider-connector-registry"])


@router.get('/status')
async def status():
    return provider_connector_registry_service.get_status()


@router.get('/package')
async def package():
    return provider_connector_registry_service.get_package()


@router.get('/list')
async def list_providers():
    return provider_connector_registry_service.list_providers()
