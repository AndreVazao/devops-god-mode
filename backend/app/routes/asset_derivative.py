from fastapi import APIRouter
from pydantic import BaseModel

from app.services.asset_derivative_service import asset_derivative_service

router = APIRouter(prefix="/api/asset-derivative", tags=["asset-derivative"])


class SvgWrapperRequest(BaseModel):
    workspace_file: str
    output_name: str
    title: str | None = None
    background: str | None = None


class BinarySidecarRequest(BaseModel):
    workspace_file: str
    label: str


@router.get('/status')
async def status():
    return asset_derivative_service.get_status()


@router.get('/package')
async def package():
    return asset_derivative_service.get_package()


@router.post('/create-svg-wrapper')
async def create_svg_wrapper(payload: SvgWrapperRequest):
    return asset_derivative_service.create_svg_wrapper(
        workspace_file=payload.workspace_file,
        output_name=payload.output_name,
        title=payload.title,
        background=payload.background,
    )


@router.post('/create-binary-sidecar')
async def create_binary_sidecar(payload: BinarySidecarRequest):
    return asset_derivative_service.create_binary_metadata_sidecar(
        workspace_file=payload.workspace_file,
        label=payload.label,
    )
