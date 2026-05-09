from typing import List, Dict

class GapDetectorService:
    def detect_gaps(self, memory: Dict[str, str], state_issues: List[str]) -> List[str]:
        gaps = []

        backlog = memory.get("BACKLOG.md", "").lower()

        # Enhanced detection logic matching RoadmapGenerator
        if "executor" in backlog:
            gaps.append("executor_upgrade")

        if "relay" in backlog or "relay_not_active" in state_issues:
            gaps.append("cloud_relay_missing")

        if "vault" in backlog:
            gaps.append("vault_setup_needed")

        if "memória" in backlog or "memory" in backlog:
            gaps.append("memory_integration_needed")

        # Example gaps based on state issues
        if "pc_brain_not_ready" in state_issues:
            gaps.append("pc_brain_hardening")

        return gaps

gap_detector_service = GapDetectorService()
