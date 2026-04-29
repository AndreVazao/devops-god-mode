from typing import Any, Dict, Optional

from fastapi import APIRouter
from pydantic import BaseModel

from app.services.first_real_run_checklist_service import first_real_run_checklist_service

router = APIRouter(prefix="/api/first-real-run", tags=["first-real-run"])


class StartRequest(BaseModel):
    operator: str = "Andre"
    target_pc: str = "primary_pc"
    target_phone: str = "android_phone"


class StepRequest(BaseModel):
    session_id: str
    step_id: str
    ok: bool
    detail: str = ""
    evidence: Optional[Dict[str, Any]] = None


class SessionRequest(BaseModel):
    session_id: str


class CompleteRequest(BaseModel):
    session_id: str
    operator_ok: bool = False


@router.get('/status')
async def status():
    return first_real_run_checklist_service.get_status()


@router.post('/status')
async def post_status():
    return first_real_run_checklist_service.get_status()


@router.get('/panel')
async def panel():
    return first_real_run_checklist_service.panel()


@router.post('/panel')
async def post_panel():
    return first_real_run_checklist_service.panel()


@router.post('/start')
async def start(payload: StartRequest):
    return first_real_run_checklist_service.start(
        operator=payload.operator,
        target_pc=payload.target_pc,
        target_phone=payload.target_phone,
    )


@router.post('/step')
async def step(payload: StepRequest):
    return first_real_run_checklist_service.record_step(
        session_id=payload.session_id,
        step_id=payload.step_id,
        ok=payload.ok,
        detail=payload.detail,
        evidence=payload.evidence,
    )


@router.post('/progress')
async def progress(payload: SessionRequest):
    return first_real_run_checklist_service.progress(session_id=payload.session_id)


@router.post('/complete')
async def complete(payload: CompleteRequest):
    return first_real_run_checklist_service.complete(
        session_id=payload.session_id,
        operator_ok=payload.operator_ok,
    )


@router.get('/latest')
async def latest():
    return first_real_run_checklist_service.latest()


@router.post('/latest')
async def post_latest():
    return first_real_run_checklist_service.latest()


@router.get('/package')
async def package():
    return first_real_run_checklist_service.get_package()


@router.post('/package')
async def post_package():
    return first_real_run_checklist_service.get_package()
