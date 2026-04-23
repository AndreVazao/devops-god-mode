from fastapi import APIRouter
from pydantic import BaseModel

from app.services.preview_packaging_service import preview_packaging_service

router = APIRouter(prefix="/api/preview-packaging", tags=["preview-packaging"])


class PreviewBundleRequest(BaseModel):
    bundle_name: str
    workspace_files: list[str]
    title: str | None = None


@router.get('/status')
async def status():
    return preview_packaging_service.get_status()


@router.get('/package')
async def package():
    return preview_packaging_service.get_package()


@router.post('/create-preview-bundle')
async def create_preview_bundle(payload: PreviewBundleRequest):
    return preview_packaging_service.create_preview_bundle(
        bundle_name=payload.bundle_name,
        workspace_files=payload.workspace_files,
        title=payload.title,
    )
