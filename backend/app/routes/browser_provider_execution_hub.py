from typing import List, Optional

from fastapi import APIRouter
from pydantic import BaseModel

from app.services.browser_provider_execution_hub_service import browser_provider_execution_hub_service

router = APIRouter(prefix="/api/browser-provider-execution", tags=["browser-provider-execution"])


class ExecutionPlanRequest(BaseModel):
    project_id: str = "GOD_MODE"
    objective: str = "continue project with provider/browser execution"
    provider_preference: Optional[List[str]] = None
    allow_google_web: bool = True
    allow_provider_fallback: bool = True


class StartSessionRequest(BaseModel):
    project_id: str = "GOD_MODE"
    objective: str = "continue provider/browser work"
    provider_preference: Optional[List[str]] = None


class HandoffRequest(BaseModel):
    session_id: str
    provider_id: str
    result: str
    stop_reason: str = "work_completed"
    next_provider_id: Optional[str] = None


@router.get('/status')
async def status():
    return browser_provider_execution_hub_service.get_status()


@router.post('/status')
async def post_status():
    return browser_provider_execution_hub_service.get_status()


@router.get('/panel')
async def panel():
    return browser_provider_execution_hub_service.panel()


@router.post('/panel')
async def post_panel():
    return browser_provider_execution_hub_service.panel()


@router.get('/policy')
async def policy():
    return browser_provider_execution_hub_service.policy()


@router.post('/policy')
async def post_policy():
    return browser_provider_execution_hub_service.policy()


@router.get('/modules')
async def modules():
    return browser_provider_execution_hub_service.module_matrix()


@router.post('/modules')
async def post_modules():
    return browser_provider_execution_hub_service.module_matrix()


@router.post('/plan')
async def plan(payload: ExecutionPlanRequest):
    return browser_provider_execution_hub_service.plan(
        project_id=payload.project_id,
        objective=payload.objective,
        provider_preference=payload.provider_preference,
        allow_google_web=payload.allow_google_web,
        allow_provider_fallback=payload.allow_provider_fallback,
    )


@router.post('/session')
async def session(payload: StartSessionRequest):
    return browser_provider_execution_hub_service.start_session(
        project_id=payload.project_id,
        objective=payload.objective,
        provider_preference=payload.provider_preference,
    )


@router.post('/handoff')
async def handoff(payload: HandoffRequest):
    return browser_provider_execution_hub_service.record_handoff(
        session_id=payload.session_id,
        provider_id=payload.provider_id,
        result=payload.result,
        stop_reason=payload.stop_reason,
        next_provider_id=payload.next_provider_id,
    )


@router.get('/latest')
async def latest():
    return browser_provider_execution_hub_service.latest()


@router.post('/latest')
async def post_latest():
    return browser_provider_execution_hub_service.latest()


@router.get('/package')
async def package():
    return browser_provider_execution_hub_service.get_package()


@router.post('/package')
async def post_package():
    return browser_provider_execution_hub_service.get_package()
