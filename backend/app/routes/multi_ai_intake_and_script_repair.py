from fastapi import APIRouter

from app.services.multi_ai_intake_and_script_repair_service import (
    multi_ai_intake_and_script_repair_service,
)

router = APIRouter(prefix="/api/multi-ai-repair", tags=["multi-ai-repair"])


@router.get("/status")
async def multi_ai_repair_status():
    issues = multi_ai_intake_and_script_repair_service.get_broken_scripts()["issues"]
    return {
        "ok": True,
        "mode": "multi_ai_repair_status",
        "sources_count": len(multi_ai_intake_and_script_repair_service.get_sources()["sources"]),
        "issues_count": len(issues),
    }


@router.get("/sources")
async def multi_ai_repair_sources():
    return multi_ai_intake_and_script_repair_service.get_sources()


@router.get("/broken-scripts")
async def multi_ai_repair_broken_scripts():
    return multi_ai_intake_and_script_repair_service.get_broken_scripts()


@router.get("/repair-plan")
async def multi_ai_repair_plan():
    return multi_ai_intake_and_script_repair_service.get_repair_plan()


@router.get("/next-repair")
async def multi_ai_repair_next_repair():
    return multi_ai_intake_and_script_repair_service.get_next_repair()
