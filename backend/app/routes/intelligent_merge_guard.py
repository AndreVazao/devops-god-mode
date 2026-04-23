from fastapi import APIRouter

from app.services.intelligent_merge_guard_service import intelligent_merge_guard_service

router = APIRouter(prefix="/api/intelligent-merge-guard", tags=["intelligent-merge-guard"])


@router.get('/status')
async def status():
    return intelligent_merge_guard_service.get_status()


@router.get('/package')
async def package():
    return intelligent_merge_guard_service.get_package()


@router.get('/evaluate/{bundle_id}/{target_project}')
async def evaluate(bundle_id: str, target_project: str):
    return intelligent_merge_guard_service.evaluate_merge_workspace(bundle_id=bundle_id, target_project=target_project)
