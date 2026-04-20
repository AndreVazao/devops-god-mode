from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.driving_mode_voice_first_service import (
    driving_mode_voice_first_service,
)

router = APIRouter(prefix="/api/driving-mode", tags=["driving-mode"])


class DrivingModeConfirmRequest(BaseModel):
    reply: str


@router.get("/status")
async def driving_mode_status():
    prompts = driving_mode_voice_first_service.get_prompts()["prompts"]
    return {
        "ok": True,
        "mode": "driving_mode_status",
        "prompts_count": len(prompts),
        "driving_mode_status": "driving_mode_ready",
    }


@router.get("/summary")
async def driving_mode_summary():
    return driving_mode_voice_first_service.get_summary()


@router.get("/prompts")
async def driving_mode_prompts():
    return driving_mode_voice_first_service.get_prompts()


@router.get("/guards")
async def driving_mode_guards():
    return driving_mode_voice_first_service.get_action_guards()


@router.get("/next-safe-action")
async def driving_mode_next_safe_action():
    return driving_mode_voice_first_service.get_next_safe_action()


@router.post("/confirm")
async def driving_mode_confirm(payload: DrivingModeConfirmRequest):
    try:
        return driving_mode_voice_first_service.confirm_short_action(payload.reply)
    except ValueError:
        raise HTTPException(status_code=400, detail="invalid_reply")
