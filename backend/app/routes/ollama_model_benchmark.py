from typing import Optional

from fastapi import APIRouter
from pydantic import BaseModel

from app.services.ollama_model_benchmark_service import ollama_model_benchmark_service

router = APIRouter(prefix="/api/ollama-model-benchmark", tags=["ollama-model-benchmark"])


class BenchmarkRequest(BaseModel):
    pc_profile: str = "auto"
    test_prompt: Optional[str] = None
    timeout_seconds: Optional[int] = None
    max_models: int = 20


@router.get('/status')
async def status():
    return ollama_model_benchmark_service.get_status()


@router.post('/status')
async def post_status():
    return ollama_model_benchmark_service.get_status()


@router.get('/panel')
async def panel():
    return ollama_model_benchmark_service.panel()


@router.post('/panel')
async def post_panel():
    return ollama_model_benchmark_service.panel()


@router.get('/policy')
async def policy():
    return ollama_model_benchmark_service.policy()


@router.post('/policy')
async def post_policy():
    return ollama_model_benchmark_service.policy()


@router.get('/models')
async def models():
    return ollama_model_benchmark_service.list_models()


@router.post('/models')
async def post_models():
    return ollama_model_benchmark_service.list_models()


@router.post('/run')
async def run(payload: BenchmarkRequest):
    return ollama_model_benchmark_service.benchmark(
        pc_profile=payload.pc_profile,
        test_prompt=payload.test_prompt,
        timeout_seconds=payload.timeout_seconds,
        max_models=payload.max_models,
    )


@router.post('/cleanup-plan')
async def cleanup_plan():
    return ollama_model_benchmark_service.cleanup_plan_from_latest()


@router.get('/latest')
async def latest():
    return ollama_model_benchmark_service.latest()


@router.post('/latest')
async def post_latest():
    return ollama_model_benchmark_service.latest()


@router.get('/package')
async def package():
    return ollama_model_benchmark_service.get_package()


@router.post('/package')
async def post_package():
    return ollama_model_benchmark_service.get_package()
