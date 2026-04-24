from fastapi import APIRouter
from pydantic import BaseModel

from app.services.mobile_approval_cockpit_v2_service import mobile_approval_cockpit_v2_service

router = APIRouter(prefix="/api/mobile-approval-cockpit-v2", tags=["mobile-approval-cockpit-v2"])


class CreateCardRequest(BaseModel):
    title: str
    body: str
    card_type: str = "progress_update"
    project_id: str = "general-intake"
    tenant_id: str = "owner-andre"
    priority: str = "medium"
    requires_approval: bool = False
    actions: list[dict] | None = None
    source_ref: dict | None = None
    metadata: dict | None = None


class DecideCardRequest(BaseModel):
    card_id: str
    decision: str
    operator_note: str = ""
    tenant_id: str = "owner-andre"


class SeedDeployReadinessRequest(BaseModel):
    project_id: str
    tenant_id: str = "owner-andre"


@router.get('/status')
async def status():
    return mobile_approval_cockpit_v2_service.get_status()


@router.get('/package')
async def package():
    return mobile_approval_cockpit_v2_service.get_package()


@router.post('/cards')
async def create_card(payload: CreateCardRequest):
    return mobile_approval_cockpit_v2_service.create_card(
        title=payload.title,
        body=payload.body,
        card_type=payload.card_type,
        project_id=payload.project_id,
        tenant_id=payload.tenant_id,
        priority=payload.priority,
        requires_approval=payload.requires_approval,
        actions=payload.actions,
        source_ref=payload.source_ref,
        metadata=payload.metadata,
    )


@router.post('/decide')
async def decide(payload: DecideCardRequest):
    return mobile_approval_cockpit_v2_service.decide_card(
        card_id=payload.card_id,
        decision=payload.decision,
        operator_note=payload.operator_note,
        tenant_id=payload.tenant_id,
    )


@router.get('/cards')
async def cards(
    tenant_id: str = 'owner-andre',
    project_id: str | None = None,
    status: str | None = None,
    limit: int = 100,
):
    return mobile_approval_cockpit_v2_service.list_cards(
        tenant_id=tenant_id,
        project_id=project_id,
        status=status,
        limit=limit,
    )


@router.post('/seed-from-latest-command')
async def seed_from_latest_command(tenant_id: str = 'owner-andre'):
    return mobile_approval_cockpit_v2_service.seed_from_latest_operator_command(tenant_id=tenant_id)


@router.post('/seed-from-deploy-readiness')
async def seed_from_deploy_readiness(payload: SeedDeployReadinessRequest):
    return mobile_approval_cockpit_v2_service.seed_from_deploy_readiness(
        project_id=payload.project_id,
        tenant_id=payload.tenant_id,
    )


@router.get('/dashboard')
async def dashboard(tenant_id: str = 'owner-andre'):
    return mobile_approval_cockpit_v2_service.build_dashboard(tenant_id=tenant_id)
