from fastapi import APIRouter

from app.services.private_tunnel_center_service import private_tunnel_center_service

router = APIRouter(prefix="/api/private-tunnel", tags=["private-tunnel"])


@router.get('/status')
async def status():
    return private_tunnel_center_service.get_status()


@router.get('/package')
async def package():
    return private_tunnel_center_service.get_package()


@router.get('/report')
async def report():
    return private_tunnel_center_service.build_tunnel_report()


@router.get('/dashboard')
async def dashboard():
    return private_tunnel_center_service.build_dashboard()
