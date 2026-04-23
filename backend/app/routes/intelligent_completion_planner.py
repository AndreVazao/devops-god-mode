from fastapi import APIRouter
from pydantic import BaseModel

from app.services.intelligent_completion_planner_service import intelligent_completion_planner_service

router = APIRouter(prefix="/api/intelligent-completion-planner", tags=["intelligent-completion-planner"])


class CompletionPlanRequest(BaseModel):
    bundle_id: str
    target_project: str
    desired_capabilities: list[str]


@router.get('/status')
async def status():
    return intelligent_completion_planner_service.get_status()


@router.get('/package')
async def package():
    return intelligent_completion_planner_service.get_package()


@router.post('/build-plan')
async def build_plan(payload: CompletionPlanRequest):
    return intelligent_completion_planner_service.build_completion_plan(
        bundle_id=payload.bundle_id,
        target_project=payload.target_project,
        desired_capabilities=payload.desired_capabilities,
    )
