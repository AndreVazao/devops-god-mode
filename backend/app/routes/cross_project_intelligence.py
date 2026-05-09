from fastapi import APIRouter
from pydantic import BaseModel, Field
from app.services.cross_project_intelligence import cross_project_intelligence_service

router = APIRouter(prefix="/api/cross-project-intelligence", tags=["cross-project-intelligence"])

class IntelligenceRequest(BaseModel):
    context: list[str] = Field(default_factory=list)

@router.post("/run")
async def run_intelligence(request: IntelligenceRequest):
    return cross_project_intelligence_service.run_cross_intelligence(request.context)
