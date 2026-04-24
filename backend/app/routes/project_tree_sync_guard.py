from fastapi import APIRouter

from app.services.project_tree_sync_guard_service import project_tree_sync_guard_service

router = APIRouter(prefix="/api/project-tree-sync-guard", tags=["project-tree-sync-guard"])


@router.get('/status')
async def status():
    return project_tree_sync_guard_service.get_status()


@router.get('/package')
async def package():
    return project_tree_sync_guard_service.get_package()


@router.get('/dashboard')
async def dashboard():
    return project_tree_sync_guard_service.build_dashboard()


@router.get('/check')
async def check():
    return project_tree_sync_guard_service.check_sync()
