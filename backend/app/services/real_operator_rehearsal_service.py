from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from app.services.andreos_memory_audit_service import andreos_memory_audit_service
from app.services.artifacts_center_service import artifacts_center_service
from app.services.daily_command_router_service import daily_command_router_service
from app.services.god_mode_home_service import god_mode_home_service
from app.services.mobile_approval_cockpit_v2_service import mobile_approval_cockpit_v2_service
from app.services.operator_chat_real_work_bridge_service import operator_chat_real_work_bridge_service
from app.services.operator_priority_service import operator_priority_service


class RealOperatorRehearsalService:
    """End-to-end rehearsal for the operator flow.

    This does not require the physical PC or Android device. It validates the
    backend chain that the APK will call: Home -> easy command/router -> chat
    bridge -> real work/autopilot -> feedback -> approvals/memory/artifacts.
    """

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def run(self, tenant_id: str = "owner-andre", requested_project: str = "GOD_MODE") -> Dict[str, Any]:
        operator_priority_service.set_order(
            [requested_project, "PROVENTIL", "BARIBUDOS_STUDIO", "BOT_FACTORY"],
            active_project=requested_project,
            note="real operator rehearsal priority order",
        )
        home_before = god_mode_home_service.build_dashboard(tenant_id=tenant_id)
        route_result = daily_command_router_service.route(
            command_id="continue_active_project",
            tenant_id=tenant_id,
            requested_project=requested_project,
        )
        chat_latest = operator_chat_real_work_bridge_service.latest()
        approvals = mobile_approval_cockpit_v2_service.list_cards(
            tenant_id=tenant_id,
            status="pending_approval",
            limit=20,
        )
        memory = andreos_memory_audit_service.build_audit(run_rehearsal=True)
        artifacts = artifacts_center_service.build_dashboard()
        home_after = god_mode_home_service.build_dashboard(tenant_id=tenant_id)
        build_probe = self._build_probe()
        checks = self._checks(
            requested_project=requested_project,
            home_before=home_before,
            route_result=route_result,
            chat_latest=chat_latest,
            approvals=approvals,
            memory=memory,
            artifacts=artifacts,
            home_after=home_after,
            build_probe=build_probe,
        )
        failed = [check for check in checks if not check["ok"]]
        score = round((sum(1 for check in checks if check["ok"]) / len(checks)) * 100) if checks else 0
        return {
            "ok": True,
            "mode": "real_operator_rehearsal",
            "created_at": self._now(),
            "tenant_id": tenant_id,
            "requested_project": requested_project,
            "status": "ready" if not failed else ("attention" if score >= 75 else "blocked"),
            "score": score,
            "checks": checks,
            "failed_checks": failed,
            "flow": {
                "home_before": self._home_summary(home_before),
                "route_result": self._route_summary(route_result),
                "chat_latest": chat_latest.get("report"),
                "approval_count": approvals.get("card_count", 0),
                "memory_status": {"status": memory.get("status"), "score": memory.get("score")},
                "artifacts_status": {"status": artifacts.get("status"), "artifact_count": artifacts.get("artifact_count")},
                "home_after": self._home_summary(home_after),
                "build_probe": build_probe,
            },
            "operator_next": self._operator_next(failed, route_result),
        }

    def _build_probe(self) -> Dict[str, Any]:
        checks = []
        workflow_specs = [
            (
                ".github/workflows/android-real-build-progressive.yml",
                "Android APK workflow",
                ["gradle --no-daemon :app:assembleDebug", "GodModeMobile-debug.apk", "real_webview_shell_apk", "apk.stat().st_size > 1024"],
            ),
            (
                ".github/workflows/windows-exe-real-build.yml",
                "Windows EXE workflow",
                ["upload-artifact", "GodMode.exe", "pyinstaller"],
            ),
        ]
        for path, label, positive_markers in workflow_specs:
            target = Path(path)
            text = target.read_text(encoding="utf-8") if target.exists() else ""
            lower = text.lower()
            harmful_placeholder = any(marker in lower for marker in [
                "echo placeholder",
                "dummy artifact",
                "placeholder artifact",
                "fake apk",
                "fake exe",
            ])
            checks.append({
                "label": label,
                "path": path,
                "exists": target.exists(),
                "mentions_upload_artifact": "upload-artifact" in text,
                "positive_markers_present": all(marker.lower() in lower for marker in positive_markers),
                "mentions_placeholder": harmful_placeholder,
                "size_bytes": target.stat().st_size if target.exists() else 0,
            })
        return {
            "ok": all(
                item["exists"]
                and item["mentions_upload_artifact"]
                and item["positive_markers_present"]
                and not item["mentions_placeholder"]
                for item in checks
            ),
            "checks": checks,
            "note": "CI also validates produced artifact files in the canonical APK/EXE workflows.",
        }

    def _checks(
        self,
        requested_project: str,
        home_before: Dict[str, Any],
        route_result: Dict[str, Any],
        chat_latest: Dict[str, Any],
        approvals: Dict[str, Any],
        memory: Dict[str, Any],
        artifacts: Dict[str, Any],
        home_after: Dict[str, Any],
        build_probe: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        report = route_result.get("result", {}).get("report", {}) if isinstance(route_result, dict) else {}
        latest_report = chat_latest.get("report") or {}
        return [
            self._check("home_ready", "Home respondeu antes do ensaio", home_before.get("ok") is True, home_before.get("operator_message")),
            self._check("router_received_order", "Daily router recebeu ordem", route_result.get("ok") is True, route_result.get("command_id")),
            self._check("project_resolved", "Projeto correto foi resolvido", route_result.get("project") == requested_project or report.get("resolved_project_id") == requested_project, report.get("resolved_project_id")),
            self._check("chat_bridge_job", "Chat bridge criou job real", bool(report.get("job_id")), report.get("job_id")),
            self._check("autopilot_feedback", "Autopilot devolveu feedback", "autopilot_stop_reason" in report, report.get("autopilot_stop_reason")),
            self._check("latest_report", "Último relatório ficou guardado", latest_report.get("job_id") == report.get("job_id"), latest_report.get("job_id")),
            self._check("approvals_visible", "Aprovações consultáveis", approvals.get("ok") is True, approvals.get("card_count", 0)),
            self._check("memory_ready", "AndreOS memory passou ensaio", memory.get("status") == "ready" and memory.get("score") == 100, memory.get("score")),
            self._check("artifacts_ready", "Artifacts Center aponta para APK/EXE", artifacts.get("status") == "ready" and artifacts.get("artifact_count") == 2, artifacts.get("artifact_count")),
            self._check("home_after", "Home continua funcional depois do ensaio", home_after.get("ok") is True, home_after.get("operator_message")),
            self._check("build_workflows_real", "Workflows APK/EXE não parecem placeholders", build_probe.get("ok") is True, build_probe),
        ]

    def _check(self, check_id: str, label: str, ok: bool, detail: Any = "") -> Dict[str, Any]:
        return {"id": check_id, "label": label, "ok": bool(ok), "detail": detail}

    def _home_summary(self, home: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "ok": home.get("ok"),
            "active_project": home.get("active_project"),
            "traffic_light": home.get("traffic_light"),
            "next_task": home.get("next_task"),
            "operator_message": home.get("operator_message"),
        }

    def _route_summary(self, route_result: Dict[str, Any]) -> Dict[str, Any]:
        report = route_result.get("result", {}).get("report", {}) if isinstance(route_result, dict) else {}
        return {
            "ok": route_result.get("ok"),
            "command_id": route_result.get("command_id"),
            "project": route_result.get("project"),
            "message": route_result.get("message"),
            "job_id": report.get("job_id"),
            "job_status": report.get("job_status"),
            "autopilot_stop_reason": report.get("autopilot_stop_reason"),
            "operator_next": route_result.get("operator_next"),
        }

    def _operator_next(self, failed: List[Dict[str, Any]], route_result: Dict[str, Any]) -> Dict[str, Any]:
        if failed:
            return {"label": f"Corrigir: {failed[0]['label']}", "endpoint": "/api/real-operator-rehearsal/run"}
        operator_next = route_result.get("operator_next") if isinstance(route_result, dict) else None
        if operator_next:
            return operator_next
        return {"label": "Abrir Home", "route": "/app/home"}

    def get_status(self) -> Dict[str, Any]:
        rehearsal = self.run()
        return {
            "ok": True,
            "mode": "real_operator_rehearsal_status",
            "status": rehearsal["status"],
            "score": rehearsal["score"],
            "failed_count": len(rehearsal["failed_checks"]),
            "operator_next": rehearsal["operator_next"],
        }

    def get_package(self) -> Dict[str, Any]:
        return {"ok": True, "mode": "real_operator_rehearsal_package", "package": {"status": self.get_status(), "rehearsal": self.run()}}


real_operator_rehearsal_service = RealOperatorRehearsalService()
