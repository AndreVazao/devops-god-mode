from fastapi import APIRouter
from pydantic import BaseModel

from app.services.external_asset_publish_execution_service import (
    external_asset_publish_execution_service,
)

router = APIRouter(
    prefix="/api/external-asset-publish",
    tags=["external-asset-publish"],
)


class ExecutePublishPlanRequest(BaseModel):
    repository_full_name: str
    project_hint: str | None = None
    branch: str | None = None
    dry_run: bool = True


@router.get("/status")
async def external_asset_publish_status():
    return external_asset_publish_execution_service.get_status()


@router.get("/package")
async def external_asset_publish_package():
    return external_asset_publish_execution_service.get_package()


@router.post("/execute")
async def external_asset_publish_execute(payload: ExecutePublishPlanRequest):
    return await external_asset_publish_execution_service.execute_publish_plan(
        repository_full_name=payload.repository_full_name,
        project_hint=payload.project_hint,
        branch=payload.branch,
        dry_run=payload.dry_run,
    )
