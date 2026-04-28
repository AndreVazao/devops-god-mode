from fastapi import APIRouter

from app.services.professional_scorecard_service import professional_scorecard_service

router = APIRouter(prefix="/api/professional-scorecard", tags=["professional-scorecard"])


@router.get('/status')
async def status(tenant_id: str = "owner-andre"):
    return professional_scorecard_service.get_status(tenant_id=tenant_id)


@router.get('/scorecard')
async def scorecard(tenant_id: str = "owner-andre", requested_project: str = "GOD_MODE"):
    return professional_scorecard_service.build_scorecard(
        tenant_id=tenant_id,
        requested_project=requested_project,
    )


@router.get('/package')
async def package(tenant_id: str = "owner-andre", requested_project: str = "GOD_MODE"):
    return professional_scorecard_service.get_package(
        tenant_id=tenant_id,
        requested_project=requested_project,
    )
