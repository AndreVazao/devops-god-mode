from fastapi import APIRouter

from app.services.andreos_memory_audit_service import andreos_memory_audit_service

router = APIRouter(prefix="/api/andreos-memory-audit", tags=["andreos-memory-audit"])


@router.get('/status')
async def status():
    return andreos_memory_audit_service.get_status()


@router.get('/package')
async def package():
    return andreos_memory_audit_service.get_package()


@router.get('/audit')
async def audit(run_rehearsal: bool = True):
    return andreos_memory_audit_service.build_audit(run_rehearsal=run_rehearsal)
