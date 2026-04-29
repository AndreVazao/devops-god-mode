from typing import Any, Dict

from fastapi import APIRouter
from pydantic import BaseModel

from app.services.mobile_result_normalizer_service import mobile_result_normalizer_service

router = APIRouter(prefix="/api/mobile-result", tags=["mobile-result-normalizer"])


class NormalizeRequest(BaseModel):
    payload: Dict[str, Any]
    source_endpoint: str | None = None
    label: str | None = None


@router.get('/status')
async def status(tenant_id: str = "owner-andre"):
    return mobile_result_normalizer_service.get_status(tenant_id=tenant_id)


@router.post('/status')
async def post_status(tenant_id: str = "owner-andre"):
    return mobile_result_normalizer_service.get_status(tenant_id=tenant_id)


@router.get('/contract')
async def contract():
    return mobile_result_normalizer_service.presentation_contract()


@router.post('/contract')
async def post_contract():
    return mobile_result_normalizer_service.presentation_contract()


@router.get('/catalog')
async def catalog(tenant_id: str = "owner-andre", requested_project: str = "GOD_MODE"):
    return mobile_result_normalizer_service.build_catalog(
        tenant_id=tenant_id,
        requested_project=requested_project,
    )


@router.post('/catalog')
async def post_catalog(tenant_id: str = "owner-andre", requested_project: str = "GOD_MODE"):
    return mobile_result_normalizer_service.build_catalog(
        tenant_id=tenant_id,
        requested_project=requested_project,
    )


@router.get('/home')
async def home(tenant_id: str = "owner-andre"):
    return mobile_result_normalizer_service.normalize_home(tenant_id=tenant_id)


@router.post('/home')
async def post_home(tenant_id: str = "owner-andre"):
    return mobile_result_normalizer_service.normalize_home(tenant_id=tenant_id)


@router.post('/normalize')
async def normalize(payload: NormalizeRequest):
    return mobile_result_normalizer_service.normalize(
        payload=payload.payload,
        source_endpoint=payload.source_endpoint,
        label=payload.label,
    )


@router.get('/package')
async def package(tenant_id: str = "owner-andre", requested_project: str = "GOD_MODE"):
    return mobile_result_normalizer_service.get_package(
        tenant_id=tenant_id,
        requested_project=requested_project,
    )


@router.post('/package')
async def post_package(tenant_id: str = "owner-andre", requested_project: str = "GOD_MODE"):
    return mobile_result_normalizer_service.get_package(
        tenant_id=tenant_id,
        requested_project=requested_project,
    )
