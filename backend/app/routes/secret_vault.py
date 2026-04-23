from fastapi import APIRouter
from pydantic import BaseModel

from app.services.secret_vault_service import secret_vault_service

router = APIRouter(prefix="/api/secret-vault", tags=["secret-vault"])


class SecretRegisterRequest(BaseModel):
    secret_name: str
    secret_value: str
    provider: str
    usage_scope: str
    target_refs: list[str] = []


@router.get('/status')
async def status():
    return secret_vault_service.get_status()


@router.get('/package')
async def package():
    return secret_vault_service.get_package()


@router.get('/list')
async def list_secrets():
    return secret_vault_service.list_secrets()


@router.post('/register')
async def register(payload: SecretRegisterRequest):
    return secret_vault_service.register_secret(
        secret_name=payload.secret_name,
        secret_value=payload.secret_value,
        provider=payload.provider,
        usage_scope=payload.usage_scope,
        target_refs=payload.target_refs,
    )
