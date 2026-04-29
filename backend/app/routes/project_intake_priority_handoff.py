from typing import Any, Dict, List, Optional

from fastapi import APIRouter
from pydantic import BaseModel

from app.services.project_intake_priority_handoff_service import project_intake_priority_handoff_service

router = APIRouter(prefix="/api/project-intake-priority-handoff", tags=["project-intake-priority-handoff"])


class HandoffReviewRequest(BaseModel):
    tenant_id: str = "owner-andre"
    requested_project: str = "GOD_MODE"


class HandoffConfirmRequest(BaseModel):
    tenant_id: str = "owner-andre"
    ordered_project_ids: List[str]
    active_project: Optional[str] = None
    confirmed_project_groups: List[Dict[str, Any]] = []
    external_ai_scan_permission: str = "manual_login_only_no_prompt_send"
    note: Optional[str] = None


class HandoffSuggestedRequest(BaseModel):
    tenant_id: str = "owner-andre"
    note: Optional[str] = None


class HandoffDeferRequest(BaseModel):
    tenant_id: str = "owner-andre"
    reason: str = "operator_deferred"


@router.get('/status')
async def status():
    return project_intake_priority_handoff_service.get_status()


@router.post('/status')
async def post_status():
    return project_intake_priority_handoff_service.get_status()


@router.get('/review')
async def review(tenant_id: str = "owner-andre", requested_project: str = "GOD_MODE"):
    return project_intake_priority_handoff_service.build_review(
        tenant_id=tenant_id,
        requested_project=requested_project,
    )


@router.post('/review')
async def post_review(payload: HandoffReviewRequest):
    return project_intake_priority_handoff_service.build_review(
        tenant_id=payload.tenant_id,
        requested_project=payload.requested_project,
    )


@router.get('/current')
async def current():
    return project_intake_priority_handoff_service.get_current()


@router.post('/current')
async def post_current():
    return project_intake_priority_handoff_service.get_current()


@router.post('/confirm-suggested')
async def confirm_suggested(payload: HandoffSuggestedRequest):
    return project_intake_priority_handoff_service.confirm_suggested(
        tenant_id=payload.tenant_id,
        note=payload.note,
    )


@router.post('/confirm')
async def confirm(payload: HandoffConfirmRequest):
    return project_intake_priority_handoff_service.confirm(
        tenant_id=payload.tenant_id,
        ordered_project_ids=payload.ordered_project_ids,
        active_project=payload.active_project,
        confirmed_project_groups=payload.confirmed_project_groups,
        external_ai_scan_permission=payload.external_ai_scan_permission,
        note=payload.note,
    )


@router.post('/defer')
async def defer(payload: HandoffDeferRequest):
    return project_intake_priority_handoff_service.defer(
        tenant_id=payload.tenant_id,
        reason=payload.reason,
    )


@router.get('/package')
async def package():
    return project_intake_priority_handoff_service.get_package()


@router.post('/package')
async def post_package():
    return project_intake_priority_handoff_service.get_package()
