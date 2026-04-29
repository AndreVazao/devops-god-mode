from typing import List, Optional

from fastapi import APIRouter
from pydantic import BaseModel

from app.services.new_project_start_intake_service import new_project_start_intake_service

router = APIRouter(prefix="/api/new-project-start", tags=["new-project-start"])


class NewProjectProposalRequest(BaseModel):
    tenant_id: str = "owner-andre"
    name: str
    idea: str
    project_type: str = "unknown"
    target_platforms: Optional[List[str]] = None
    must_have: Optional[List[str]] = None
    nice_to_have: Optional[List[str]] = None
    deadline: Optional[str] = None


class ApproveNewProjectPlanRequest(BaseModel):
    tenant_id: str = "owner-andre"
    proposal_id: str
    note: str = "operator approved new project start plan"


@router.get('/status')
async def status():
    return new_project_start_intake_service.get_status()


@router.post('/status')
async def post_status():
    return new_project_start_intake_service.get_status()


@router.get('/panel')
async def panel():
    return new_project_start_intake_service.panel()


@router.post('/panel')
async def post_panel():
    return new_project_start_intake_service.panel()


@router.get('/template')
async def template():
    return new_project_start_intake_service.template()


@router.post('/template')
async def post_template():
    return new_project_start_intake_service.template()


@router.post('/propose')
async def propose(payload: NewProjectProposalRequest):
    return new_project_start_intake_service.propose(
        tenant_id=payload.tenant_id,
        name=payload.name,
        idea=payload.idea,
        project_type=payload.project_type,
        target_platforms=payload.target_platforms,
        must_have=payload.must_have,
        nice_to_have=payload.nice_to_have,
        deadline=payload.deadline,
    )


@router.post('/approve-plan')
async def approve_plan(payload: ApproveNewProjectPlanRequest):
    return new_project_start_intake_service.approve_plan(
        tenant_id=payload.tenant_id,
        proposal_id=payload.proposal_id,
        note=payload.note,
    )


@router.get('/creation-gates')
async def creation_gates(proposal_id: Optional[str] = None):
    return new_project_start_intake_service.creation_gates(proposal_id=proposal_id)


@router.post('/creation-gates')
async def post_creation_gates(proposal_id: Optional[str] = None):
    return new_project_start_intake_service.creation_gates(proposal_id=proposal_id)


@router.get('/latest')
async def latest():
    return new_project_start_intake_service.latest()


@router.post('/latest')
async def post_latest():
    return new_project_start_intake_service.latest()


@router.get('/package')
async def package():
    return new_project_start_intake_service.get_package()


@router.post('/package')
async def post_package():
    return new_project_start_intake_service.get_package()
