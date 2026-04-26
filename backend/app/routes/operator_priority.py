from fastapi import APIRouter
from pydantic import BaseModel

from app.services.operator_priority_service import operator_priority_service

router = APIRouter(prefix="/api/operator-priority", tags=["operator-priority"])


class ProjectOrderRequest(BaseModel):
    ordered_project_ids: list[str]
    active_project: str | None = None
    note: str | None = None


class ActiveProjectRequest(BaseModel):
    project_id: str
    note: str | None = None


@router.get('/status')
async def status():
    return operator_priority_service.get_status()


@router.get('/package')
async def package():
    return operator_priority_service.get_package()


@router.get('/priorities')
async def priorities():
    return operator_priority_service.get_priorities()


@router.get('/resolve')
async def resolve(project_id: str | None = None):
    return operator_priority_service.resolve_project(project_id)


@router.post('/order')
async def set_order(payload: ProjectOrderRequest):
    return operator_priority_service.set_order(
        ordered_project_ids=payload.ordered_project_ids,
        active_project=payload.active_project,
        note=payload.note,
    )


@router.post('/active')
async def set_active(payload: ActiveProjectRequest):
    return operator_priority_service.set_active_project(payload.project_id, note=payload.note)
