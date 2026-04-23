from fastapi import APIRouter
from pydantic import BaseModel

from app.services.intelligent_repo_merge_service import intelligent_repo_merge_service

router = APIRouter(prefix="/api/intelligent-repo-merge", tags=["intelligent-repo-merge"])


class IntelligentRepoMergeRequest(BaseModel):
    bundle_id: str
    target_project: str
    desired_capabilities: list[str]
    overwrite_existing: bool = False


@router.get('/status')
async def status():
    return intelligent_repo_merge_service.get_status()


@router.get('/package')
async def package():
    return intelligent_repo_merge_service.get_package()


@router.post('/merge')
async def merge(payload: IntelligentRepoMergeRequest):
    return intelligent_repo_merge_service.merge_applied_patch(
        bundle_id=payload.bundle_id,
        target_project=payload.target_project,
        desired_capabilities=payload.desired_capabilities,
        overwrite_existing=payload.overwrite_existing,
    )
