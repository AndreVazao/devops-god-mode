from typing import Optional

from fastapi import APIRouter
from pydantic import BaseModel

from app.services.local_performance_autopilot_service import local_performance_autopilot_service

router = APIRouter(prefix="/api/local-performance-autopilot", tags=["local-performance-autopilot"])


class PerformancePlanRequest(BaseModel):
    pc_profile: str = "auto"
    run_ollama_benchmark: bool = False
    ollama_timeout_seconds: Optional[int] = None
    max_ollama_models: int = 20


class PerformanceRunRequest(BaseModel):
    pc_profile: str = "auto"
    run_ollama_benchmark: bool = True
    ollama_timeout_seconds: Optional[int] = None
    max_ollama_models: int = 20


@router.get('/status')
async def status():
    return local_performance_autopilot_service.get_status()


@router.post('/status')
async def post_status():
    return local_performance_autopilot_service.get_status()


@router.get('/panel')
async def panel():
    return local_performance_autopilot_service.panel()


@router.post('/panel')
async def post_panel():
    return local_performance_autopilot_service.panel()


@router.get('/policy')
async def policy():
    return local_performance_autopilot_service.policy()


@router.post('/policy')
async def post_policy():
    return local_performance_autopilot_service.policy()


@router.post('/plan')
async def plan(payload: PerformancePlanRequest):
    return local_performance_autopilot_service.plan(
        pc_profile=payload.pc_profile,
        run_ollama_benchmark=payload.run_ollama_benchmark,
        ollama_timeout_seconds=payload.ollama_timeout_seconds,
        max_ollama_models=payload.max_ollama_models,
    )


@router.post('/run-safe')
async def run_safe(payload: PerformanceRunRequest):
    return local_performance_autopilot_service.run_safe(
        pc_profile=payload.pc_profile,
        run_ollama_benchmark=payload.run_ollama_benchmark,
        ollama_timeout_seconds=payload.ollama_timeout_seconds,
        max_ollama_models=payload.max_ollama_models,
    )


@router.get('/latest')
async def latest():
    return local_performance_autopilot_service.latest()


@router.post('/latest')
async def post_latest():
    return local_performance_autopilot_service.latest()


@router.get('/package')
async def package():
    return local_performance_autopilot_service.get_package()


@router.post('/package')
async def post_package():
    return local_performance_autopilot_service.get_package()
