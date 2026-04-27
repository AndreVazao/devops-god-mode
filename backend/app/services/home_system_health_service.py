from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Callable, Dict, List


class HomeSystemHealthService:
    """One compact health snapshot for the God Mode Home."""

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def _safe(self, label: str, fn: Callable[[], Any]) -> Dict[str, Any]:
        try:
            value = fn()
            return value if isinstance(value, dict) else {"ok": True, "mode": label, "value": value}
        except Exception as exc:
            return {"ok": False, "mode": label, "error": exc.__class__.__name__, "detail": str(exc)[:240]}

    def _home(self):
        from app.services.god_mode_home_service import god_mode_home_service

        return god_mode_home_service

    def _ready(self):
        from app.services.ready_to_use_home_check_service import ready_to_use_home_check_service

        return ready_to_use_home_check_service

    def _install(self):
        from app.services.install_first_run_guide_service import install_first_run_guide_service

        return install_first_run_guide_service

    def _artifacts(self):
        from app.services.artifacts_center_service import artifacts_center_service

        return artifacts_center_service

    def _pc(self):
        from app.services.pc_autopilot_loop_service import pc_autopilot_loop_service

        return pc_autopilot_loop_service

    def _chat(self):
        from app.services.operator_chat_real_work_bridge_service import operator_chat_real_work_bridge_service

        return operator_chat_real_work_bridge_service

    def _priority(self):
        from app.services.operator_priority_service import operator_priority_service

        return operator_priority_service

    def build_snapshot(self, tenant_id: str = "owner-andre") -> Dict[str, Any]:
        home = self._safe("home", lambda: self._home().get_status(tenant_id=tenant_id))
        ready = self._safe("ready", lambda: self._ready().get_status(tenant_id=tenant_id))
        install = self._safe("install", lambda: self._install().get_status(tenant_id=tenant_id))
        artifacts = self._safe("artifacts", self._artifacts().get_status)
        pc = self._safe("pc", self._pc().get_status)
        chat = self._safe("chat", self._chat().get_status)
        priority = self._safe("priority", self._priority().get_status)
        signals = self._signals(home, ready, install, artifacts, pc, chat, priority)
        blockers = [item for item in signals if item["severity"] in {"critical", "warning"}]
        score = self._score(signals)
        return {
            "ok": True,
            "mode": "home_system_health_snapshot",
            "created_at": self._now(),
            "tenant_id": tenant_id,
            "health_score": score,
            "status": "healthy" if score >= 90 else ("attention" if score >= 70 else "blocked"),
            "traffic_light": self._traffic_light(score, blockers),
            "next_action": self._next_action(blockers, home, ready, install, artifacts, pc),
            "signals": signals,
            "blockers": blockers,
            "subsystems": {
                "home": home,
                "ready_to_use": ready,
                "install_first_run": install,
                "artifacts_center": artifacts,
                "pc_autopilot": pc,
                "chat_bridge": chat,
                "operator_priority": priority,
            },
        }

    def _signals(self, home: Dict[str, Any], ready: Dict[str, Any], install: Dict[str, Any], artifacts: Dict[str, Any], pc: Dict[str, Any], chat: Dict[str, Any], priority: Dict[str, Any]) -> List[Dict[str, Any]]:
        return [
            self._signal("home", "Home API", home.get("ok") is True, "critical", home.get("mode")),
            self._signal("ready_to_use", "Pronto para usar", ready.get("ok") is True and ready.get("readiness_score", 0) >= 75, "warning", f"{ready.get('readiness_score', 0)}%"),
            self._signal("install_first_run", "Guia de instalação", install.get("ok") is True and install.get("blocked_count", 0) == 0, "warning", f"{install.get('done_count', 0)} passos"),
            self._signal("artifacts", "APK/EXE", artifacts.get("ok") is True and artifacts.get("artifact_count", 0) >= 2, "critical", artifacts.get("status")),
            self._signal("pc_autopilot", "PC Autopilot", pc.get("ok") is True and pc.get("apk_disconnect_safe") is True, "warning", pc.get("status")),
            self._signal("chat", "Chat → backend", chat.get("ok") is True, "critical", chat.get("status")),
            self._signal("priority", "Prioridade operador", priority.get("ok") is True and priority.get("money_priority_enabled") is False, "critical", priority.get("active_project")),
        ]

    def _signal(self, signal_id: str, label: str, ok: bool, severity_if_bad: str, detail: Any) -> Dict[str, Any]:
        return {"id": signal_id, "label": label, "ok": bool(ok), "severity": "ok" if ok else severity_if_bad, "detail": detail}

    def _score(self, signals: List[Dict[str, Any]]) -> int:
        if not signals:
            return 0
        weights = {"critical": 25, "warning": 12}
        penalty = sum(weights.get(item["severity"], 0) for item in signals if not item["ok"])
        return max(0, min(100, 100 - penalty))

    def _traffic_light(self, score: int, blockers: List[Dict[str, Any]]) -> Dict[str, str]:
        if any(item["severity"] == "critical" for item in blockers):
            return {"color": "red", "label": "Bloqueado", "reason": "critical_health_blocker"}
        if blockers:
            return {"color": "yellow", "label": "Atenção", "reason": "health_warning"}
        if score >= 90:
            return {"color": "green", "label": "Saudável", "reason": "all_core_signals_ok"}
        return {"color": "blue", "label": "Operacional", "reason": "usable_with_notes"}

    def _next_action(self, blockers: List[Dict[str, Any]], home: Dict[str, Any], ready: Dict[str, Any], install: Dict[str, Any], artifacts: Dict[str, Any], pc: Dict[str, Any]) -> Dict[str, Any]:
        if blockers:
            first = blockers[0]
            mapping = {
                "home": {"label": "Abrir Home", "route": "/app/home"},
                "ready_to_use": {"label": "Ver pronto para usar", "endpoint": "/api/ready-to-use/checklist"},
                "install_first_run": {"label": "Ver guia de instalação", "endpoint": "/api/install-first-run/guide"},
                "artifacts": {"label": "Ver APK/EXE", "endpoint": "/api/artifacts-center/dashboard"},
                "pc_autopilot": {"label": "Ligar PC Autopilot", "endpoint": "/api/god-mode-home/start-autopilot"},
                "chat": {"label": "Abrir chat", "route": "/app/operator-chat-sync-cards"},
                "priority": {"label": "Ver prioridades", "route": "/app/operator-priority"},
            }
            action = mapping.get(first["id"], {"label": "Abrir Home", "route": "/app/home"})
            return {"kind": "resolve_blocker", "blocker": first, **action}
        if pc.get("status") == "disabled":
            return {"kind": "start", "label": "Ligar PC Autopilot", "endpoint": "/api/god-mode-home/start-autopilot"}
        return {"kind": "command", "label": "Dar próxima ordem no chat", "route": "/app/operator-chat-sync-cards"}

    def get_status(self, tenant_id: str = "owner-andre") -> Dict[str, Any]:
        snapshot = self.build_snapshot(tenant_id=tenant_id)
        return {
            "ok": True,
            "mode": "home_system_health_status",
            "status": snapshot["status"],
            "health_score": snapshot["health_score"],
            "traffic_light": snapshot["traffic_light"],
            "blocker_count": len(snapshot["blockers"]),
            "next_action": snapshot["next_action"],
        }

    def get_package(self, tenant_id: str = "owner-andre") -> Dict[str, Any]:
        return {"ok": True, "mode": "home_system_health_package", "package": {"status": self.get_status(tenant_id), "snapshot": self.build_snapshot(tenant_id)}}


home_system_health_service = HomeSystemHealthService()
