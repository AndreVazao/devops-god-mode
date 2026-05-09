from fastapi import APIRouter
from app.services.self_evolution_engine_service import self_evolution_engine_service

router = APIRouter(prefix="/api/self-evolution", tags=["Self Evolution"])

@router.post("/run")
def run_evolution():
    """Triggers the self-evolution engine to analyze state and propose next phases."""
    return self_evolution_engine_service.run_self_evolution()
