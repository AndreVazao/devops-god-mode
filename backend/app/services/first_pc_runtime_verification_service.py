from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from app.services.artifacts_center_service import artifacts_center_service
from app.services.first_real_install_launcher_service import first_real_install_launcher_service
from app.services.god_mode_global_state_service import god_mode_global_state_service
from app.services.ready_to_use_home_check_service import ready_to_use_home_check_service


class FirstPcRuntimeVerificationService:
    SERVICE_ID = "first_pc_runtime_verification"
    VERSION = "phase_198_v1"

    ESSENTIAL_ROUTES = [
        {"label": "Home", "route": "/app/home", "purpose": "cockpit principal"},
        {"label": "Trabalho Real", "route": "/app/real-work-fast-path", "purpose": "mapa real de projetos/repos/conversas"},
        {"label": "Repo Inventory", "route": "/app/github-repo-inventory-feed", "purpose": "alimentar scanner com repos"},
        {"label": "Repo Scanner", "route": "/app/repo-scanner-real-work-map", "purpose": "classificar repos por grupo/frente"},
        {"label": "Conversation Import", "route": "/app/conversation-source-import-feed", "purpose": "importar conversas/transcrições"},
        {"label": "Provider Launcher", "route": "/app/provider-browser-local-launcher", "purpose": "abrir provider e capturar resposta"},
        {"label": "Broadcast IA", "route": "/app/provider-broadcast-cockpit", "purpose": "preparar prompts multi-IA"},
        {"label": "Mobile Approval", "route": "/app/mobile-approval-cockpit-v2", "purpose": "cards e aprovações"},
    ]

    API_PROBES = [
        "/api/god-mode-home/dashboard",
        "/api/real-work-fast-path/package",
        "/api/github-repo-inventory-feed/package",
        "/api/repo-scanner-real-work-map/package",
        "/api/conversation-source-import-feed/package",
        "/api/provider-browser-local-launcher/package",
        "/api/provider-browser-proof-link/package",
        "/api/god-mode-global-state/package",
    ]

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def status(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "service": self.SERVICE_ID,
            "version": self.VERSION,
            "generated_at": self._now(),
            "pc_runtime_verification_ready": True,
            "canonical_home": "/app/home",
            "essential_route_count": len(self.ESSENTIAL_ROUTES),
            "api_probe_count": len(self.API_PROBES),
        }

    def first_run_guide(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "mode": "first_pc_run_operator_guide",
            "goal": "Abrir o God Mode no PC e executar o primeiro fluxo real sem confusão.",
            "pc_steps": [
                "Descarregar o artifact Windows EXE mais recente da GitHub Actions.",
                "Extrair o bundle se vier compactado.",
                "Executar GodModeDesktop.exe.",
                "Confirmar que abre /app/home ou abrir manualmente http://127.0.0.1:8000/app/home.",
                "Abrir /app/github-repo-inventory-feed e carregar seed/import manual dos repos.",
                "Abrir /app/repo-scanner-real-work-map e confirmar grupos/frentes.",
                "Abrir /app/conversation-source-import-feed e colar uma conversa curta com labels Oner:/Assistant:.",
                "Abrir /app/provider-browser-local-launcher e criar contrato para ChatGPT/Claude/Gemini.",
            ],
            "phone_steps": [
                "Usar o telemóvel para abrir o cockpit remoto quando o PC estiver online.",
                "Usar cards para confirmar dúvidas de repo/conversa/login.",
                "Dar ordens curtas ao God Mode pelo Home/Trabalho Real.",
            ],
            "first_real_flow": [
                "1. Importar inventário de repos.",
                "2. Scan/classificação de repos.",
                "3. Importar conversa.",
                "4. Criar provider launcher package.",
                "5. Colar captura/importar resposta.",
                "6. Rever ledger/cards.",
            ],
        }

    def runtime_checks(self) -> Dict[str, Any]:
        artifacts = self._safe_call(artifacts_center_service.dashboard)
        install = self._safe_call(first_real_install_launcher_service.get_package)
        ready = self._safe_call(ready_to_use_home_check_service.checklist)
        global_state = self._safe_call(god_mode_global_state_service.package)
        route_checks = [{"label": item["label"], "route": item["route"], "purpose": item["purpose"], "expected": True} for item in self.ESSENTIAL_ROUTES]
        api_checks = [{"endpoint": endpoint, "expected": True, "method": "GET/POST depending route"} for endpoint in self.API_PROBES]
        return {
            "ok": True,
            "mode": "first_pc_runtime_checks",
            "generated_at": self._now(),
            "route_checks": route_checks,
            "api_checks": api_checks,
            "artifacts": artifacts,
            "install": install,
            "ready_to_use": ready,
            "global_state": global_state,
            "manual_verification_required": [
                "Confirmar visualmente que /app/home abre no PC.",
                "Confirmar que o browser local consegue abrir provider externo.",
                "Confirmar que nenhuma password/token/cookie é colada em importadores.",
            ],
        }

    def package(self) -> Dict[str, Any]:
        return {
            "status": self.status(),
            "guide": self.first_run_guide(),
            "runtime_checks": self.runtime_checks(),
        }

    def _safe_call(self, fn) -> Dict[str, Any]:
        try:
            result = fn()
            return result if isinstance(result, dict) else {"ok": True, "value": result}
        except Exception as exc:  # pragma: no cover - runtime diagnostic safety
            return {"ok": False, "error": str(exc), "function": getattr(fn, "__name__", "unknown")}


first_pc_runtime_verification_service = FirstPcRuntimeVerificationService()
