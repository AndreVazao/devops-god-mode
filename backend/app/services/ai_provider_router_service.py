from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


PROVIDERS: dict[str, dict[str, Any]] = {
    "chatgpt": {
        "name": "ChatGPT",
        "kind": "external_web_ai",
        "default_priority": 100,
        "strengths": ["software_engineering", "planning", "debugging", "architecture", "portuguese", "long_context"],
        "weaknesses": ["rate_limits", "policy_refusals_possible", "web_ui_dependency"],
        "safe_for_sensitive": False,
        "requires_security_guard": True,
        "preferred_for": ["default", "architecture", "code_review", "planning", "debugging", "documentation"],
    },
    "gemini": {
        "name": "Gemini",
        "kind": "external_web_ai",
        "default_priority": 82,
        "strengths": ["large_context", "research", "multimodal", "google_ecosystem"],
        "weaknesses": ["policy_refusals_possible", "web_ui_dependency"],
        "safe_for_sensitive": False,
        "requires_security_guard": True,
        "preferred_for": ["large_context", "research", "multimodal", "cross_check"],
    },
    "deepseek": {
        "name": "DeepSeek",
        "kind": "external_web_ai",
        "default_priority": 76,
        "strengths": ["coding", "algorithmic_reasoning", "less_restrictive_for_code", "fallback"],
        "weaknesses": ["external_provider", "security_review_required"],
        "safe_for_sensitive": False,
        "requires_security_guard": True,
        "preferred_for": ["code_generation", "fallback_when_primary_refuses", "algorithm", "script_completion"],
    },
    "grok": {
        "name": "Grok",
        "kind": "external_web_ai",
        "default_priority": 68,
        "strengths": ["alternative_reasoning", "fast_cross_check", "current_discussion_style"],
        "weaknesses": ["external_provider", "not_primary_for_codebase_changes"],
        "safe_for_sensitive": False,
        "requires_security_guard": True,
        "preferred_for": ["cross_check", "alternative_opinion", "ideation"],
    },
    "ollama": {
        "name": "Ollama Local",
        "kind": "local_ai",
        "default_priority": 70,
        "strengths": ["private", "offline_possible", "local_summary", "triage", "no_web_account_needed"],
        "weaknesses": ["model_quality_varies", "slow_on_old_pc", "limited_context_by_model"],
        "safe_for_sensitive": True,
        "requires_security_guard": True,
        "preferred_for": ["private_context", "local_summary", "triage", "offline", "sensitive_preprocessing"],
    },
    "claude_code_or_codex_local": {
        "name": "Local coding assistant / Codex / Claude Code when available",
        "kind": "local_or_cli_tool",
        "default_priority": 72,
        "strengths": ["local_repo_editing", "codebase_navigation", "patch_generation"],
        "weaknesses": ["tool_availability_varies", "setup_required", "pc_dependency"],
        "safe_for_sensitive": True,
        "requires_security_guard": True,
        "preferred_for": ["local_repo_edit", "patch", "codebase_navigation"],
    },
}

TASK_TAG_WEIGHTS: dict[str, dict[str, int]] = {
    "default": {"chatgpt": 25, "ollama": 5},
    "architecture": {"chatgpt": 30, "gemini": 10, "ollama": 5},
    "planning": {"chatgpt": 30, "gemini": 10, "ollama": 10},
    "debugging": {"chatgpt": 25, "deepseek": 20, "claude_code_or_codex_local": 15},
    "code_generation": {"chatgpt": 20, "deepseek": 28, "claude_code_or_codex_local": 18},
    "code_review": {"chatgpt": 25, "deepseek": 14, "claude_code_or_codex_local": 18},
    "large_context": {"gemini": 30, "chatgpt": 16},
    "research": {"gemini": 25, "chatgpt": 14, "grok": 12},
    "multimodal": {"gemini": 30, "chatgpt": 10},
    "fallback_when_primary_refuses": {"deepseek": 32, "grok": 10, "gemini": 8},
    "private_context": {"ollama": 40, "claude_code_or_codex_local": 20},
    "offline": {"ollama": 45},
    "local_repo_edit": {"claude_code_or_codex_local": 35, "ollama": 12},
    "cross_check": {"gemini": 18, "grok": 18, "deepseek": 12},
    "security": {"ollama": 22, "chatgpt": 8},
}


class AiProviderRouterService:
    """Ranks AI providers for a God Mode task and returns safe fallback order."""

    def status(self) -> dict[str, Any]:
        return {
            "ok": True,
            "service": "ai_provider_router",
            "created_at": _utc_now(),
            "provider_count": len(PROVIDERS),
            "task_weight_count": len(TASK_TAG_WEIGHTS),
            "mode": "scored_provider_selection_and_fallback",
        }

    def panel(self) -> dict[str, Any]:
        return {
            **self.status(),
            "headline": "AI Provider Router",
            "description": "Escolhe o provider IA mais adequado por tarefa, segurança, privacidade, fallback e disponibilidade.",
            "primary_actions": [
                {"label": "Escolher provider", "endpoint": "/api/ai-provider-router/route", "method": "POST", "safe": True},
                {"label": "Ver providers", "endpoint": "/api/ai-provider-router/providers", "method": "GET", "safe": True},
                {"label": "Ver política", "endpoint": "/api/ai-provider-router/policy", "method": "GET", "safe": True},
            ],
            "rules": self.rules(),
        }

    def rules(self) -> list[str]:
        return [
            "ChatGPT é provider principal por defeito para PT, planeamento, arquitetura, debugging e revisão.",
            "Ollama/local é preferido para contexto sensível, triagem privada, resumo local e modo offline.",
            "DeepSeek é fallback forte para código quando o provider principal recusa ou não conclui.",
            "Gemini é forte para contexto grande, pesquisa, multimodal e cross-check.",
            "Grok é útil para segunda opinião, ideação e cross-check rápido.",
            "Todo handoff passa pelo AI Handoff Security Guard antes de enviar contexto.",
            "Se houver secrets, providers externos ficam bloqueados até sanitização.",
            "Provider Router escolhe e recomenda; não executa web automation diretamente nesta fase.",
        ]

    def providers(self) -> dict[str, Any]:
        return {"ok": True, "providers": PROVIDERS}

    def policy(self) -> dict[str, Any]:
        return {
            "ok": True,
            "default_provider": "chatgpt",
            "local_private_provider": "ollama",
            "code_fallback_provider": "deepseek",
            "large_context_provider": "gemini",
            "cross_check_providers": ["gemini", "grok", "deepseek"],
            "security_gate": "/api/ai-handoff-security-guard/prepare",
            "trace_gate": "/api/ai-handoff-trace/panel",
            "hard_blocks": [
                "raw tokens/passwords/cookies/private keys in context",
                "operator did not approve high-risk external handoff",
                "provider is unavailable and no fallback exists",
            ],
        }

    def route(
        self,
        goal: str,
        task_tags: list[str] | None = None,
        context: str | None = None,
        sensitive: bool = False,
        needs_code: bool = False,
        needs_large_context: bool = False,
        needs_multimodal: bool = False,
        primary_failed: bool = False,
        provider_availability: dict[str, bool] | None = None,
        preferred_provider: str | None = None,
    ) -> dict[str, Any]:
        tags = self._infer_tags(
            goal=goal,
            context=context,
            explicit_tags=task_tags or [],
            sensitive=sensitive,
            needs_code=needs_code,
            needs_large_context=needs_large_context,
            needs_multimodal=needs_multimodal,
            primary_failed=primary_failed,
        )
        availability = provider_availability or {}
        scored = []
        for provider_id, provider in PROVIDERS.items():
            available = availability.get(provider_id, True)
            score = self._score_provider(provider_id, provider, tags, sensitive, preferred_provider)
            reasons = self._reasons(provider_id, provider, tags, sensitive, preferred_provider, available)
            hard_blocked = not available or (sensitive and not provider.get("safe_for_sensitive", False) and self._has_secret_risk(goal, context))
            scored.append(
                {
                    "provider_id": provider_id,
                    "name": provider["name"],
                    "kind": provider["kind"],
                    "score": score if not hard_blocked else -999,
                    "available": available,
                    "hard_blocked": hard_blocked,
                    "safe_for_sensitive": provider["safe_for_sensitive"],
                    "requires_security_guard": provider["requires_security_guard"],
                    "reasons": reasons,
                    "handoff_requirements": self._handoff_requirements(provider_id, provider, sensitive),
                }
            )
        scored.sort(key=lambda item: item["score"], reverse=True)
        usable = [item for item in scored if item["score"] >= 0 and not item["hard_blocked"]]
        selected = usable[0] if usable else None
        fallback_chain = usable[1:5]
        return {
            "ok": True,
            "created_at": _utc_now(),
            "goal": goal,
            "tags": tags,
            "sensitive": sensitive,
            "selected_provider": selected,
            "fallback_chain": fallback_chain,
            "all_scores": scored,
            "security_gate_required": True,
            "security_gate_endpoint": "/api/ai-handoff-security-guard/prepare",
            "trace_endpoint": "/api/ai-handoff-trace/panel",
            "operator_summary": self._summary(selected, fallback_chain, tags),
        }

    def _infer_tags(
        self,
        goal: str,
        context: str | None,
        explicit_tags: list[str],
        sensitive: bool,
        needs_code: bool,
        needs_large_context: bool,
        needs_multimodal: bool,
        primary_failed: bool,
    ) -> list[str]:
        tags = list(dict.fromkeys(explicit_tags))
        text = f"{goal}\n{context or ''}".lower()
        if not tags:
            tags.append("default")
        if any(word in text for word in ["arquitetura", "architecture", "design", "estrutura"]):
            tags.append("architecture")
        if any(word in text for word in ["plano", "planeia", "planning", "goal"]):
            tags.append("planning")
        if any(word in text for word in ["erro", "bug", "falha", "debug", "corrigir"]):
            tags.append("debugging")
        if needs_code or any(word in text for word in ["código", "codigo", "script", "implementar", "função", "endpoint", "service"]):
            tags.append("code_generation")
        if any(word in text for word in ["review", "auditoria", "revisão", "revisao"]):
            tags.append("code_review")
        if sensitive:
            tags.append("private_context")
            tags.append("security")
        if needs_large_context or any(word in text for word in ["muito contexto", "conversa longa", "large context"]):
            tags.append("large_context")
        if needs_multimodal or any(word in text for word in ["imagem", "screenshot", "multimodal", "foto"]):
            tags.append("multimodal")
        if primary_failed or any(word in text for word in ["recusou", "não quer fazer", "nao quer fazer", "refused"]):
            tags.append("fallback_when_primary_refuses")
        return list(dict.fromkeys(tags))

    def _score_provider(self, provider_id: str, provider: dict[str, Any], tags: list[str], sensitive: bool, preferred_provider: str | None) -> int:
        score = int(provider["default_priority"])
        for tag in tags:
            score += TASK_TAG_WEIGHTS.get(tag, {}).get(provider_id, 0)
            if tag in provider.get("preferred_for", []):
                score += 10
            if tag in provider.get("strengths", []):
                score += 8
        if sensitive:
            score += 35 if provider.get("safe_for_sensitive") else -80
        if preferred_provider and provider_id == preferred_provider:
            score += 25
        if "rate_limits" in provider.get("weaknesses", []):
            score -= 4
        return score

    def _reasons(
        self,
        provider_id: str,
        provider: dict[str, Any],
        tags: list[str],
        sensitive: bool,
        preferred_provider: str | None,
        available: bool,
    ) -> list[str]:
        reasons: list[str] = []
        if not available:
            return ["Provider marcado como indisponível."]
        if preferred_provider == provider_id:
            reasons.append("Provider preferido pelo operador/pedido.")
        for tag in tags:
            if tag in provider.get("preferred_for", []):
                reasons.append(f"Preferido para {tag}.")
            elif TASK_TAG_WEIGHTS.get(tag, {}).get(provider_id):
                reasons.append(f"Recebe peso positivo para {tag}.")
        if sensitive and provider.get("safe_for_sensitive"):
            reasons.append("Adequado para contexto sensível/local.")
        if sensitive and not provider.get("safe_for_sensitive"):
            reasons.append("Não é ideal para contexto sensível sem sanitização forte.")
        return reasons or ["Pontuação base e disponibilidade." ]

    def _handoff_requirements(self, provider_id: str, provider: dict[str, Any], sensitive: bool) -> list[str]:
        requirements = ["run_ai_handoff_security_guard", "create_ai_handoff_trace"]
        if not provider.get("safe_for_sensitive"):
            requirements.append("send_sanitized_context_only")
        if sensitive:
            requirements.append("operator_review_if_high_risk")
        if provider_id == "ollama":
            requirements.append("check_local_model_availability")
        return requirements

    def _has_secret_risk(self, goal: str, context: str | None) -> bool:
        text = f"{goal}\n{context or ''}".lower()
        return any(word in text for word in ["token", "password", "senha", "cookie", "secret", "private key", "api key"])

    def _summary(self, selected: dict[str, Any] | None, fallback_chain: list[dict[str, Any]], tags: list[str]) -> str:
        if not selected:
            return "Nenhum provider seguro disponível. Sanitizar contexto ou alterar disponibilidade."
        fallback = ", ".join(item["provider_id"] for item in fallback_chain) or "sem fallback"
        return f"Provider escolhido: {selected['provider_id']} ({selected['score']} pts). Tags: {', '.join(tags)}. Fallback: {fallback}."

    def package(self) -> dict[str, Any]:
        return {
            "status": self.status(),
            "panel": self.panel(),
            "rules": self.rules(),
            "providers": PROVIDERS,
            "policy": self.policy(),
        }


ai_provider_router_service = AiProviderRouterService()
