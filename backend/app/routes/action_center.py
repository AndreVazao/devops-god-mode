from fastapi import APIRouter

from app.services.action_center_service import action_center_service

router = APIRouter(prefix="/api/action-center", tags=["action-center"])


@router.get("/status")
async def action_center_status():
    summary = action_center_service.get_summary()["action_center"]
    return {
        "ok": True,
        "mode": "action_center_status",
        "action_center_id": summary["action_center_id"],
        "action_center_status": summary["action_center_status"],
    }


@router.get("/summary")
async def action_center_summary():
    return action_center_service.get_summary()


@router.get("/quick-actions")
async def action_center_quick_actions():
    return action_center_service.get_quick_actions()


@router.get("/recommended-action")
async def action_center_recommended_action():
    return action_center_service.get_recommended_action()
