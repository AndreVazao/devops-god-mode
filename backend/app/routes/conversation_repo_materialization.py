from fastapi import APIRouter
from pydantic import BaseModel

from app.services.conversation_repo_materialization_service import conversation_repo_materialization_service

router = APIRouter(prefix="/api/conversation-repo-materialization", tags=["conversation-repo-materialization"])


class MaterializeRepoPlanRequest(BaseModel):
    bundle_id: str
    repository_name: str | None = None
    overwrite_existing: bool = True


@router.get('/status')
async def status():
    return conversation_repo_materialization_service.get_status()


@router.get('/package')
async def package():
    return conversation_repo_materialization_service.get_package()


@router.post('/materialize')
async def materialize(payload: MaterializeRepoPlanRequest):
    return conversation_repo_materialization_service.materialize_bundle_repo_plan(
        bundle_id=payload.bundle_id,
        repository_name=payload.repository_name,
        overwrite_existing=payload.overwrite_existing,
    )
