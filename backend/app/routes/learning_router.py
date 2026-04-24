from fastapi import APIRouter
from pydantic import BaseModel

from app.services.learning_router_service import learning_router_service

router = APIRouter(prefix="/api/learning-router", tags=["learning-router"])


class RouteMessageRequest(BaseModel):
    message: str
    project_hint: str | None = None
    tenant_id: str = "owner-andre"
    auto_execute_confident: bool = True


class LearnPatternRequest(BaseModel):
    phrase: str
    intent: str
    action_id: str | None = None
    project: str = "GOD_MODE"
    tenant_id: str = "owner-andre"


@router.get('/status')
async def status():
    return learning_router_service.get_status()


@router.get('/package')
async def package():
    return learning_router_service.get_package()


@router.get('/dashboard')
async def dashboard():
    return learning_router_service.build_dashboard()


@router.post('/route')
async def route(payload: RouteMessageRequest):
    return learning_router_service.route_message(
        message=payload.message,
        project_hint=payload.project_hint,
        tenant_id=payload.tenant_id,
        auto_execute_confident=payload.auto_execute_confident,
    )


@router.post('/learn')
async def learn(payload: LearnPatternRequest):
    return learning_router_service.learn_pattern(
        phrase=payload.phrase,
        intent=payload.intent,
        action_id=payload.action_id,
        project=payload.project,
        tenant_id=payload.tenant_id,
    )


@router.get('/unknowns')
async def unknowns(limit: int = 50):
    return learning_router_service.list_unknowns(limit=limit)
