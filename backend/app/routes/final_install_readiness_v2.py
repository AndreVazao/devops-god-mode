from fastapi import APIRouter

from app.services.final_install_readiness_v2_service import final_install_readiness_v2_service

router = APIRouter(prefix="/api/final-install-readiness-v2", tags=["final-install-readiness-v2"])


@router.get('/status')
async def status():
    return final_install_readiness_v2_service.get_status()


@router.post('/status')
async def post_status():
    return final_install_readiness_v2_service.get_status()


@router.get('/panel')
async def panel():
    return final_install_readiness_v2_service.panel()


@router.post('/panel')
async def post_panel():
    return final_install_readiness_v2_service.panel()


@router.get('/check')
async def check():
    return final_install_readiness_v2_service.run_check()


@router.post('/check')
async def post_check():
    return final_install_readiness_v2_service.run_check()


@router.get('/install-contract')
async def install_contract():
    return final_install_readiness_v2_service.install_contract()


@router.post('/install-contract')
async def post_install_contract():
    return final_install_readiness_v2_service.install_contract()


@router.get('/latest')
async def latest():
    return final_install_readiness_v2_service.latest()


@router.post('/latest')
async def post_latest():
    return final_install_readiness_v2_service.latest()


@router.get('/package')
async def package():
    return final_install_readiness_v2_service.get_package()


@router.post('/package')
async def post_package():
    return final_install_readiness_v2_service.get_package()
