from fastapi import APIRouter
from pydantic import BaseModel

from app.services.money_command_center_service import money_command_center_service

router = APIRouter(prefix="/api/money-command-center", tags=["money-command-center"])


class MoneySprintRequest(BaseModel):
    max_projects: int = 3
    tenant_id: str = "owner-andre"


class DeliveryRequest(BaseModel):
    project_id: str | None = None
    tenant_id: str = "owner-andre"


@router.get('/status')
async def status():
    return money_command_center_service.get_status()


@router.get('/package')
async def package():
    return money_command_center_service.get_package()


@router.get('/dashboard')
async def dashboard(tenant_id: str = "owner-andre"):
    return money_command_center_service.build_dashboard(tenant_id=tenant_id)


@router.get('/matrix')
async def matrix():
    return money_command_center_service.build_money_matrix()


@router.get('/top-project')
async def top_project():
    return money_command_center_service.top_project()


@router.get('/blockers')
async def blockers():
    return money_command_center_service.get_blockers()


@router.get('/sellable-offers')
async def sellable_offers():
    return money_command_center_service.get_sellable_offers()


@router.post('/revenue-sprint')
async def revenue_sprint(payload: MoneySprintRequest):
    return money_command_center_service.create_revenue_sprint(max_projects=payload.max_projects, tenant_id=payload.tenant_id)


@router.post('/approval-card')
async def approval_card(payload: MoneySprintRequest):
    return money_command_center_service.create_approval_card(max_projects=payload.max_projects, tenant_id=payload.tenant_id)


@router.post('/prepare-mvp-delivery')
async def prepare_mvp_delivery(payload: DeliveryRequest):
    return money_command_center_service.prepare_mvp_delivery(project_id=payload.project_id, tenant_id=payload.tenant_id)
