from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List
from uuid import uuid4

from app.services.github_approved_actions_executor_service import github_approved_actions_executor_service
from app.services.local_knowledge_rag_decision_service import local_knowledge_rag_decision_service
from app.services.memory_sync_runtime_service import memory_sync_runtime_service
from app.services.pipeline_persistence_executor_service import pipeline_persistence_executor_service
from app.services.playbook_templates_library_service import playbook_templates_library_service
from app.services.provider_outcome_learning_service import provider_outcome_learning_service


class HomeAppControlSurfaceService:
    """Unified control surface for PC/APK home screens.

    Phase 172 does not execute destructive actions. It exposes real buttons,
    groups, quick payloads and module health so desktop/mobile shells can render
    a working God Mode cockpit without hardcoding every endpoint.
    """

    SERVICE_ID = "home_app_control_surface"
    VERSION = "phase_172_v1"

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def status(self) -> Dict[str, Any]:
        modules = self.modules()
        return {
            "ok": True,
            "service": self.SERVICE_ID,
            "version": self.VERSION,
            "created_at": self._now(),
            "module_count": len(modules),
            "button_count": sum(len(module.get("buttons", [])) for module in modules),
            "dangerous_actions_exposed": False,
            "owner_approval_required_for_high_risk": True,
            "surface_targets": ["pc_desktop", "android_apk", "webview", "backend_api"],
        }

    def policy(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "service": self.SERVICE_ID,
            "rules": self.rules(),
            "risk_levels": {
                "safe": "read/status/preview/dry-run only",
                "low": "local non-destructive action",
                "approval_required": "requires explicit Oner approval or phrase/gate",
                "blocked_from_home": "merge/release/delete/payment/license/credential changes are not exposed from Home",
            },
            "render_contract": {
                "button_fields": ["id", "label", "description", "method", "endpoint", "risk", "requires_confirmation", "default_payload"],
                "traffic_light": ["green", "yellow", "red"],
                "layout": "module_cards_with_primary_buttons",
            },
        }

    def rules(self) -> List[str]:
        return [
            "Home/App mostra botões reais para módulos já implementados.",
            "Ações perigosas não são executadas diretamente pela Home/App.",
            "Approved GitHub Actions continua dependente da frase de aprovação e PR/checks.",
            "Memory Sync real mantém dry-run por defeito.",
            "Local RAG e Provider Learning são safe/read/decision por defeito.",
            "Low-risk executor só executa passos classificados como seguros.",
            "PC/APK deve renderizar esta superfície via `/api/home-control-surface/package`.",
        ]

    def modules(self) -> List[Dict[str, Any]]:
        return [
            self._playbooks_module(),
            self._pipelines_module(),
            self._memory_sync_module(),
            self._github_actions_module(),
            self._local_rag_module(),
            self._provider_learning_module(),
            self._history_module(),
        ]

    def panel(self) -> Dict[str, Any]:
        modules = self.modules()
        return {
            **self.status(),
            "headline": "God Mode Home/App Control Surface",
            "description": "Superfície única para PC/APK com botões reais para templates, pipelines, memory sync, GitHub approved actions, Local RAG e provider learning.",
            "traffic_light": self._traffic_light(modules),
            "modules": modules,
            "quick_start": self.quick_start(),
        }

    def quick_start(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "service": self.SERVICE_ID,
            "recommended_flow": [
                "1. Abrir Playbook Templates e escolher receita.",
                "2. Criar/guardar pipeline quando aplicável.",
                "3. Usar Local RAG para confirmar reuse-first antes de código novo.",
                "4. Usar Low-Risk Executor para passos seguros.",
                "5. Usar GitHub Approved Actions só com plano aprovado e PR.",
                "6. Após merge, usar Memory Sync Runtime para atualizar AndreOS memory.",
                "7. Registar Provider Outcome quando IA externa/local resolver uma tarefa.",
            ],
            "safe_default_buttons": [
                "playbook_templates_panel",
                "pipeline_store_status",
                "memory_sync_policy",
                "github_approved_policy",
                "local_rag_decision",
                "provider_learning_scorecard",
            ],
        }

    def button_manifest(self) -> Dict[str, Any]:
        buttons = []
        for module in self.modules():
            for button in module.get("buttons", []):
                buttons.append({**button, "module_id": module["id"], "module_label": module["label"]})
        return {
            "ok": True,
            "service": self.SERVICE_ID,
            "created_at": self._now(),
            "button_count": len(buttons),
            "buttons": buttons,
        }

    def mobile_shell_manifest(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "service": self.SERVICE_ID,
            "target": "android_apk_webview",
            "title": "God Mode",
            "default_route": "/api/home-control-surface/package",
            "refresh_seconds": 10,
            "cards": [
                {"id": module["id"], "title": module["label"], "traffic_light": module["traffic_light"], "endpoint": module["panel_endpoint"]}
                for module in self.modules()
            ],
            "blocked_from_mobile": ["merge", "release", "delete", "payment", "license", "credential_change"],
        }

    def desktop_shell_manifest(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "service": self.SERVICE_ID,
            "target": "pc_desktop_launcher",
            "title": "DevOps God Mode Control Surface",
            "default_endpoint": "/api/home-control-surface/package",
            "window": {"width": 1280, "height": 820, "theme": "dark", "auto_start_backend": True},
            "panels": [
                {"id": module["id"], "label": module["label"], "endpoint": module["panel_endpoint"], "buttons": len(module.get("buttons", []))}
                for module in self.modules()
            ],
        }

    def module_detail(self, module_id: str) -> Dict[str, Any]:
        for module in self.modules():
            if module["id"] == module_id:
                return {"ok": True, "service": self.SERVICE_ID, "module": module}
        return {"ok": False, "service": self.SERVICE_ID, "error": "module_not_found", "module_id": module_id}

    def package(self) -> Dict[str, Any]:
        return {
            "status": self.status(),
            "policy": self.policy(),
            "panel": self.panel(),
            "buttons": self.button_manifest(),
            "mobile_shell": self.mobile_shell_manifest(),
            "desktop_shell": self.desktop_shell_manifest(),
        }

    def _playbooks_module(self) -> Dict[str, Any]:
        status = self._safe_call(playbook_templates_library_service.status)
        return self._module(
            module_id="playbook_templates",
            label="Playbook Templates",
            description="Receitas reutilizáveis para criar pipelines reais sem depender de conversa longa.",
            panel_endpoint="/api/playbook-templates/panel",
            status=status,
            buttons=[
                self._button("playbook_templates_panel", "Abrir templates", "GET", "/api/playbook-templates/panel", "safe"),
                self._button("playbook_templates_list", "Listar templates", "GET", "/api/playbook-templates/templates", "safe"),
                self._button("playbook_templates_package", "Pacote templates", "GET", "/api/playbook-templates/package", "safe"),
            ],
        )

    def _pipelines_module(self) -> Dict[str, Any]:
        status = self._safe_call(pipeline_persistence_executor_service.status)
        return self._module(
            module_id="pipeline_store_low_risk",
            label="Pipelines + Low-Risk Executor",
            description="Guardar pipelines e executar apenas passos seguros classificados como low-risk.",
            panel_endpoint="/api/pipeline-store/panel",
            status=status,
            buttons=[
                self._button("pipeline_store_panel", "Abrir pipelines", "GET", "/api/pipeline-store/panel", "safe"),
                self._button("pipeline_store_status", "Estado pipeline store", "GET", "/api/pipeline-store/status", "safe"),
                self._button("pipeline_low_risk_latest", "Últimos runs", "GET", "/api/pipeline-store/latest", "safe"),
            ],
        )

    def _memory_sync_module(self) -> Dict[str, Any]:
        status = self._safe_call(memory_sync_runtime_service.status)
        return self._module(
            module_id="memory_sync_runtime",
            label="Memory Sync Runtime",
            description="Atualizar AndreOS GitHub memory e preparar notas Obsidian/local após fases merged.",
            panel_endpoint="/api/memory-sync-runtime/panel",
            status=status,
            buttons=[
                self._button("memory_sync_panel", "Abrir memory sync", "GET", "/api/memory-sync-runtime/panel", "safe"),
                self._button("memory_sync_policy", "Política memory sync", "GET", "/api/memory-sync-runtime/policy", "safe"),
                self._button(
                    "memory_sync_dry_run",
                    "Sync dry-run",
                    "POST",
                    "/api/memory-sync-runtime/sync-stable",
                    "approval_required",
                    requires_confirmation=True,
                    default_payload={"package_id": "<package_id>", "dry_run": True, "memory_repo": "AndreVazao/andreos-memory"},
                ),
            ],
        )

    def _github_actions_module(self) -> Dict[str, Any]:
        status = self._safe_call(github_approved_actions_executor_service.status)
        return self._module(
            module_id="github_approved_actions",
            label="GitHub Approved Actions",
            description="Executar patches GitHub aprovados: branch, ficheiros, commits e PR; sem merge/release automático.",
            panel_endpoint="/api/github-approved-actions/panel",
            status=status,
            buttons=[
                self._button("github_approved_panel", "Abrir executor GitHub", "GET", "/api/github-approved-actions/panel", "safe"),
                self._button("github_approved_policy", "Política GitHub", "GET", "/api/github-approved-actions/policy", "safe"),
                self._button(
                    "github_approved_execute_dry_run",
                    "Executar dry-run aprovado",
                    "POST",
                    "/api/github-approved-actions/execute",
                    "approval_required",
                    requires_confirmation=True,
                    default_payload={"plan_id": "<plan_id>", "approval_phrase": "APPLY REPO PATCH", "dry_run": True},
                ),
            ],
        )

    def _local_rag_module(self) -> Dict[str, Any]:
        status = self._safe_call(local_knowledge_rag_decision_service.status)
        return self._module(
            module_id="local_knowledge_rag",
            label="Local Knowledge/RAG",
            description="Pesquisar memória/docs/código local antes de criar código novo; regra reuse-first.",
            panel_endpoint="/api/local-knowledge-rag/panel",
            status=status,
            buttons=[
                self._button("local_rag_panel", "Abrir Local RAG", "GET", "/api/local-knowledge-rag/panel", "safe"),
                self._button("local_rag_build_index", "Construir índice", "POST", "/api/local-knowledge-rag/build-index", "low", default_payload={"project_name": "GOD_MODE", "max_items": 300}),
                self._button("local_rag_decision", "Decisão reuse-first", "POST", "/api/local-knowledge-rag/decision", "safe", default_payload={"goal": "<objetivo>", "project_name": "GOD_MODE", "limit": 10}),
            ],
        )

    def _provider_learning_module(self) -> Dict[str, Any]:
        status = self._safe_call(provider_outcome_learning_service.status)
        return self._module(
            module_id="provider_outcome_learning",
            label="Provider Outcome Learning",
            description="Scorecards e hints para melhorar escolha de provider IA sem contornar segurança.",
            panel_endpoint="/api/provider-outcome-learning/panel",
            status=status,
            buttons=[
                self._button("provider_learning_panel", "Abrir provider learning", "GET", "/api/provider-outcome-learning/panel", "safe"),
                self._button("provider_learning_scorecard", "Gerar scorecard", "POST", "/api/provider-outcome-learning/scorecard", "safe", default_payload={"provider_id": None, "task_tag": None}),
                self._button("provider_learning_simulate", "Simular rota aprendida", "POST", "/api/provider-outcome-learning/simulate-route", "safe", default_payload={"goal": "<objetivo>", "task_tags": ["code_generation"], "needs_code": True}),
            ],
        )

    def _history_module(self) -> Dict[str, Any]:
        return self._module(
            module_id="history_and_audit",
            label="Histórico + Auditoria",
            description="Ponto de acesso a latest/package de módulos e memória de última sessão.",
            panel_endpoint="/api/home-control-surface/latest",
            status={"ok": True, "status": "history_surface_ready"},
            buttons=[
                self._button("home_latest", "Último estado Home", "GET", "/api/home-control-surface/latest", "safe"),
                self._button("home_buttons", "Manifesto de botões", "GET", "/api/home-control-surface/buttons", "safe"),
                self._button("home_package", "Pacote Home/App", "GET", "/api/home-control-surface/package", "safe"),
            ],
        )

    def _module(self, module_id: str, label: str, description: str, panel_endpoint: str, status: Dict[str, Any], buttons: List[Dict[str, Any]]) -> Dict[str, Any]:
        return {
            "id": module_id,
            "label": label,
            "description": description,
            "panel_endpoint": panel_endpoint,
            "traffic_light": "green" if status.get("ok") else "yellow",
            "status": status,
            "buttons": buttons,
        }

    def _button(
        self,
        button_id: str,
        label: str,
        method: str,
        endpoint: str,
        risk: str,
        description: str = "",
        requires_confirmation: bool = False,
        default_payload: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        return {
            "id": button_id,
            "label": label,
            "description": description or label,
            "method": method,
            "endpoint": endpoint,
            "risk": risk,
            "requires_confirmation": requires_confirmation or risk == "approval_required",
            "default_payload": default_payload or {},
            "button_instance_id": f"home-button-{uuid4().hex[:8]}",
        }

    def _safe_call(self, fn: Any) -> Dict[str, Any]:
        try:
            result = fn()
            return result if isinstance(result, dict) else {"ok": True, "value": result}
        except Exception as exc:
            return {"ok": False, "error": exc.__class__.__name__, "detail": str(exc)[:200]}

    def _traffic_light(self, modules: List[Dict[str, Any]]) -> str:
        if any(module.get("traffic_light") == "red" for module in modules):
            return "red"
        if any(module.get("traffic_light") == "yellow" for module in modules):
            return "yellow"
        return "green"

    def latest(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "service": self.SERVICE_ID,
            "created_at": self._now(),
            "panel_traffic_light": self.panel().get("traffic_light"),
            "quick_start": self.quick_start(),
            "button_count": self.status().get("button_count"),
        }


home_app_control_surface_service = HomeAppControlSurfaceService()
