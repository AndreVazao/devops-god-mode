from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.external_asset_intake_service import external_asset_intake_service

router = APIRouter(prefix="/api/external-asset-intake", tags=["external-asset-intake"])


class StageAssetRequest(BaseModel):
    source_type: str
    source_ref: str
    asset_role: str
    project_hint: str | None = None
    repository_full_name: str | None = None
    destination_path: str | None = None
    content_text: str | None = None
    content_base64: str | None = None
    content_kind: str | None = None


@router.get("/status")
async def external_asset_intake_status():
    return external_asset_intake_service.get_status()


@router.get("/sources")
async def external_asset_intake_sources():
    return external_asset_intake_service.get_sources()


@router.post("/stage")
async def external_asset_stage(payload: StageAssetRequest):
    try:
        return external_asset_intake_service.stage_asset_request(
            source_type=payload.source_type,
            source_ref=payload.source_ref,
            asset_role=payload.asset_role,
            project_hint=payload.project_hint,
            repository_full_name=payload.repository_full_name,
            destination_path=payload.destination_path,
            content_text=payload.content_text,
            content_base64=payload.content_base64,
            content_kind=payload.content_kind,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.get("/staged-assets")
async def external_asset_staged_assets(project_hint: str | None = None):
    return external_asset_intake_service.get_staged_assets(project_hint=project_hint)


@router.get("/github-publish-plan")
async def external_asset_github_publish_plan(
    repository_full_name: str,
    project_hint: str | None = None,
):
    return external_asset_intake_service.build_github_publish_plan(
        repository_full_name=repository_full_name,
        project_hint=project_hint,
    )


@router.get("/package")
async def external_asset_intake_package():
    return external_asset_intake_service.get_package()
