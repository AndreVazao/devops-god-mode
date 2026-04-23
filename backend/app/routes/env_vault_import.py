from fastapi import APIRouter
from pydantic import BaseModel

from app.services.env_vault_import_service import env_vault_import_service

router = APIRouter(prefix="/api/env-vault-import", tags=["env-vault-import"])


class EnvVaultImportRequest(BaseModel):
    env_text: str
    source_name: str
    target_project: str
    environment_name: str


@router.get('/status')
async def status():
    return env_vault_import_service.get_status()


@router.get('/package')
async def package():
    return env_vault_import_service.get_package()


@router.post('/import')
async def import_env(payload: EnvVaultImportRequest):
    return env_vault_import_service.import_env_text(
        env_text=payload.env_text,
        source_name=payload.source_name,
        target_project=payload.target_project,
        environment_name=payload.environment_name,
    )
