from fastapi import APIRouter

from app.services.provider_live_capability_service import provider_live_capability_service

router = APIRouter(prefix="/api/provider-live-capability", tags=["provider-live-capability"])


@router.get('/status')
async def status():
    return provider_live_capability_service.get_status()


@router.get('/package')
async def package():
    return provider_live_capability_service.get_package()


@router.get('/list')
async def list_capabilities():
    return provider_live_capability_service.list_capabilities()


@router.get('/provider/{provider_name}')
async def provider_item(provider_name: str):
    return provider_live_capability_service.get_provider_capability(provider_name)
