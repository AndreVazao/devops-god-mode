from fastapi import APIRouter
from pydantic import BaseModel

from app.services.env_intake_service import env_intake_service

router = APIRouter(prefix="/api/env-intake", tags=["env-intake"])


class EnvIntakeRequest(BaseModel):
    env_text: str
    source_name: str
    target_project: str
    environment_name: str


@router.get('/status')
async def status():
    return env_intake_service.get_status()


@router.get('/package')
async def package():
    return env_intake_service.get_package()


@router.post('/parse')
async def parse(payload: EnvIntakeRequest):
    return env_intake_service.parse_env_text(
        env_text=payload.env_text,
        source_name=payload.source_name,
        target_project=payload.target_project,
        environment_name=payload.environment_name,
    )
