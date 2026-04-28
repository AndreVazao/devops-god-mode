from fastapi import APIRouter
from pydantic import BaseModel

from app.services.local_ai_adapter_service import local_ai_adapter_service

router = APIRouter(prefix="/api/local-ai", tags=["local-ai"])


class LocalAiTextRequest(BaseModel):
    text: str


class LocalAiGenerateRequest(BaseModel):
    prompt: str
    model: str | None = None


@router.get('/status')
async def status():
    return local_ai_adapter_service.get_status()


@router.get('/panel')
async def panel():
    return local_ai_adapter_service.build_panel()


@router.get('/models')
async def models():
    return local_ai_adapter_service.list_models()


@router.post('/classify')
async def classify(payload: LocalAiTextRequest):
    return local_ai_adapter_service.classify_operator_text(payload.text)


@router.post('/generate-short')
async def generate_short(payload: LocalAiGenerateRequest):
    return local_ai_adapter_service.generate_short(
        prompt=payload.prompt,
        model=payload.model,
    )


@router.get('/package')
async def package():
    return local_ai_adapter_service.get_package()
