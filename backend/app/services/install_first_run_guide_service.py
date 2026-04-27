from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List


class InstallFirstRunGuideService:
    """Mobile-first install and first-run guide.

    The goal is to give the operator a no-command path from build artifact to
    a working PC + APK control loop.
    """

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def _ready(self):
        from app.services.ready_to_use_home_check_service import ready_to_use_home_check_service

        return ready_to_use_home_check_service

    def _home(self):
        from app.services.god_mode_home_service import god_mode_home_service

        return god_mode_home_service

    def build_guide(self, tenant_id: str = "owner-andre") -> Dict[str, Any]:
        readiness = self._ready().build_checklist(tenant_id=tenant_id)
        steps = self._steps(readiness)
        done_count = sum(1 for step in steps if step["status"] == "done")
        blocked_count = sum(1 for step in steps if step["status"] == "blocked")
        current = next((step for step in steps if step["status"] != "done"), steps[-1] if steps else None)
        return {
            "ok": True,
            "mode": "install_first_run_guide",
            "created_at": self._now(),
            "tenant_id": tenant_id,
            "readiness_score": readiness.get("readiness_score", 0),
            "status": "ready_to_start" if blocked_count == 0 else "needs_attention",
            "done_count": done_count,
            "blocked_count": blocked_count,
            "current_step": current,
            "steps": steps,
            "safe_operator_rules": [
                "Não escrever dados sensíveis no chat.",
                "Usar Aprovações quando o God Mode pedir OK.",
                "Manter data/, memory/, .env e backend/.env preservados.",
                "Preferir Home como entrada principal.",
            ],
            "primary_routes": [
                {"label": "Home", "route": "/app/home"},
                {"label": "Pronto para usar", "endpoint": "/api/ready-to-use/checklist"},
                {"label": "Pairing", "route": "/app/private-tunnel"},
                {"label": "PC Autopilot", "route": "/app/pc-autopilot"},
                {"label": "Aprovações", "route": "/app/mobile-approval-cockpit-v2"},
            ],
        }

    def _steps(self, readiness: Dict[str, Any]) -> List[Dict[str, Any]]:
        checks = {item["id"]: item for item in readiness.get("checks", [])}
        return [
            self._step(1, "Confirmar builds", "APK e EXE precisam estar verdes nos workflows.", checks.get("apk_workflow", {}).get("ok") and checks.get("exe_workflow", {}).get("ok"), "/api/ready-to-use/checklist"),
            self._step(2, "Instalar/abrir backend no PC", "Abrir o EXE ou backend local no PC e confirmar /health.", checks.get("home_backend_route", {}).get("ok"), "/health"),
            self._step(3, "Abrir APK", "O APK deve cair em /app/home depois de encontrar o PC.", checks.get("home_route", {}).get("ok"), "/app/home"),
            self._step(4, "Ligar APK ao PC", "Usar auto discovery, URL manual ou QR/deep link.", checks.get("home_route", {}).get("ok"), "/app/private-tunnel"),
            self._step(5, "Confirmar Home", "Ver semáforo, projeto ativo, Pronto para usar e próxima tarefa.", checks.get("home_backend_route", {}).get("ok"), "/app/home"),
            self._step(6, "Ligar PC Autopilot", "Permite continuar ciclos no PC mesmo com APK fechado.", checks.get("pc_autopilot", {}).get("ok"), "/app/pc-autopilot"),
            self._step(7, "Dar primeiro comando", "Exemplo: continua o God Mode até precisares do meu OK.", checks.get("chat_pipeline", {}).get("ok"), "/app/operator-chat-sync-cards"),
            self._step(8, "Responder aprovações", "Quando bloquear, abrir Aprovações e decidir.", checks.get("approval_route", {}).get("ok"), "/app/mobile-approval-cockpit-v2"),
        ]

    def _step(self, order: int, title: str, detail: str, ok: Any, route: str) -> Dict[str, Any]:
        is_ok = bool(ok)
        return {
            "order": order,
            "title": title,
            "detail": detail,
            "status": "done" if is_ok else "blocked",
            "route": route if route.startswith("/app/") or route == "/health" else None,
            "endpoint": route if route.startswith("/api/") else None,
        }

    def get_status(self, tenant_id: str = "owner-andre") -> Dict[str, Any]:
        guide = self.build_guide(tenant_id=tenant_id)
        return {
            "ok": True,
            "mode": "install_first_run_guide_status",
            "status": guide["status"],
            "readiness_score": guide["readiness_score"],
            "done_count": guide["done_count"],
            "blocked_count": guide["blocked_count"],
            "current_step": guide["current_step"],
        }

    def get_package(self, tenant_id: str = "owner-andre") -> Dict[str, Any]:
        return {"ok": True, "mode": "install_first_run_guide_package", "package": {"status": self.get_status(tenant_id), "guide": self.build_guide(tenant_id)}}


install_first_run_guide_service = InstallFirstRunGuideService()
