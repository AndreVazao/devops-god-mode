from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.mobile_cockpit_command_surface_service import (
    mobile_cockpit_command_surface_service,
)

router = APIRouter(prefix="/api/mobile-cockpit", tags=["mobile-cockpit"])


class MobileQuickActionAdvanceRequest(BaseModel):
    action_id: str


@router.get("/status")
async def mobile_cockpit_status():
    cards = mobile_cockpit_command_surface_service.get_cards()["cards"]
    summary = mobile_cockpit_command_surface_service.get_summary()["summary"]
    next_action = mobile_cockpit_command_surface_service.get_next_critical_action()[
        "next_critical_action"
    ]
    return {
        "ok": True,
        "mode": "mobile_cockpit_status",
        "cards_count": len(cards),
        "cockpit_status": "mobile_cockpit_ready",
        "runtime_status": summary["runtime_status"],
        "link_mode": summary["link_mode"],
        "phone_buffered": summary["phone_buffered"],
        "pc_ready": summary["pc_ready"],
        "pc_active": summary["pc_active"],
        "next_critical_action_id": next_action["action_id"] if next_action else None,
    }


@router.get("/summary")
async def mobile_cockpit_summary():
    return mobile_cockpit_command_surface_service.get_summary()


@router.get("/cards")
async def mobile_cockpit_cards():
    return mobile_cockpit_command_surface_service.get_cards()


@router.get("/quick-actions")
async def mobile_cockpit_quick_actions():
    return mobile_cockpit_command_surface_service.get_quick_actions()


@router.get("/next-critical-action")
async def mobile_cockpit_next_critical_action():
    return mobile_cockpit_command_surface_service.get_next_critical_action()


@router.post("/quick-actions/advance")
async def mobile_cockpit_advance_quick_action(payload: MobileQuickActionAdvanceRequest):
    try:
        return mobile_cockpit_command_surface_service.advance_quick_action(
            payload.action_id
        )
    except ValueError:
        raise HTTPException(status_code=404, detail="quick_action_not_found")
