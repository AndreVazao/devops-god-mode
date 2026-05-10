from app.services.god_mode_global_state_service import god_mode_global_state_service
from app.services.self_state_analyzer_service import self_state_analyzer_service
from app.services.gap_detector_service import gap_detector_service
from app.services.roadmap_generator_service import roadmap_generator_service
from app.services.phase_planner_service import phase_planner_service

def generate_plan(memory):
    """
    Generates an evolution plan by analyzing global state, memory gaps,
    and generating a roadmap.
    """
    global_state = god_mode_global_state_service.package()
    state_issues = self_state_analyzer_service.analyze_state(global_state)

    gaps = gap_detector_service.detect_gaps(memory, state_issues)
    roadmap = roadmap_generator_service.generate_roadmap(gaps)

    if not roadmap:
        return None

    next_phase = roadmap[0]
    plan = phase_planner_service.plan_phase(next_phase)

    # Enrich plan with more details for the executor
    plan["title"] = f"Evolution Phase: {next_phase['phase']}"
    plan["type"] = "critical" if next_phase.get("priority") == 1 else "standard"

    return plan
