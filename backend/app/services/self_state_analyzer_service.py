from typing import List, Dict, Any
from app.services.god_mode_global_state_service import god_mode_global_state_service

class SelfStateAnalyzerService:
    def analyze_state(self, global_state: Dict[str, Any]) -> List[str]:
        issues = []

        status = global_state.get("status", {})

        # Check for remote access readiness
        if not status.get("pc_brain"):
             issues.append("pc_brain_not_ready")

        # Check for mobile cockpit readiness
        if not status.get("mobile_first"):
             issues.append("mobile_cockpit_not_ready")

        # Check for relay active (placeholder logic as per requirements)
        if not status.get("relay_active", False):
            issues.append("relay_not_active")

        # Check for current phase vs latest merged
        current_phase = status.get("current_phase", 0)
        latest_merged = status.get("latest_merged_phase", 0)

        if current_phase > latest_merged:
            # We are in the middle of a phase
            pass

        return issues

self_state_analyzer_service = SelfStateAnalyzerService()
