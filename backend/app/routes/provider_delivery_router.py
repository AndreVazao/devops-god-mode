from fastapi import APIRouter

from app.services.provider_completion_router_service import provider_completion_router_service

router = APIRouter(prefix="/api/provider-delivery-router", tags=["provider-delivery-router"])


@router.get('/status')
async def status():
    return provider_completion_router_service.get_status()


@router.post('/status')
async def post_status():
    return provider_completion_router_service.get_status()


@router.get('/panel')
async def panel():
    return provider_completion_router_service.panel()


@router.post('/panel')
async def post_panel():
    return provider_completion_router_service.panel()


@router.get('/policy')
async def policy():
    return provider_completion_router_service.policy()


@router.post('/policy')
async def post_policy():
    return provider_completion_router_service.policy()


@router.get('/latest')
async def latest():
    return provider_completion_router_service.latest()


@router.post('/latest')
async def post_latest():
    return provider_completion_router_service.latest()


@router.get('/package')
async def package():
    return provider_completion_router_service.get_package()


@router.post('/package')
async def post_package():
    return provider_completion_router_service.get_package()
