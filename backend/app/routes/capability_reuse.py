from fastapi import APIRouter
from pydantic import BaseModel

from app.services.capability_reuse_service import capability_reuse_service

router = APIRouter(prefix="/api/capability-reuse", tags=["capability-reuse"])


class ReusePlanRequest(BaseModel):
    capability_name: str
    target_project: str


@router.get('/status')
async def status():
    return capability_reuse_service.get_status()


@router.get('/package')
async def package():
    return capability_reuse_service.get_package()


@router.get('/lookup/{capability_name}')
async def lookup(capability_name: str):
    return capability_reuse_service.lookup_capability(capability_name)


@router.post('/suggest-plan')
async def suggest_plan(payload: ReusePlanRequest):
    return capability_reuse_service.suggest_reuse_plan(
        capability_name=payload.capability_name,
        target_project=payload.target_project,
    )


@router.post('/export-index')
async def export_index():
    return capability_reuse_service.export_capability_index()
