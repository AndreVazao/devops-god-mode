from fastapi import APIRouter
from pydantic import BaseModel

from app.services.revenue_sprint_planner_service import revenue_sprint_planner_service

router = APIRouter(prefix="/api/revenue-sprint", tags=["revenue-sprint"])


class SprintRequest(BaseModel):
    max_projects: int = 3
    tenant_id: str = "owner-andre"


@router.get('/status')
async def status():
    return revenue_sprint_planner_service.get_status()


@router.get('/package')
async def package():
    return revenue_sprint_planner_service.get_package()


@router.get('/dashboard')
async def dashboard():
    return revenue_sprint_planner_service.build_dashboard()


@router.post('/create')
async def create(payload: SprintRequest):
    return revenue_sprint_planner_service.create_sprint(max_projects=payload.max_projects, tenant_id=payload.tenant_id)


@router.post('/approval-card')
async def approval_card(payload: SprintRequest):
    created = revenue_sprint_planner_service.create_sprint(max_projects=payload.max_projects, tenant_id=payload.tenant_id)
    if not created.get("ok"):
        return created
    return revenue_sprint_planner_service.create_approval_card_for_latest_sprint(tenant_id=payload.tenant_id)


@router.get('/sprints')
async def sprints(limit: int = 20):
    return revenue_sprint_planner_service.list_sprints(limit=limit)
