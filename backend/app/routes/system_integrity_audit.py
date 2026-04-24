from fastapi import APIRouter

from app.services.system_integrity_audit_service import system_integrity_audit_service

router = APIRouter(prefix="/api/system-integrity-audit", tags=["system-integrity-audit"])


@router.get('/status')
async def status():
    return system_integrity_audit_service.get_status()


@router.get('/package')
async def package():
    return system_integrity_audit_service.get_package()


@router.post('/run')
async def run_audit():
    return system_integrity_audit_service.run_audit()


@router.get('/dashboard')
async def dashboard():
    return system_integrity_audit_service.build_dashboard()
