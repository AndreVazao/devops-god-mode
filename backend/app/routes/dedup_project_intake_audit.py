from fastapi import APIRouter

from app.services.dedup_project_intake_audit_service import dedup_project_intake_audit_service

router = APIRouter(prefix="/api/dedup-project-intake-audit", tags=["dedup-project-intake-audit"])


@router.get('/status')
async def status():
    return dedup_project_intake_audit_service.get_status()


@router.post('/status')
async def post_status():
    return dedup_project_intake_audit_service.get_status()


@router.get('/audit')
async def audit():
    return dedup_project_intake_audit_service.build_audit()


@router.post('/audit')
async def post_audit():
    return dedup_project_intake_audit_service.build_audit()


@router.get('/package')
async def package():
    return dedup_project_intake_audit_service.get_package()


@router.post('/package')
async def post_package():
    return dedup_project_intake_audit_service.get_package()
