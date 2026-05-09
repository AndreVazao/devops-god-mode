from typing import List, Dict, Any

class RoadmapGeneratorService:
    def generate_roadmap(self, gaps: List[str]) -> List[Dict[str, Any]]:
        roadmap = []

        for g in gaps:
            if g == "cloud_relay_missing":
                roadmap.append({
                    "phase": "relay_stabilization",
                    "priority": 1,
                    "gap": g
                })

            if g == "executor_upgrade":
                roadmap.append({
                    "phase": "executor_upgrade",
                    "priority": 2,
                    "gap": g
                })

            if g == "vault_setup_needed":
                roadmap.append({
                    "phase": "vault_hardening",
                    "priority": 1,
                    "gap": g
                })

            if g == "pc_brain_hardening":
                roadmap.append({
                    "phase": "pc_brain_security",
                    "priority": 3,
                    "gap": g
                })

            if g == "memory_integration_needed":
                roadmap.append({
                    "phase": "memory_sync_evolution",
                    "priority": 2,
                    "gap": g
                })

        # Ensure only known phases are added and unique
        seen_phases = set()
        unique_roadmap = []
        for item in roadmap:
            if item["phase"] not in seen_phases:
                unique_roadmap.append(item)
                seen_phases.add(item["phase"])

        unique_roadmap.sort(key=lambda x: x["priority"])

        return unique_roadmap

roadmap_generator_service = RoadmapGeneratorService()
