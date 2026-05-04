from __future__ import annotations

import re
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import uuid4

from app.services.ai_provider_router_service import PROVIDERS, TASK_TAG_WEIGHTS, ai_provider_router_service
from app.utils.atomic_json_store import AtomicJsonStore

DATA_DIR = Path("data")
LEARNING_FILE = DATA_DIR / "provider_outcome_learning.json"
LEARNING_STORE = AtomicJsonStore(
    LEARNING_FILE,
    default_factory=lambda: {
        "version": 1,
        "policy": "learn_provider_outcomes_without_safety_bypass",
        "outcomes": [],
        "scorecards": [],
        "recommendations": [],
    },
)


class ProviderOutcomeLearningService:
    """Learns which AI providers work best per task type.

    Phase 171 records sanitized outcome metadata only. It does not store raw
    prompts, raw model answers, secrets, cookies, tokens or private repo dumps.
    It never recommends provider fallback to bypass safety rules.
    """

    SERVICE_ID = "provider_outcome_learning"
    OUTCOME_VALUES = {"success", "partial", "failed", "blocked", "unsafe", "timeout", "rate_limited"}
    BLOCKED_TEXT = [
        "password",
        "senha",
        "token",
        "api_key",
        "apikey",
        "secret",
        "private_key",
        "cookie",
        "authorization",
        "bearer",
        "access_token",
        "refresh_token",
        "github_pat",
    ]
    BLOCKED_FAILURE_REASONS = {"safety_refusal", "secret_detected", "policy_block", "operator_denied"}

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def status(self) -> Dict[str, Any]:
        state = LEARNING_STORE.load()
        return {
            "ok": True,
            "service": self.SERVICE_ID,
            "created_at": self._now(),
            "outcome_count": len(state.get("outcomes") or []),
            "scorecard_count": len(state.get("scorecards") or []),
            "recommendation_count": len(state.get("recommendations") or []),
            "provider_count": len(PROVIDERS),
            "task_weight_count": len(TASK_TAG_WEIGHTS),
            "raw_prompt_storage": False,
            "safety_bypass_allowed": False,
        }

    def rules(self) -> List[str]:
        return [
            "Guardar apenas metadados sanitizados de resultado; nunca prompts/respostas completas com segredos.",
            "Aprender sucesso/falha por provider, task_tags, risco e tipo de output.",
            "Gerar scorecards e ajustes recomendados para o AI Provider Router.",
            "Não recomendar fallback para contornar segurança, recusa política ou operador.",
            "Providers externos continuam dependentes do AI Handoff Security Guard.",
            "Ollama/local mantém prioridade para contexto sensível mesmo que outro provider tenha melhor sucesso geral.",
            "Ajustes aprendidos são recomendações explicáveis; não alteram destructivamente pesos base nesta fase.",
        ]

    def policy(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "service": self.SERVICE_ID,
            "purpose": "provider_outcome_learning_for_safe_router_tuning",
            "stored_fields": [
                "provider_id", "task_tags", "outcome", "quality_score", "latency_ms", "cost_hint",
                "failure_reason", "requires_safety_guard", "sensitive", "operator_rating",
            ],
            "not_stored": ["raw prompt", "raw response", "tokens", "passwords", "cookies", "private keys", "API keys", "repo dumps"],
            "blocked_failure_reasons": sorted(self.BLOCKED_FAILURE_REASONS),
            "rules": self.rules(),
        }

    def panel(self) -> Dict[str, Any]:
        return {
            **self.status(),
            "headline": "Provider Outcome Learning",
            "description": "Aprende quais providers IA funcionam melhor por tipo de tarefa sem guardar segredos e sem contornar segurança.",
            "primary_actions": [
                {"label": "Registar outcome", "endpoint": "/api/provider-outcome-learning/record-outcome", "method": "POST", "safe": True},
                {"label": "Gerar scorecard", "endpoint": "/api/provider-outcome-learning/scorecard", "method": "POST", "safe": True},
                {"label": "Router hints", "endpoint": "/api/provider-outcome-learning/router-hints", "method": "POST", "safe": True},
                {"label": "Simular rota aprendida", "endpoint": "/api/provider-outcome-learning/simulate-route", "method": "POST", "safe": True},
            ],
            "policy": self.policy(),
            "latest": self.latest(),
        }

    def record_outcome(
        self,
        provider_id: str,
        task_tags: List[str],
        outcome: str,
        quality_score: float = 0.0,
        latency_ms: Optional[int] = None,
        cost_hint: str = "unknown",
        failure_reason: str = "",
        sensitive: bool = False,
        requires_safety_guard: bool = True,
        operator_rating: Optional[int] = None,
        notes: str = "",
        project_name: str = "GOD_MODE",
    ) -> Dict[str, Any]:
        provider_id = provider_id.strip()
        if provider_id not in PROVIDERS:
            return {"ok": False, "service": self.SERVICE_ID, "error": "unknown_provider", "provider_id": provider_id}
        normalized_outcome = outcome.strip().lower()
        if normalized_outcome not in self.OUTCOME_VALUES:
            return {"ok": False, "service": self.SERVICE_ID, "error": "invalid_outcome", "allowed": sorted(self.OUTCOME_VALUES)}
        safe = self._validate_safe_text("\n".join([provider_id, " ".join(task_tags), failure_reason, notes, project_name]))
        if not safe.get("ok"):
            return {"ok": False, "service": self.SERVICE_ID, "error": "blocked_secret_keyword", "blocked_keywords": safe.get("blocked_keywords")}

        clamped_quality = max(0.0, min(float(quality_score), 1.0))
        outcome_record = {
            "outcome_id": f"provider-outcome-{uuid4().hex[:12]}",
            "created_at": self._now(),
            "project": self._normalize_project(project_name),
            "provider_id": provider_id,
            "task_tags": self._normalize_tags(task_tags),
            "outcome": normalized_outcome,
            "quality_score": clamped_quality,
            "latency_ms": max(0, int(latency_ms)) if latency_ms is not None else None,
            "cost_hint": self._safe_label(cost_hint),
            "failure_reason": self._safe_label(failure_reason),
            "sensitive": bool(sensitive),
            "requires_safety_guard": bool(requires_safety_guard),
            "operator_rating": max(1, min(int(operator_rating), 5)) if operator_rating is not None else None,
            "notes_summary": self._sanitize(notes)[:400],
            "safety_bypass_attempt": self._is_safety_bypass(normalized_outcome, failure_reason),
        }
        self._store("outcomes", outcome_record)
        return {"ok": True, "service": self.SERVICE_ID, "outcome": outcome_record}

    def scorecard(self, provider_id: Optional[str] = None, task_tag: Optional[str] = None) -> Dict[str, Any]:
        outcomes = self._filtered_outcomes(provider_id=provider_id, task_tag=task_tag)
        grouped: Dict[str, Dict[str, Any]] = defaultdict(lambda: {
            "total": 0,
            "success": 0,
            "partial": 0,
            "failed": 0,
            "blocked": 0,
            "unsafe": 0,
            "timeout": 0,
            "rate_limited": 0,
            "quality_sum": 0.0,
            "latency_values": [],
            "operator_rating_sum": 0,
            "operator_rating_count": 0,
            "sensitive_total": 0,
            "safety_bypass_attempts": 0,
        })
        for item in outcomes:
            for tag in item.get("task_tags") or ["default"]:
                key = f"{item['provider_id']}::{tag}"
                group = grouped[key]
                group["provider_id"] = item["provider_id"]
                group["task_tag"] = tag
                group["total"] += 1
                group[item.get("outcome", "failed")] += 1
                group["quality_sum"] += float(item.get("quality_score") or 0.0)
                if item.get("latency_ms") is not None:
                    group["latency_values"].append(int(item["latency_ms"]))
                if item.get("operator_rating") is not None:
                    group["operator_rating_sum"] += int(item["operator_rating"])
                    group["operator_rating_count"] += 1
                if item.get("sensitive"):
                    group["sensitive_total"] += 1
                if item.get("safety_bypass_attempt"):
                    group["safety_bypass_attempts"] += 1

        rows: List[Dict[str, Any]] = []
        for group in grouped.values():
            total = max(1, group["total"])
            success_rate = (group["success"] + 0.55 * group["partial"]) / total
            failure_rate = (group["failed"] + group["timeout"] + group["rate_limited"]) / total
            safety_penalty = (group["blocked"] + group["unsafe"] + group["safety_bypass_attempts"] * 2) / total
            quality_avg = group["quality_sum"] / total
            latency_avg = int(sum(group["latency_values"]) / len(group["latency_values"])) if group["latency_values"] else None
            operator_avg = (group["operator_rating_sum"] / group["operator_rating_count"]) if group["operator_rating_count"] else None
            learned_delta = self._learned_delta(success_rate, failure_rate, safety_penalty, quality_avg, operator_avg)
            rows.append({
                "provider_id": group["provider_id"],
                "task_tag": group["task_tag"],
                "total": group["total"],
                "success_rate": round(success_rate, 3),
                "failure_rate": round(failure_rate, 3),
                "safety_penalty": round(safety_penalty, 3),
                "quality_avg": round(quality_avg, 3),
                "latency_avg_ms": latency_avg,
                "operator_rating_avg": round(operator_avg, 2) if operator_avg is not None else None,
                "sensitive_total": group["sensitive_total"],
                "learned_score_delta": learned_delta,
                "recommendation": self._recommendation_for_delta(learned_delta, safety_penalty),
            })
        rows.sort(key=lambda item: (item["task_tag"], item["learned_score_delta"], item["success_rate"]), reverse=True)
        card = {
            "scorecard_id": f"provider-scorecard-{uuid4().hex[:12]}",
            "created_at": self._now(),
            "provider_filter": provider_id,
            "task_tag_filter": task_tag,
            "outcome_count": len(outcomes),
            "rows": rows,
        }
        self._store("scorecards", card)
        return {"ok": True, "service": self.SERVICE_ID, "scorecard": card}

    def router_hints(self, task_tags: List[str], sensitive: bool = False) -> Dict[str, Any]:
        tags = self._normalize_tags(task_tags or ["default"])
        card = self.scorecard().get("scorecard", {})
        hints: Dict[str, int] = {provider_id: 0 for provider_id in PROVIDERS}
        evidence: List[Dict[str, Any]] = []
        for row in card.get("rows") or []:
            if row.get("task_tag") not in tags:
                continue
            provider_id = row.get("provider_id")
            delta = int(row.get("learned_score_delta") or 0)
            if sensitive and not PROVIDERS.get(provider_id, {}).get("safe_for_sensitive", False):
                delta = min(delta, -20)
            if row.get("safety_penalty", 0) > 0:
                delta = min(delta, 0)
            hints[provider_id] = hints.get(provider_id, 0) + delta
            evidence.append(row)
        recommendation = {
            "recommendation_id": f"provider-router-hints-{uuid4().hex[:12]}",
            "created_at": self._now(),
            "task_tags": tags,
            "sensitive": sensitive,
            "learned_provider_adjustments": hints,
            "evidence": evidence[:20],
            "safety_bypass_allowed": False,
            "apply_mode": "advisory_v1",
        }
        self._store("recommendations", recommendation)
        return {"ok": True, "service": self.SERVICE_ID, "router_hints": recommendation}

    def simulate_route(
        self,
        goal: str,
        task_tags: List[str] | None = None,
        sensitive: bool = False,
        needs_code: bool = False,
        needs_large_context: bool = False,
        needs_multimodal: bool = False,
    ) -> Dict[str, Any]:
        base = ai_provider_router_service.route(
            goal=goal,
            task_tags=task_tags,
            sensitive=sensitive,
            needs_code=needs_code,
            needs_large_context=needs_large_context,
            needs_multimodal=needs_multimodal,
        )
        tags = base.get("tags") or task_tags or ["default"]
        hints = self.router_hints(task_tags=tags, sensitive=sensitive).get("router_hints", {})
        adjustments = hints.get("learned_provider_adjustments") or {}
        learned_scores = []
        for item in base.get("all_scores") or []:
            adjusted = int(item.get("score") or 0) + int(adjustments.get(item.get("provider_id"), 0))
            learned = dict(item)
            learned["base_score"] = item.get("score")
            learned["learned_adjustment"] = int(adjustments.get(item.get("provider_id"), 0))
            learned["learned_score"] = adjusted if not item.get("hard_blocked") else -999
            learned_scores.append(learned)
        learned_scores.sort(key=lambda row: row["learned_score"], reverse=True)
        selected = next((item for item in learned_scores if item["learned_score"] >= 0 and not item.get("hard_blocked")), None)
        return {
            "ok": True,
            "service": self.SERVICE_ID,
            "base_route": base,
            "router_hints": hints,
            "learned_selected_provider": selected,
            "learned_scores": learned_scores,
            "safety_bypass_allowed": False,
            "note": "Simulation only; Phase 171 does not mutate base router weights automatically.",
        }

    def latest(self) -> Dict[str, Any]:
        state = LEARNING_STORE.load()
        return {
            "ok": True,
            "service": self.SERVICE_ID,
            "latest_outcome": (state.get("outcomes") or [None])[-1],
            "latest_scorecard": (state.get("scorecards") or [None])[-1],
            "latest_recommendation": (state.get("recommendations") or [None])[-1],
            "outcome_count": len(state.get("outcomes") or []),
            "scorecard_count": len(state.get("scorecards") or []),
            "recommendation_count": len(state.get("recommendations") or []),
        }

    def package(self) -> Dict[str, Any]:
        return {"status": self.status(), "panel": self.panel(), "policy": self.policy(), "latest": self.latest()}

    def _filtered_outcomes(self, provider_id: Optional[str] = None, task_tag: Optional[str] = None) -> List[Dict[str, Any]]:
        outcomes = LEARNING_STORE.load().get("outcomes") or []
        result = []
        for item in outcomes:
            if provider_id and item.get("provider_id") != provider_id:
                continue
            if task_tag and task_tag not in (item.get("task_tags") or []):
                continue
            result.append(item)
        return result

    def _learned_delta(self, success_rate: float, failure_rate: float, safety_penalty: float, quality_avg: float, operator_avg: Optional[float]) -> int:
        delta = 0
        delta += int((success_rate - 0.5) * 36)
        delta += int((quality_avg - 0.5) * 24)
        delta -= int(failure_rate * 18)
        delta -= int(safety_penalty * 60)
        if operator_avg is not None:
            delta += int((operator_avg - 3.0) * 6)
        return max(-40, min(40, delta))

    def _recommendation_for_delta(self, delta: int, safety_penalty: float) -> str:
        if safety_penalty > 0:
            return "do_not_boost_due_to_safety_penalty"
        if delta >= 12:
            return "boost_for_matching_task"
        if delta <= -12:
            return "deprioritize_for_matching_task"
        return "keep_neutral"

    def _is_safety_bypass(self, outcome: str, failure_reason: str) -> bool:
        reason = self._safe_label(failure_reason)
        return outcome in {"blocked", "unsafe"} or reason in self.BLOCKED_FAILURE_REASONS

    def _validate_safe_text(self, text: str) -> Dict[str, Any]:
        lowered = text.lower()
        hits = [keyword for keyword in self.BLOCKED_TEXT if re.search(rf"(?<![a-z0-9_]){re.escape(keyword)}(?![a-z0-9_])", lowered)]
        return {"ok": not hits, "blocked_keywords": hits}

    def _sanitize(self, text: str) -> str:
        sanitized = text
        sanitized = re.sub(r"(?i)(api[_-]?key|secret|password|senha|token|authorization|bearer|cookie)\s*[:=]\s*[^\s\n]+", "[REDACTED_SECRET]", sanitized)
        sanitized = re.sub(r"(?i)(sk_live_|sk_test_|ghp_|github_pat_|xoxb-|ya29\.)[^\s\n]+", "[REDACTED_SECRET]", sanitized)
        return sanitized

    def _normalize_tags(self, tags: List[str]) -> List[str]:
        cleaned = []
        for tag in tags or ["default"]:
            value = re.sub(r"[^a-z0-9_]+", "_", str(tag).lower()).strip("_")
            if value:
                cleaned.append(value)
        return list(dict.fromkeys(cleaned or ["default"]))

    def _safe_label(self, value: str) -> str:
        return re.sub(r"[^a-zA-Z0-9_\- .:/]+", "_", str(value or "unknown"))[:120]

    def _normalize_project(self, project_name: str) -> str:
        return re.sub(r"[^A-Z0-9_]+", "_", (project_name or "GOD_MODE").upper()).strip("_") or "GOD_MODE"

    def _store(self, key: str, item: Dict[str, Any]) -> None:
        def mutate(state: Dict[str, Any]) -> Dict[str, Any]:
            state.setdefault("version", 1)
            state.setdefault("policy", "learn_provider_outcomes_without_safety_bypass")
            state.setdefault(key, [])
            state[key].append(item)
            state[key] = state[key][-300:]
            return state

        LEARNING_STORE.update(mutate)


provider_outcome_learning_service = ProviderOutcomeLearningService()
