from typing import Dict, Any
from .andreos_memory_reader_service import andreos_memory_reader_service
from .self_state_analyzer_service import self_state_analyzer_service
from .gap_detector_service import gap_detector_service
from .roadmap_generator_service import roadmap_generator_service
from .phase_planner_service import phase_planner_service
from .self_evolution_gate_service import self_evolution_gate_service
from .cross_project_intelligence import cross_project_intelligence_service
from app.services.god_mode_global_state_service import god_mode_global_state_service

class SelfEvolutionEngineService:
    def run_self_evolution(self) -> Dict[str, Any]:
        global_state = god_mode_global_state_service.package()

        memory = andreos_memory_reader_service.read_memory()

        state_issues = self_state_analyzer_service.analyze_state(global_state)

        # Cross-project intelligence injection
        cross_intel = cross_project_intelligence_service.run_cross_intelligence(context=["self-evolution", "multi-repo"])

        gaps = gap_detector_service.detect_gaps(memory, state_issues)

        roadmap = roadmap_generator_service.generate_roadmap(gaps)

        if not roadmap:
            return {"status": "no_evolution_needed"}

        next_phase = roadmap[0]

        plan = phase_planner_service.plan_phase(next_phase)

        approval = self_evolution_gate_service.require_approval(plan)

        return {
            "status": "awaiting_approval",
            "approval": approval,
            "roadmap": roadmap,
            "cross_project_intelligence": cross_intel
        }

self_evolution_engine_service = SelfEvolutionEngineService()
