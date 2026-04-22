from fastapi import APIRouter
from pydantic import BaseModel

from app.services.external_fetch_runtime_service import external_fetch_runtime_service

router = APIRouter(prefix="/api/external-fetch-runtime", tags=["external-fetch-runtime"])


class FetchUrlToStageRequest(BaseModel):
    source_url: str
    asset_role: str
    project_hint: str | None = None
    repository_full_name: str | None = None
    destination_path: str | None = None
    source_type: str = "external_url"


@router.get('/status')
async def status():
    return external_fetch_runtime_service.get_status()


@router.get('/package')
async def package():
    return external_fetch_runtime_service.get_package()


@router.post('/fetch-url-to-stage')
async def fetch_url_to_stage(payload: FetchUrlToStageRequest):
    return await external_fetch_runtime_service.fetch_url_to_stage(
        source_url=payload.source_url,
        asset_role=payload.asset_role,
        project_hint=payload.project_hint,
        repository_full_name=payload.repository_full_name,
        destination_path=payload.destination_path,
        source_type=payload.source_type,
    )
