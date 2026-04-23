from fastapi import APIRouter
from pydantic import BaseModel

from app.services.guarded_deploy_promotion_service import guarded_deploy_promotion_service

router = APIRouter(prefix="/api/guarded-deploy-promotion", tags=["guarded-deploy-promotion"])


class GuardedDeployPromotionRequest(BaseModel):
    bundle_id: str
    target_project: str
    environment_name: str


@router.get('/status')
async def status():
    return guarded_deploy_promotion_service.get_status()


@router.get('/package')
async def package():
    return guarded_deploy_promotion_service.get_package()


@router.post('/prepare')
async def prepare(payload: GuardedDeployPromotionRequest):
    return guarded_deploy_promotion_service.prepare_promotion(
        bundle_id=payload.bundle_id,
        target_project=payload.target_project,
        environment_name=payload.environment_name,
    )
