from fastapi import APIRouter
from pydantic import BaseModel

from app.services.external_asset_materialization_service import (
    external_asset_materialization_service,
)

router = APIRouter(
    prefix="/api/external-asset-materialization",
    tags=["external-asset-materialization"],
)


class MaterializeGitHubFileRequest(BaseModel):
    repository_full_name: str
    file_path: str
    asset_role: str
    project_hint: str | None = None
    destination_path: str | None = None
    ref: str | None = None


@router.get("/status")
async def external_asset_materialization_status():
    return external_asset_materialization_service.get_status()


@router.get("/package")
async def external_asset_materialization_package():
    return external_asset_materialization_service.get_package()


@router.post("/materialize-github-file")
async def external_asset_materialize_github_file(payload: MaterializeGitHubFileRequest):
    return await external_asset_materialization_service.materialize_github_file_to_stage(
        repository_full_name=payload.repository_full_name,
        file_path=payload.file_path,
        asset_role=payload.asset_role,
        project_hint=payload.project_hint,
        destination_path=payload.destination_path,
        ref=payload.ref,
    )
