from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List


class SmolGodModeReferenceAdapterService:
    """Extract useful ideas from smol-ai/GodMode as native God Mode cockpit patterns.

    smol-ai/GodMode is useful as a UX/reference project: a dedicated multi-AI
    chat browser with full webapps, panes, provider toggles, prompt broadcast and
    prompt critic. It is not a backend/orchestration replacement for Andre's
    God Mode.
    """

    SERVICE_ID = "smol_godmode_reference_adapter"
    VERSION = "phase_189_v1"

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def status(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "service": self.SERVICE_ID,
            "version": self.VERSION,
            "generated_at": self._now(),
            "source_repo": "smol-ai/GodMode",
            "source_role": "ux_reference_not_core_dependency",
            "native_first": True,
            "dependency_added": False,
            "helps_god_mode": True,
            "package_endpoint": "/api/smol-godmode-reference-adapter/package",
        }

    def extracted_patterns(self) -> Dict[str, Any]:
        patterns: List[Dict[str, Any]] = [
            {
                "id": "dedicated_multi_ai_browser",
                "source_feature": "Dedicated chat browser for full AI webapps",
                "god_mode_native_target": "provider cockpit / browser provider execution hub",
                "value": "O God Mode deve conseguir abrir e controlar várias IAs como webapps completas quando API não chega.",
                "implementation_rule": "Use as UX reference; implement natively around existing PC brain + mobile cockpit.",
                "priority": "critical",
            },
            {
                "id": "prompt_broadcast",
                "source_feature": "Input at bottom submitted to all enabled webapps simultaneously",
                "god_mode_native_target": "provider prompt broadcast planner",
                "value": "Enviar o mesmo pedido a ChatGPT/Claude/Gemini/Perplexity/local para comparar respostas e captar scripts.",
                "implementation_rule": "Broadcast must create ledger entries and separate operator request from AI responses.",
                "priority": "critical",
            },
            {
                "id": "full_webapp_over_api_when_needed",
                "source_feature": "Use webapps to access features not exposed via API",
                "god_mode_native_target": "external AI browser worker + provider conversation proof",
                "value": "Mantém acesso a uploads, ferramentas multimodais, code interpreter e features novas sem esperar APIs.",
                "implementation_rule": "Never bypass provider terms or store credentials; use local browser/session approved by operator.",
                "priority": "high",
            },
            {
                "id": "provider_toggle_and_saved_layout",
                "source_feature": "Enable/disable providers and save pane choices",
                "god_mode_native_target": "mobile/PC cockpit provider pane registry",
                "value": "O Oner escolhe quais IAs entram numa missão e o PC guarda layout/preferências.",
                "implementation_rule": "Provider toggles feed AI Provider Router and Provider Outcome Learning.",
                "priority": "high",
            },
            {
                "id": "resizable_reorderable_panes",
                "source_feature": "Pane resizing/reordering/popout",
                "god_mode_native_target": "visible cockpit page layout model",
                "value": "Ajuda a comparar respostas lado a lado e ver qual IA acertou melhor.",
                "implementation_rule": "Start as backend manifest/cards; frontend can render panes later.",
                "priority": "normal",
            },
            {
                "id": "keyboard_quick_open",
                "source_feature": "Quick open and submit shortcuts",
                "god_mode_native_target": "PC cockpit shortcuts + mobile quick actions",
                "value": "No PC, atalhos aceleram trabalho. No telemóvel, botões rápidos equivalentes.",
                "implementation_rule": "Shortcuts must only trigger low-risk actions unless approval gate is satisfied.",
                "priority": "normal",
            },
            {
                "id": "prompt_critic",
                "source_feature": "PromptCritic for prompt improvement",
                "god_mode_native_target": "request orchestrator + conversation requirement ledger",
                "value": "Antes de enviar a várias IAs, melhorar pedido mantendo intenção original do Oner.",
                "implementation_rule": "Prompt critic cannot change intent silently; must preserve original request and log revised prompt.",
                "priority": "high",
            },
            {
                "id": "local_model_webui_support",
                "source_feature": "Oobabooga/local model URL support",
                "god_mode_native_target": "ollama/local_ai_adapter/local provider registry",
                "value": "Permite usar local LLM como mais um provider quando PC tiver recursos.",
                "implementation_rule": "Prefer Ollama/local adapter already in God Mode; add generic local web provider later.",
                "priority": "normal",
            },
        ]
        return {"ok": True, "pattern_count": len(patterns), "patterns": patterns}

    def capability_fit(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "fit": {
                "good_for": [
                    "multi-AI cockpit UX",
                    "webapp-based provider access",
                    "prompt broadcast",
                    "provider panes/toggles",
                    "prompt improvement before broadcast",
                    "side-by-side answer comparison",
                ],
                "not_good_for": [
                    "backend orchestration",
                    "GitHub PR automation",
                    "local encrypted vault",
                    "deployment gates",
                    "project memory architecture",
                    "real install/build pipeline",
                ],
                "verdict": "Adopt UX patterns, not architecture. God Mode remains PC brain + mobile cockpit + FastAPI orchestration.",
            },
        }

    def provider_pane_manifest(self) -> Dict[str, Any]:
        providers = [
            {"id": "chatgpt", "label": "ChatGPT", "kind": "full_webapp", "default_enabled": True, "ledger_role": "ai_response_source"},
            {"id": "claude", "label": "Claude", "kind": "full_webapp", "default_enabled": True, "ledger_role": "ai_response_source"},
            {"id": "gemini", "label": "Gemini", "kind": "full_webapp", "default_enabled": True, "ledger_role": "ai_response_source"},
            {"id": "perplexity", "label": "Perplexity", "kind": "full_webapp", "default_enabled": True, "ledger_role": "research_response_source"},
            {"id": "bing_copilot", "label": "Bing/Copilot", "kind": "full_webapp", "default_enabled": False, "ledger_role": "ai_response_source"},
            {"id": "openrouter", "label": "OpenRouter", "kind": "api_or_webapp", "default_enabled": False, "ledger_role": "model_gateway"},
            {"id": "local_ollama", "label": "Local Ollama", "kind": "local_api", "default_enabled": True, "ledger_role": "local_ai_response_source"},
            {"id": "local_webui", "label": "Local WebUI", "kind": "local_webapp", "default_enabled": False, "ledger_role": "local_ai_response_source"},
        ]
        return {
            "ok": True,
            "manifest_id": "smol-inspired-provider-pane-manifest",
            "source_reference": "smol-ai/GodMode multi-webapp provider list",
            "providers": providers,
            "layout": {
                "default_columns": 2,
                "supports_resize": True,
                "supports_reorder": True,
                "supports_popout": True,
                "supports_provider_toggle": True,
            },
            "security": {
                "store_credentials": False,
                "use_existing_local_browser_session": True,
                "operator_approval_required_for_credential_entry": True,
                "ledger_capture_separates_operator_request_and_ai_response": True,
            },
        }

    def prompt_broadcast_contract(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "contract": {
                "endpoint_future": "/api/provider-prompt-broadcast/package",
                "input": ["operator_request", "selected_provider_ids", "prompt_mode", "context_bundle_ref"],
                "outputs": ["broadcast_plan", "provider_jobs", "ledger_analysis", "script_extraction_queue", "comparison_report"],
                "rules": [
                    "Original operator request is preserved verbatim.",
                    "Prompt critic may produce improved prompt but cannot replace original intent silently.",
                    "Every provider answer becomes ai_response, not decision.",
                    "Scripts extracted from provider answers require reconciliation before apply.",
                    "Failures/login-needed states become operator attention cards.",
                ],
                "risk_gates": ["credential entry", "browser automation", "script apply", "repo write", "deploy", "merge", "release"],
            },
        }

    def prompt_critic_policy(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "policy": {
                "goal": "Improve clarity before multi-provider broadcast without changing the Oner's intent.",
                "must_preserve": ["original request", "project key", "constraints", "do-not-do rules", "approval gates", "security restrictions"],
                "must_output": ["original_prompt", "improved_prompt", "changes_summary", "risk_flags"],
                "blocked": ["remove operator constraint", "invent secret", "change architecture direction silently", "turn proposal into decision"],
            },
        }

    def package(self) -> Dict[str, Any]:
        return {
            "status": self.status(),
            "capability_fit": self.capability_fit(),
            "extracted_patterns": self.extracted_patterns(),
            "provider_pane_manifest": self.provider_pane_manifest(),
            "prompt_broadcast_contract": self.prompt_broadcast_contract(),
            "prompt_critic_policy": self.prompt_critic_policy(),
            "next_native_phase_recommendation": {
                "phase": 190,
                "name": "Provider Prompt Broadcast + Pane Manifest Runtime",
                "reason": "Implement smol-inspired provider panes and broadcast workflow natively, tied to ledger and provider proof.",
            },
        }


smol_godmode_reference_adapter_service = SmolGodModeReferenceAdapterService()
