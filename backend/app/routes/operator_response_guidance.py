from fastapi import APIRouter
from pydantic import BaseModel

from app.services.operator_response_guidance_service import operator_response_guidance_service

router = APIRouter(prefix="/api/operator-response-guidance", tags=["operator-response-guidance"])


class OperatorResponseGuidanceRequest(BaseModel):
    thread_id: str


@router.get('/status')
async def status():
    return operator_response_guidance_service.get_status()


@router.get('/package')
async def package():
    return operator_response_guidance_service.get_package()


@router.post('/build')
async def build(payload: OperatorResponseGuidanceRequest):
    return operator_response_guidance_service.build_guidance(thread_id=payload.thread_id)
