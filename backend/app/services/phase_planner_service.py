import time
from typing import Dict, Any

class PhasePlannerService:
    def plan_phase(self, roadmap_item: Dict[str, Any]) -> Dict[str, Any]:
        phase_id = int(time.time())

        return {
            "action": "dev_loop",
            "phase_number": phase_id,
            "initial_message": f"Auto phase: {roadmap_item['phase']}",
            "meta": roadmap_item
        }

phase_planner_service = PhasePlannerService()
