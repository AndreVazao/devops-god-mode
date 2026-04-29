from fastapi import APIRouter

from app.services.real_install_smoke_test_service import real_install_smoke_test_service

router = APIRouter(prefix="/api/real-install-smoke-test", tags=["real-install-smoke-test"])


@router.get('/status')
async def status():
    return real_install_smoke_test_service.get_status()


@router.post('/status')
async def post_status():
    return real_install_smoke_test_service.get_status()


@router.get('/panel')
async def panel():
    return real_install_smoke_test_service.panel()


@router.post('/panel')
async def post_panel():
    return real_install_smoke_test_service.panel()


@router.get('/ci-safe')
async def ci_safe():
    return real_install_smoke_test_service.run_ci_safe()


@router.post('/ci-safe')
async def post_ci_safe():
    return real_install_smoke_test_service.run_ci_safe()


@router.get('/local-contract')
async def local_contract():
    return real_install_smoke_test_service.local_contract()


@router.post('/local-contract')
async def post_local_contract():
    return real_install_smoke_test_service.local_contract()


@router.get('/latest')
async def latest():
    return real_install_smoke_test_service.latest()


@router.post('/latest')
async def post_latest():
    return real_install_smoke_test_service.latest()


@router.get('/package')
async def package():
    return real_install_smoke_test_service.get_package()


@router.post('/package')
async def post_package():
    return real_install_smoke_test_service.get_package()
