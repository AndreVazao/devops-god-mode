from typing import Any, Dict, List

from app.services.delivery_history_service import delivery_history_service


class FinalSummaryService:
    def get_summaries(self) -> Dict[str, Any]:
        histories = delivery_history_service.get_histories()["histories"]
        summaries: List[Dict[str, Any]] = []
        for history in histories:
            summaries.append(
                {
                    "final_summary_id": f"final_summary_{history['recovery_project_id']}",
                    "recovery_project_id": history["recovery_project_id"],
                    "summary_line_count": history["total_history_items"],
                    "primary_summary_label": "DevOps God Mode Mobile.apk ready_for_delivery",
                    "summary_status": "summary_ready",
                }
            )
        return {"ok": True, "mode": "final_summaries", "summaries": summaries}

    def get_summary_lines(self, recovery_project_id: str | None = None) -> Dict[str, Any]:
        records = delivery_history_service.get_history_records(recovery_project_id)["records"]
        lines: List[Dict[str, Any]] = []
        for index, record in enumerate(records, start=1):
            lines.append(
                {
                    "final_summary_line_id": f"final_summary_line_{index}_{record['recovery_project_id']}",
                    "recovery_project_id": record["recovery_project_id"],
                    "source_record_id": record["delivery_history_record_id"],
                    "summary_type": "primary_output" if index == 1 else "history_note",
                    "summary_label": record["record_label"],
                    "summary_state": "ready_for_delivery" if index == 1 else record["record_status"],
                }
            )
        return {"ok": True, "mode": "final_summary_lines", "lines": lines}

    def get_summary_package(self, recovery_project_id: str) -> Dict[str, Any]:
        summary = next(
            item for item in self.get_summaries()["summaries"] if item["recovery_project_id"] == recovery_project_id
        )
        package = {
            "summary": summary,
            "lines": self.get_summary_lines(recovery_project_id)["lines"],
            "mobile_compact": True,
            "package_status": summary["summary_status"],
        }
        return {"ok": True, "mode": "final_summary_package", "package": package}

    def get_next_summary_action(self) -> Dict[str, Any]:
        summaries = self.get_summaries()["summaries"]
        next_summary = summaries[0] if summaries else None
        return {
            "ok": True,
            "mode": "next_final_summary_action",
            "next_summary_action": {
                "final_summary_id": next_summary["final_summary_id"],
                "recovery_project_id": next_summary["recovery_project_id"],
                "action": "surface_final_project_summary",
                "summary_status": next_summary["summary_status"],
            }
            if next_summary
            else None,
        }


final_summary_service = FinalSummaryService()
