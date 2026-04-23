from fastapi import APIRouter
from pydantic import BaseModel

from app.services.intelligent_patch_synthesis_service import intelligent_patch_synthesis_service

router = APIRouter(prefix="/api/intelligent-patch-synthesis", tags=["intelligent-patch-synthesis"])


class IntelligentPatchRequest(BaseModel):
    bundle_id: str
    target_project: str
    desired_capabilities: list[str]


@router.get('/status')
async def status():
    return intelligent_patch_synthesis_service.get_status()


@router.get('/package')
async def package():
    return intelligent_patch_synthesis_service.get_package()


@router.post('/synthesize')
async def synthesize(payload: IntelligentPatchRequest):
    return intelligent_patch_synthesis_service.synthesize_bundle_patch(
        bundle_id=payload.bundle_id,
        target_project=payload.target_project,
        desired_capabilities=payload.desired_capabilities,
    )
