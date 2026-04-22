from fastapi import APIRouter
from pydantic import BaseModel

from app.services.local_asset_transformation_service import (
    local_asset_transformation_service,
)

router = APIRouter(prefix="/api/local-asset-transformation", tags=["local-asset-transformation"])


class TransformTextAssetRequest(BaseModel):
    workspace_file: str
    operation: str
    transform_value: str
    output_suffix: str = ".generated"


class DuplicateWorkspaceAssetRequest(BaseModel):
    workspace_file: str
    duplicate_name: str


@router.get("/status")
async def local_asset_transformation_status():
    return local_asset_transformation_service.get_status()


@router.get("/package")
async def local_asset_transformation_package():
    return local_asset_transformation_service.get_package()


@router.post("/transform-text")
async def local_asset_transformation_transform_text(payload: TransformTextAssetRequest):
    return local_asset_transformation_service.transform_text_asset(
        workspace_file=payload.workspace_file,
        operation=payload.operation,
        transform_value=payload.transform_value,
        output_suffix=payload.output_suffix,
    )


@router.post("/duplicate")
async def local_asset_transformation_duplicate(payload: DuplicateWorkspaceAssetRequest):
    return local_asset_transformation_service.duplicate_workspace_asset(
        workspace_file=payload.workspace_file,
        duplicate_name=payload.duplicate_name,
    )
