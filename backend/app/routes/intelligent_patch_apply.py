from fastapi import APIRouter
from pydantic import BaseModel

from app.services.intelligent_patch_apply_service import intelligent_patch_apply_service

router = APIRouter(prefix="/api/intelligent-patch-apply", tags=["intelligent-patch-apply"])


class IntelligentPatchApplyRequest(BaseModel):
    bundle_id: str
    target_project: str
    desired_capabilities: list[str]
    overwrite_existing: bool = True


@router.get('/status')
async def status():
    return intelligent_patch_apply_service.get_status()


@router.get('/package')
async def package():
    return intelligent_patch_apply_service.get_package()


@router.post('/apply')
async def apply_patch(payload: IntelligentPatchApplyRequest):
    return intelligent_patch_apply_service.apply_synthesized_patch(
        bundle_id=payload.bundle_id,
        target_project=payload.target_project,
        desired_capabilities=payload.desired_capabilities,
        overwrite_existing=payload.overwrite_existing,
    )
