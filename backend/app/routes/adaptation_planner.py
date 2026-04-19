from fastapi import APIRouter

from app.services.adaptation_planner_service import adaptation_planner_service

router = APIRouter(prefix="/api/adaptation-planner", tags=["adaptation-planner"])


@router.get("/status")
async def adaptation_planner_status():
    plans = adaptation_planner_service.get_adaptation_plans()["adaptation_plans"]
    return {
        "ok": True,
        "mode": "adaptation_planner_status",
        "adaptation_plans_count": len(plans),
        "adaptation_status": "adaptation_planner_ready",
    }


@router.get("/plans")
async def adaptation_planner_plans():
    return adaptation_planner_service.get_adaptation_plans()


@router.get("/target-fit")
async def adaptation_planner_target_fit():
    return adaptation_planner_service.get_target_fit()


@router.get("/best-plans")
async def adaptation_planner_best_plans():
    return adaptation_planner_service.get_best_plans()


@router.get("/blockers")
async def adaptation_planner_blockers():
    return adaptation_planner_service.get_blockers()
