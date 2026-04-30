from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Query
from pydantic import BaseModel, Field

from app.services.ollama_local_brain_adapter_service import ollama_local_brain_adapter_service


router = APIRouter(prefix="/api/ollama-local-brain", tags=["ollama-local-brain"])


class BenchmarkRequest(BaseModel):
    model: str | None = None
    prompt: str | None = None
    base_url: str = Field(default="http://127.0.0.1:11434")


class GenerateRequest(BaseModel):
    prompt: str
    model: str | None = None
    base_url: str = Field(default="http://127.0.0.1:11434")
    max_tokens: int = Field(default=256, ge=32, le=1024)


@router.get("/status")
@router.post("/status")
def status() -> dict[str, Any]:
    return ollama_local_brain_adapter_service.status()


@router.get("/panel")
@router.post("/panel")
def panel() -> dict[str, Any]:
    return ollama_local_brain_adapter_service.panel()


@router.get("/policy")
@router.post("/policy")
def policy() -> dict[str, Any]:
    return ollama_local_brain_adapter_service.policy()


@router.get("/use-cases")
@router.post("/use-cases")
def use_cases() -> dict[str, Any]:
    return ollama_local_brain_adapter_service.use_cases()


@router.get("/health")
async def health(base_url: str = Query(default="http://127.0.0.1:11434")) -> dict[str, Any]:
    return await ollama_local_brain_adapter_service.health(base_url=base_url)


@router.get("/models")
async def models(base_url: str = Query(default="http://127.0.0.1:11434")) -> dict[str, Any]:
    return await ollama_local_brain_adapter_service.models(base_url=base_url)


@router.post("/benchmark-light")
async def benchmark_light(request: BenchmarkRequest) -> dict[str, Any]:
    return await ollama_local_brain_adapter_service.benchmark_light(
        model=request.model,
        base_url=request.base_url,
        prompt=request.prompt,
    )


@router.post("/auto-select")
async def auto_select(base_url: str = Query(default="http://127.0.0.1:11434")) -> dict[str, Any]:
    return await ollama_local_brain_adapter_service.auto_select(base_url=base_url)


@router.get("/route-decision")
def route_decision(task_kind: str = Query(default="summary_private")) -> dict[str, Any]:
    return ollama_local_brain_adapter_service.route_decision(task_kind=task_kind)


@router.post("/generate")
async def generate(request: GenerateRequest) -> dict[str, Any]:
    return await ollama_local_brain_adapter_service.generate(
        prompt=request.prompt,
        model=request.model,
        base_url=request.base_url,
        max_tokens=request.max_tokens,
    )


@router.get("/package")
@router.post("/package")
async def package() -> dict[str, Any]:
    return await ollama_local_brain_adapter_service.package()
