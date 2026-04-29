from typing import List, Optional

from fastapi import APIRouter
from pydantic import BaseModel

from app.services.autonomous_install_research_code_service import autonomous_install_research_code_service

router = APIRouter(prefix="/api/autonomous-delivery", tags=["autonomous-delivery"])


class AutoInstallRequest(BaseModel):
    pc_profile: str = "auto"


class ResearchPlanRequest(BaseModel):
    project_id: Optional[str] = None
    topic: str = ""
    objective: str = "recolher informação útil para desenvolvimento do projeto"
    include_google: bool = True
    include_ai_providers: bool = True


class ResearchNoteRequest(BaseModel):
    project_id: Optional[str] = None
    source: str = "manual"
    title: str = ""
    summary: str = ""
    url: Optional[str] = None
    usefulness_score: int = 70


class CodeContractRequest(BaseModel):
    project_id: Optional[str] = None
    goal: str = "entregar programa funcional"
    language: str = "auto"
    target_files: Optional[List[str]] = None


class DeliveryRunRequest(BaseModel):
    project_id: Optional[str] = None
    goal: str = "continuar até produto funcional"
    topic: str = ""
    language: str = "auto"
    pc_profile: str = "auto"


class ProviderScoreRequest(BaseModel):
    provider_id: str
    success: bool
    reason: str = ""
    project_id: Optional[str] = None


@router.get('/status')
async def status():
    return autonomous_install_research_code_service.get_status()


@router.post('/status')
async def post_status():
    return autonomous_install_research_code_service.get_status()


@router.get('/panel')
async def panel():
    return autonomous_install_research_code_service.panel()


@router.post('/panel')
async def post_panel():
    return autonomous_install_research_code_service.panel()


@router.get('/policy')
async def policy():
    return autonomous_install_research_code_service.policy()


@router.post('/policy')
async def post_policy():
    return autonomous_install_research_code_service.policy()


@router.post('/auto-install-decision')
async def auto_install_decision(payload: AutoInstallRequest):
    return autonomous_install_research_code_service.decide_auto_install(pc_profile=payload.pc_profile)


@router.post('/research-plan')
async def research_plan(payload: ResearchPlanRequest):
    return autonomous_install_research_code_service.research_plan(
        project_id=payload.project_id,
        topic=payload.topic,
        objective=payload.objective,
        include_google=payload.include_google,
        include_ai_providers=payload.include_ai_providers,
    )


@router.post('/research-note')
async def research_note(payload: ResearchNoteRequest):
    return autonomous_install_research_code_service.add_research_note(
        project_id=payload.project_id,
        source=payload.source,
        title=payload.title,
        summary=payload.summary,
        url=payload.url,
        usefulness_score=payload.usefulness_score,
    )


@router.post('/code-contract')
async def code_contract(payload: CodeContractRequest):
    return autonomous_install_research_code_service.code_contract(
        project_id=payload.project_id,
        goal=payload.goal,
        language=payload.language,
        target_files=payload.target_files,
    )


@router.post('/run')
async def delivery_run(payload: DeliveryRunRequest):
    return autonomous_install_research_code_service.delivery_run(
        project_id=payload.project_id,
        goal=payload.goal,
        topic=payload.topic,
        language=payload.language,
        pc_profile=payload.pc_profile,
    )


@router.post('/provider-score')
async def provider_score(payload: ProviderScoreRequest):
    return autonomous_install_research_code_service.provider_score(
        provider_id=payload.provider_id,
        success=payload.success,
        reason=payload.reason,
        project_id=payload.project_id,
    )


@router.get('/latest')
async def latest():
    return autonomous_install_research_code_service.latest()


@router.post('/latest')
async def post_latest():
    return autonomous_install_research_code_service.latest()


@router.get('/package')
async def package():
    return autonomous_install_research_code_service.get_package()


@router.post('/package')
async def post_package():
    return autonomous_install_research_code_service.get_package()
