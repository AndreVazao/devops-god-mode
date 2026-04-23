from fastapi import APIRouter
from pydantic import BaseModel

from app.services.bundle_publish_link_service import bundle_publish_link_service

router = APIRouter(prefix="/api/bundle-publish-link", tags=["bundle-publish-link"])


class RestagePreviewBundleRequest(BaseModel):
    bundle_name: str
    repository_full_name: str
    destination_root: str
    project_hint: str | None = None
    include_archive: bool = True


class PublishPreviewBundleRequest(BaseModel):
    bundle_name: str
    repository_full_name: str
    destination_root: str
    project_hint: str | None = None
    branch: str | None = None
    include_archive: bool = True


@router.get('/status')
async def status():
    return bundle_publish_link_service.get_status()


@router.get('/package')
async def package():
    return bundle_publish_link_service.get_package()


@router.post('/restage-preview-bundle')
async def restage_preview_bundle(payload: RestagePreviewBundleRequest):
    return bundle_publish_link_service.restage_preview_bundle(
        bundle_name=payload.bundle_name,
        repository_full_name=payload.repository_full_name,
        destination_root=payload.destination_root,
        project_hint=payload.project_hint,
        include_archive=payload.include_archive,
    )


@router.post('/dry-run-publish-preview-bundle')
async def dry_run_publish_preview_bundle(payload: PublishPreviewBundleRequest):
    return await bundle_publish_link_service.dry_run_publish_preview_bundle(
        bundle_name=payload.bundle_name,
        repository_full_name=payload.repository_full_name,
        destination_root=payload.destination_root,
        project_hint=payload.project_hint,
        branch=payload.branch,
        include_archive=payload.include_archive,
    )
