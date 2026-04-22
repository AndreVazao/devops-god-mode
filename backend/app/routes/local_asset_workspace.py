from fastapi import APIRouter
from pydantic import BaseModel

from app.services.local_asset_workspace_service import local_asset_workspace_service

router = APIRouter(prefix="/api/local-asset-workspace", tags=["local-asset-workspace"])


class StagedAssetRequest(BaseModel):
    staged_asset_id: str


class ProjectAssetRequest(BaseModel):
    project_hint: str


@router.get('/status')
async def status():
    return local_asset_workspace_service.get_status()


@router.get('/package')
async def package():
    return local_asset_workspace_service.get_package()


@router.post('/staged-asset')
async def staged_asset(payload: StagedAssetRequest):
    return local_asset_workspace_service.materialize_staged_asset_to_disk(payload.staged_asset_id)


@router.post('/project-assets')
async def project_assets(payload: ProjectAssetRequest):
    return local_asset_workspace_service.materialize_project_assets_to_disk(payload.project_hint)
