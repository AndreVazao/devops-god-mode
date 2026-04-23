from fastapi import APIRouter
from pydantic import BaseModel

from app.services.intelligent_repo_state_service import intelligent_repo_state_service

router = APIRouter(prefix="/api/intelligent-repo-state", tags=["intelligent-repo-state"])


class IntelligentRepoStatePrepareRequest(BaseModel):
    bundle_id: str
    target_project: str
    desired_capabilities: list[str]
    overwrite_existing: bool = False


@router.get('/status')
async def status():
    return intelligent_repo_state_service.get_status()


@router.get('/package')
async def package():
    return intelligent_repo_state_service.get_package()


@router.get('/inspect/{bundle_id}/{target_project}')
async def inspect(bundle_id: str, target_project: str):
    return intelligent_repo_state_service.inspect_merge_workspace(bundle_id=bundle_id, target_project=target_project)


@router.post('/prepare')
async def prepare(payload: IntelligentRepoStatePrepareRequest):
    return intelligent_repo_state_service.prepare_merge_with_inspection(
        bundle_id=payload.bundle_id,
        target_project=payload.target_project,
        desired_capabilities=payload.desired_capabilities,
        overwrite_existing=payload.overwrite_existing,
    )
