from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from app.services.end_to_end_operational_drill_service import end_to_end_operational_drill_service
from app.services.install_run_readiness_service import install_run_readiness_service
from app.services.mobile_first_run_wizard_service import mobile_first_run_wizard_service
from app.services.request_worker_loop_service import request_worker_loop_service

ROOT = Path(".")


class FirstUsableReleaseService:
    """Practical first-use release guide for installing and using God Mode."""

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def _exists(self, path: str) -> bool:
        return (ROOT / path).exists()

    def _artifact_expectations(self) -> List[Dict[str, Any]]:
        return [
            {
                "id": "windows_exe",
                "label": "Windows EXE",
                "workflow": ".github/workflows/windows-exe-real-build.yml",
                "expected_use": "instalar/abrir God Mode no PC como cérebro principal",
                "required": True,
                "workflow_present": self._exists(".github/workflows/windows-exe-real-build.yml"),
            },
            {
                "id": "android_apk",
                "label": "Android APK",
                "workflow": ".github/workflows/android-real-build-progressive.yml",
                "expected_use": "abrir cockpit mobile/APK no telemóvel",
                "required": True,
                "workflow_present": self._exists(".github/workflows/android-real-build-progressive.yml"),
            },
            {
                "id": "universal_total_test",
                "label": "Universal Total Test",
                "workflow": ".github/workflows/universal-total-test.yml",
                "expected_use": "validar backend, rotas e integrações antes de usar",
                "required": True,
                "workflow_present": self._exists(".github/workflows/universal-total-test.yml"),
            },
        ]

    def _pc_steps(self) -> List[Dict[str, Any]]:
        return [
            {
                "step": 1,
                "title": "Instalar/abrir o God Mode no PC",
                "detail": "Usar o EXE gerado pelo workflow Windows ou o launcher local desktop/godmode_desktop_launcher.py.",
                "path": "desktop/godmode_desktop_launcher.py",
                "present": self._exists("desktop/godmode_desktop_launcher.py"),
            },
            {
                "step": 2,
                "title": "Confirmar backend local",
                "detail": "Abrir /health e /api/system/config no browser local.",
                "routes": ["/health", "/api/system/config"],
                "present": True,
            },
            {
                "step": 3,
                "title": "Abrir readiness",
                "detail": "Usar /app/install-readiness para ver se há blockers antes de operar.",
                "route": "/app/install-readiness",
                "present": True,
            },
            {
                "step": 4,
                "title": "Correr drill operacional",
                "detail": "Usar /app/e2e-operational-drill para provar ordem → job → worker → aprovação/resume.",
                "route": "/app/e2e-operational-drill",
                "present": True,
            },
        ]

    def _mobile_steps(self) -> List[Dict[str, Any]]:
        return [
            {
                "step": 1,
                "title": "Abrir APK/WebView",
                "detail": "Entrada única do APK: /app/apk-start.",
                "route": "/app/apk-start",
                "present": True,
            },
            {
                "step": 2,
                "title": "Validar first run",
                "detail": "Abrir /app/mobile-first-run e confirmar semáforo.",
                "route": "/app/mobile-first-run",
                "present": True,
            },
            {
                "step": 3,
                "title": "Usar chat principal",
                "detail": "Abrir /app/operator-chat-sync-cards e dar ordens em linguagem normal.",
                "route": "/app/operator-chat-sync-cards",
                "present": True,
            },
            {
                "step": 4,
                "title": "Aprovar quando necessário",
                "detail": "Quando o backend bloquear por OK/login/input, abrir /app/mobile-approval-cockpit-v2.",
                "route": "/app/mobile-approval-cockpit-v2",
                "present": True,
            },
        ]

    def _first_commands(self) -> List[Dict[str, Any]]:
        return [
            {
                "id": "money",
                "label": "Começar dinheiro",
                "text": "quero começar a ganhar dinheiro com o projeto mais rápido; faz o processo até precisares do meu OK",
                "expected_backend": "cria job money_flow, executa passos seguros e bloqueia em aprovação",
            },
            {
                "id": "audit",
                "label": "Auditoria operacional",
                "text": "audita o God Mode e diz o próximo blocker para ficar pronto a instalar e usar",
                "expected_backend": "cria job geral, prepara plano seguro e pede aprovação antes de alterações",
            },
            {
                "id": "offline",
                "label": "Teste offline",
                "text": "guarda esta ordem e continua no PC quando ele voltar online",
                "expected_backend": "offline buffer sincroniza, cria job no orquestrador e worker continua",
            },
            {
                "id": "provider",
                "label": "Provider externo",
                "text": "prepara uso de Gemini/ChatGPT provider e pára quando precisares do meu login manual",
                "expected_backend": "bloqueia em blocked_credentials sem guardar credenciais",
            },
        ]

    def build_release_plan(self) -> Dict[str, Any]:
        readiness = install_run_readiness_service.build_report()
        drill = end_to_end_operational_drill_service.latest_report()
        first_run = mobile_first_run_wizard_service.run_check()
        worker = request_worker_loop_service.get_status()
        artifacts = self._artifact_expectations()
        missing_artifact_workflows = [item for item in artifacts if item["required"] and not item["workflow_present"]]
        blockers: List[Dict[str, Any]] = []
        blockers.extend(readiness.get("blockers", []))
        blockers.extend(
            {"id": f"missing_workflow:{item['id']}", "label": item["label"], "detail": item["workflow"]}
            for item in missing_artifact_workflows
        )
        latest_drill_report = drill.get("report") if drill.get("ok") else None
        if not latest_drill_report:
            blockers.append({"id": "drill:not_run", "label": "E2E drill ainda não correu", "detail": "Abrir /app/e2e-operational-drill"})
        status = "green" if not blockers else "yellow"
        if readiness.get("status") == "red":
            status = "red"
        return {
            "ok": True,
            "mode": "first_usable_release_plan",
            "created_at": self._now(),
            "status": status,
            "release_name": "God Mode First Usable Release",
            "readiness": {
                "status": readiness.get("status"),
                "score": readiness.get("score"),
                "install_decision": readiness.get("install_decision"),
                "blocker_count": len(readiness.get("blockers", [])),
                "warning_count": len(readiness.get("warnings", [])),
            },
            "first_run": first_run.get("check", {}),
            "worker": worker,
            "latest_drill": latest_drill_report,
            "blockers": blockers,
            "artifacts": artifacts,
            "pc_steps": self._pc_steps(),
            "mobile_steps": self._mobile_steps(),
            "first_commands": self._first_commands(),
            "install_urls": {
                "readiness": "/app/install-readiness",
                "first_run": "/app/mobile-first-run",
                "apk_start": "/app/apk-start",
                "chat": "/app/operator-chat-sync-cards",
                "approvals": "/app/mobile-approval-cockpit-v2",
                "worker": "/app/request-worker",
                "offline": "/app/offline-buffer",
                "drill": "/app/e2e-operational-drill",
            },
        }

    def build_operator_guide(self) -> Dict[str, Any]:
        plan = self.build_release_plan()
        guide = {
            "title": "God Mode — primeira utilização",
            "status": plan["status"],
            "short_answer": self._short_answer(plan),
            "pc": plan["pc_steps"],
            "mobile": plan["mobile_steps"],
            "first_commands": plan["first_commands"],
            "when_blocked": [
                "Se pedir OK, abrir /app/mobile-approval-cockpit-v2.",
                "Se pedir login/provider, fazer login manual no provider. Não escrever credenciais no chat.",
                "Se o APK desligar, o job fica no backend. Ver /app/request-worker e /app/request-orchestrator.",
                "Se PC/telefone desconectar, usar /app/offline-buffer para sync/replay.",
            ],
        }
        return {"ok": True, "mode": "first_usable_release_operator_guide", "guide": guide, "plan": plan}

    def _short_answer(self, plan: Dict[str, Any]) -> str:
        if plan["status"] == "green":
            return "Sim: pronto para primeira instalação controlada e teste real pelo APK."
        if plan["status"] == "yellow":
            return "Quase: usável para teste controlado, mas ainda há blockers/avisos a resolver."
        return "Não: corrigir blockers antes de instalar/usar como operação real."

    def build_dashboard(self) -> Dict[str, Any]:
        plan = self.build_release_plan()
        return {
            "ok": True,
            "mode": "first_usable_release_dashboard",
            "plan": plan,
            "guide": self.build_operator_guide()["guide"],
            "buttons": [
                {"id": "readiness", "label": "Readiness", "route": "/app/install-readiness", "priority": "critical"},
                {"id": "drill", "label": "Correr drill", "route": "/app/e2e-operational-drill", "priority": "critical"},
                {"id": "apk_start", "label": "APK Start", "route": "/app/apk-start", "priority": "high"},
                {"id": "chat", "label": "Chat", "route": "/app/operator-chat-sync-cards", "priority": "high"},
                {"id": "worker", "label": "Worker", "route": "/app/request-worker", "priority": "medium"},
            ],
        }

    def get_status(self) -> Dict[str, Any]:
        plan = self.build_release_plan()
        return {
            "ok": True,
            "mode": "first_usable_release_status",
            "status": plan["status"],
            "release_name": plan["release_name"],
            "blocker_count": len(plan.get("blockers", [])),
            "readiness_status": plan["readiness"].get("status"),
        }

    def get_package(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "mode": "first_usable_release_package",
            "package": {
                "status": self.get_status(),
                "dashboard": self.build_dashboard(),
                "guide": self.build_operator_guide(),
            },
        }


first_usable_release_service = FirstUsableReleaseService()
