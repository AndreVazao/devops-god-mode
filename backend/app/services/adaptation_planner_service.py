from typing import Any, Dict, List

from app.services.script_extraction_reuse_service import script_extraction_reuse_service


class AdaptationPlannerService:
    def _adaptation_plans(self) -> List[Dict[str, Any]]:
        scripts = script_extraction_reuse_service.get_extracted_scripts()["scripts"]
        return [
            {
                "adaptation_id": "adapt_runtime_supervisor_to_future_project",
                "source_script_id": scripts[2]["script_id"],
                "target_project": "future_project",
                "compatibility_score": 0.91,
                "required_changes": [
                    "rename runtime endpoints",
                    "adjust project-specific labels",
                    "update target paths",
                ],
                "adaptation_steps": [
                    "select source script",
                    "map target project context",
                    "rename project-specific symbols",
                    "validate route fit",
                ],
                "adaptation_status": "planned",
            },
            {
                "adaptation_id": "adapt_baribudos_backend_to_future_project",
                "source_script_id": scripts[0]["script_id"],
                "target_project": "future_project",
                "compatibility_score": 0.84,
                "required_changes": [
                    "replace project-specific naming",
                    "adapt service imports",
                ],
                "adaptation_steps": [
                    "inspect source boundaries",
                    "replace project-specific symbols",
                    "validate startup integration",
                ],
                "adaptation_status": "planned",
            },
        ]

    def get_adaptation_plans(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "mode": "adaptation_plans",
            "adaptation_plans": self._adaptation_plans(),
        }

    def get_target_fit(self) -> Dict[str, Any]:
        plans = self._adaptation_plans()
        return {
            "ok": True,
            "mode": "target_fit_summaries",
            "target_fits": [
                {
                    "target_fit_id": "fit_future_project_backend",
                    "target_project": "future_project",
                    "candidate_scripts": [plan["source_script_id"] for plan in plans],
                    "fit_summary": "Strong backend reuse candidate set with moderate rename effort.",
                    "blockers": ["target route naming not finalized"],
                    "target_fit_status": "target_fit_ready",
                }
            ],
        }

    def get_best_plans(self) -> Dict[str, Any]:
        plans = sorted(
            self._adaptation_plans(),
            key=lambda item: item["compatibility_score"],
            reverse=True,
        )
        return {
            "ok": True,
            "mode": "best_adaptation_plans",
            "best_plans": plans,
        }

    def get_blockers(self) -> Dict[str, Any]:
        plans = self._adaptation_plans()
        blockers = []
        for plan in plans:
            blockers.append(
                {
                    "adaptation_id": plan["adaptation_id"],
                    "target_project": plan["target_project"],
                    "blockers": [
                        "target naming confirmation pending"
                        if plan["compatibility_score"] > 0.9
                        else "import adaptation review needed"
                    ],
                }
            )
        return {"ok": True, "mode": "adaptation_blockers", "blockers": blockers}


adaptation_planner_service = AdaptationPlannerService()
