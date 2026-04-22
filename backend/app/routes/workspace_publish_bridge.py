from fastapi import APIRouter
from pydantic import BaseModel

from app.services.workspace_publish_bridge_service import (
    workspace_publish_bridge_service,
)

router = APIRouter(prefix="/api/workspace-publish-bridge", tags=["workspace-publish-bridge"])


class RestageWorkspaceFileRequest(BaseModel):
    workspace_file: str
    asset_role: str
    source_ref: str
    project_hint: str | None = None
    repository_full_name: str | None = None
    destination_path: str | None = None
    content_kind: str | None = None


class PublishWorkspaceFileRequest(BaseModel):
    workspace_file: str
    asset_role: str
    source_ref: str
    repository_full_name: str
    destination_path: str
    project_hint: str | None = None
    branch: str | None = None
    content_kind: str | None = None
    dry_run: bool = True


@router.get('/status')
async def status():
    return workspace_publish_bridge_service.get_status()


@router.get('/package')
async def package():
    return workspace_publish_bridge_service.get_package()


@router.post('/restage-workspace-file')
async def restage_workspace_file(payload: RestageWorkspaceFileRequest):
    return workspace_publish_bridge_service.restage_workspace_file(
        workspace_file=payload.workspace_file,
        asset_role=payload.asset_role,
        source_ref=payload.source_ref,
        project_hint=payload.project_hint,
        repository_full_name=payload.repository_full_name,
        destination_path=payload.destination_path,
        content_kind=payload.content_kind,
    )


@router.post('/publish-workspace-file')
async def publish_workspace_file(payload: PublishWorkspaceFileRequest):
    return await workspace_publish_bridge_service.publish_workspace_file(
        workspace_file=payload.workspace_file,
        asset_role=payload.asset_role,
        source_ref=payload.source_ref,
        repository_full_name=payload.repository_full_name,
        destination_path=payload.destination_path,
        project_hint=payload.project_hint,
        branch=payload.branch,
        content_kind=payload.content_kind,
        dry_run=payload.dry_run,
    )


@router.post('/dry-run-publish-workspace-file')
async def dry_run_publish_workspace_file(payload: PublishWorkspaceFileRequest):
    return await workspace_publish_bridge_service.publish_workspace_file(
        workspace_file=payload.workspace_file,
        asset_role=payload.asset_role,
        source_ref=payload.source_ref,
        repository_full_name=payload.repository_full_name,
        destination_path=payload.destination_path,
        project_hint=payload.project_hint,
        branch=payload.branch,
        content_kind=payload.content_kind,
        dry_run=True,
    )
