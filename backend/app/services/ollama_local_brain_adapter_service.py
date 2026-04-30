from __future__ import annotations

import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import httpx

from app.utils.atomic_json_store import AtomicJsonStore


OLLAMA_DEFAULT_URL = "http://127.0.0.1:11434"
STORE_PATH = Path("data/ollama_local_brain_adapter.json")

PREFERRED_LIGHT_MODELS = [
    "gemma2:2b",
    "qwen2.5:3b",
    "llama3.2:3b",
    "phi3:mini",
    "tinyllama:latest",
]

PREFERRED_CODE_MODELS = [
    "qwen2.5-coder:3b",
    "qwen2.5-coder:7b",
    "deepseek-coder:6.7b",
    "codellama:7b",
]

KNOWN_HEAVY_MARKERS = ["13b", "14b", "27b", "32b", "70b", "mixtral", "moe"]


def _default_store() -> dict[str, Any]:
    return {"runs": [], "last": None, "selected_model": None}


class OllamaLocalBrainAdapterService:
    def __init__(self) -> None:
        self.store = AtomicJsonStore(STORE_PATH, default_factory=_default_store)

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def _load(self) -> dict[str, Any]:
        payload = self.store.load()
        if not isinstance(payload, dict):
            return _default_store()
        payload.setdefault("runs", [])
        payload.setdefault("last", None)
        payload.setdefault("selected_model", None)
        return payload

    def _save_run(self, run: dict[str, Any]) -> dict[str, Any]:
        payload = self._load()
        runs = payload.get("runs", [])
        runs.append(run)
        payload["runs"] = runs[-100:]
        payload["last"] = run
        if run.get("selected_model"):
            payload["selected_model"] = run.get("selected_model")
        self.store.save(payload)
        return run

    def status(self) -> dict[str, Any]:
        payload = self._load()
        return {
            "ok": True,
            "service": "ollama_local_brain_adapter",
            "mode": "local_private_ai_worker",
            "ollama_url": OLLAMA_DEFAULT_URL,
            "store_path": str(STORE_PATH),
            "selected_model": payload.get("selected_model"),
            "last_run": payload.get("last"),
            "use_cases": self.use_cases()["use_cases"],
        }

    def panel(self) -> dict[str, Any]:
        return {
            **self.status(),
            "headline": "Ollama Local Brain Adapter",
            "description": "Usa modelos locais instalados no PC como cérebro auxiliar privado do God Mode.",
            "primary_actions": [
                {
                    "label": "Ver modelos Ollama",
                    "endpoint": "/api/ollama-local-brain/models",
                    "method": "GET",
                    "safe": True,
                },
                {
                    "label": "Benchmark leve",
                    "endpoint": "/api/ollama-local-brain/benchmark-light",
                    "method": "POST",
                    "safe": True,
                },
                {
                    "label": "Selecionar melhor modelo",
                    "endpoint": "/api/ollama-local-brain/auto-select",
                    "method": "POST",
                    "safe": True,
                },
                {
                    "label": "Política de uso",
                    "endpoint": "/api/ollama-local-brain/policy",
                    "method": "GET",
                    "safe": True,
                },
            ],
        }

    def use_cases(self) -> dict[str, Any]:
        return {
            "ok": True,
            "use_cases": [
                "resumir conversas antigas antes de enviar a provider externo",
                "classificar projeto/conversa/repo localmente",
                "gerar primeira versão de prompt/handoff",
                "limpar textos e MEMORY_DELTA",
                "sugerir próximos passos offline",
                "fazer revisão leve de código sem expor contexto privado",
                "funcionar como fallback quando internet/provider externo falhar",
            ],
            "not_recommended_for": [
                "decisões críticas sem validação",
                "código final complexo sem testes",
                "ações destrutivas",
                "substituir ChatGPT/providers externos quando o trabalho exigir mais qualidade",
            ],
        }

    def policy(self) -> dict[str, Any]:
        return {
            "ok": True,
            "rules": [
                "Ollama é worker local privado, não substituto total dos providers externos.",
                "No PC velho, preferir modelos pequenos e rápidos.",
                "No PC novo, retestar e promover modelos melhores automaticamente.",
                "Se um modelo falhar, marcar como não recomendado e escolher outro.",
                "Nunca enviar credenciais para o modelo local.",
                "Usar outputs do Ollama como rascunho/recomendação, depois validar com God Mode.",
            ],
            "routing": {
                "offline_or_private_summary": "ollama_first",
                "large_code_generation": "external_provider_first_then_local_review",
                "memory_delta_cleanup": "ollama_ok",
                "security_sensitive_task": "god_mode_gate_required",
                "driver_mode_short_answer": "ollama_if_fast_else_cached_summary",
            },
        }

    async def health(self, base_url: str = OLLAMA_DEFAULT_URL) -> dict[str, Any]:
        started = time.perf_counter()
        try:
            async with httpx.AsyncClient(timeout=2.0) as client:
                response = await client.get(f"{base_url.rstrip('/')}/api/tags")
            elapsed_ms = round((time.perf_counter() - started) * 1000, 2)
            return {
                "ok": response.status_code == 200,
                "reachable": response.status_code == 200,
                "status_code": response.status_code,
                "elapsed_ms": elapsed_ms,
                "base_url": base_url,
            }
        except Exception as exc:
            return {
                "ok": False,
                "reachable": False,
                "error_type": exc.__class__.__name__,
                "base_url": base_url,
            }

    async def models(self, base_url: str = OLLAMA_DEFAULT_URL) -> dict[str, Any]:
        health = await self.health(base_url)
        if not health.get("reachable"):
            return {
                "ok": False,
                "health": health,
                "models": [],
                "message": "Ollama não está acessível. Confirma se o serviço está aberto no PC.",
            }
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{base_url.rstrip('/')}/api/tags")
            data = response.json()
            models = []
            for item in data.get("models", []):
                name = item.get("name") or item.get("model") or "unknown"
                size = item.get("size")
                models.append(
                    {
                        "name": name,
                        "size": size,
                        "modified_at": item.get("modified_at"),
                        "family": (item.get("details") or {}).get("family"),
                        "parameter_size": (item.get("details") or {}).get("parameter_size"),
                        "quantization_level": (item.get("details") or {}).get("quantization_level"),
                        "is_known_light": name in PREFERRED_LIGHT_MODELS,
                        "is_known_code": name in PREFERRED_CODE_MODELS,
                        "is_likely_heavy": self._is_likely_heavy(name),
                    }
                )
            return {
                "ok": True,
                "health": health,
                "model_count": len(models),
                "models": models,
                "recommended_candidates": self._rank_candidates(models),
            }
        except Exception as exc:
            return {"ok": False, "health": health, "error_type": exc.__class__.__name__, "models": []}

    def _is_likely_heavy(self, name: str) -> bool:
        lowered = name.lower()
        return any(marker in lowered for marker in KNOWN_HEAVY_MARKERS)

    def _rank_candidates(self, models: list[dict[str, Any]]) -> list[dict[str, Any]]:
        ranked = []
        for model in models:
            name = model.get("name", "")
            score = 50
            reason = []
            if name in PREFERRED_LIGHT_MODELS:
                score += 35
                reason.append("modelo leve conhecido")
            if name in PREFERRED_CODE_MODELS:
                score += 20
                reason.append("modelo de código conhecido")
            if model.get("is_likely_heavy"):
                score -= 30
                reason.append("provavelmente pesado para PC fraco")
            parameter_size = str(model.get("parameter_size") or "").lower()
            if "2b" in parameter_size or ":2b" in name.lower():
                score += 20
                reason.append("2B adequado a PC fraco")
            if "7b" in parameter_size or ":7b" in name.lower():
                score += 5
                reason.append("7B pode ser útil se o PC aguentar")
            ranked.append({"name": name, "score": score, "reason": reason or ["candidato neutro"]})
        return sorted(ranked, key=lambda item: item["score"], reverse=True)

    async def benchmark_light(
        self,
        model: str | None = None,
        base_url: str = OLLAMA_DEFAULT_URL,
        prompt: str | None = None,
    ) -> dict[str, Any]:
        model_payload = await self.models(base_url)
        if not model_payload.get("ok"):
            return {"ok": False, "error_type": "ollama_unavailable", "models": model_payload}
        candidates = model_payload.get("recommended_candidates", [])
        selected = model or (candidates[0]["name"] if candidates else None)
        if not selected:
            return {"ok": False, "error_type": "no_model_available", "models": model_payload}
        test_prompt = prompt or (
            "Responde em PT-PT com uma frase curta: o God Mode deve usar Ollama para resumos locais privados."
        )
        started = time.perf_counter()
        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                response = await client.post(
                    f"{base_url.rstrip('/')}/api/generate",
                    json={
                        "model": selected,
                        "prompt": test_prompt,
                        "stream": False,
                        "options": {"num_predict": 80, "temperature": 0.2},
                    },
                )
            elapsed_ms = round((time.perf_counter() - started) * 1000, 2)
            ok = response.status_code == 200
            body = response.json() if ok else {"error": response.text[:500]}
            text = body.get("response", "") if isinstance(body, dict) else ""
            tokens_estimate = max(1, len(text.split()))
            speed_score = max(0, 100 - int(elapsed_ms / 250))
            quality_score = 20 if len(text.strip()) >= 20 else 5
            total_score = min(100, speed_score + quality_score)
            run = {
                "run_id": f"ollama-bench-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}",
                "created_at": self._now(),
                "model": selected,
                "ok": ok,
                "elapsed_ms": elapsed_ms,
                "tokens_estimate": tokens_estimate,
                "score": total_score,
                "preview": text[:500],
                "selected_model": selected if ok else None,
            }
            self._save_run(run)
            return {"ok": ok, "benchmark": run, "raw_status_code": response.status_code}
        except Exception as exc:
            run = {
                "run_id": f"ollama-bench-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}",
                "created_at": self._now(),
                "model": selected,
                "ok": False,
                "error_type": exc.__class__.__name__,
                "score": 0,
            }
            self._save_run(run)
            return {"ok": False, "benchmark": run}

    async def auto_select(self, base_url: str = OLLAMA_DEFAULT_URL) -> dict[str, Any]:
        model_payload = await self.models(base_url)
        if not model_payload.get("ok"):
            return {"ok": False, "error_type": "models_unavailable", "models": model_payload}
        candidates = model_payload.get("recommended_candidates", [])[:5]
        benchmark_results = []
        best = None
        for candidate in candidates:
            result = await self.benchmark_light(model=candidate["name"], base_url=base_url)
            benchmark_results.append(result)
            bench = result.get("benchmark", {})
            if bench.get("ok") and (best is None or bench.get("score", 0) > best.get("score", 0)):
                best = bench
        if not best:
            return {
                "ok": False,
                "error_type": "no_working_model",
                "benchmark_results": benchmark_results,
                "recommendation": "desinstalar ou ignorar modelos que falham e instalar um modelo leve como gemma2:2b",
            }
        payload = self._load()
        payload["selected_model"] = best.get("model")
        payload["last_auto_select"] = self._now()
        self.store.save(payload)
        return {
            "ok": True,
            "selected_model": best.get("model"),
            "score": best.get("score"),
            "benchmark_results": benchmark_results,
            "recommended_usage": self.route_decision(task_kind="summary_private"),
        }

    def route_decision(self, task_kind: str = "summary_private") -> dict[str, Any]:
        payload = self._load()
        selected = payload.get("selected_model")
        local_ok = bool(selected)
        routing = {
            "summary_private": "ollama" if local_ok else "external_provider_or_cached",
            "memory_delta": "ollama" if local_ok else "god_mode_template",
            "code_review_light": "ollama_then_external_if_needed" if local_ok else "external_provider",
            "code_generation_complex": "external_provider_then_god_mode_validation",
            "offline_next_steps": "ollama" if local_ok else "local_rules_only",
        }
        return {
            "ok": True,
            "task_kind": task_kind,
            "selected_model": selected,
            "route": routing.get(task_kind, "god_mode_decides"),
            "local_available": local_ok,
        }

    async def generate(
        self,
        prompt: str,
        model: str | None = None,
        base_url: str = OLLAMA_DEFAULT_URL,
        max_tokens: int = 256,
    ) -> dict[str, Any]:
        payload = self._load()
        selected = model or payload.get("selected_model")
        if not selected:
            return {"ok": False, "error_type": "no_selected_model", "next_action": "run_auto_select"}
        try:
            async with httpx.AsyncClient(timeout=45.0) as client:
                response = await client.post(
                    f"{base_url.rstrip('/')}/api/generate",
                    json={
                        "model": selected,
                        "prompt": prompt,
                        "stream": False,
                        "options": {"num_predict": max(32, min(max_tokens, 1024)), "temperature": 0.2},
                    },
                )
            ok = response.status_code == 200
            body = response.json() if ok else {"error": response.text[:500]}
            return {
                "ok": ok,
                "model": selected,
                "response": body.get("response", "") if isinstance(body, dict) else "",
                "raw_status_code": response.status_code,
                "fallback_needed": not ok,
            }
        except Exception as exc:
            return {"ok": False, "model": selected, "error_type": exc.__class__.__name__, "fallback_needed": True}

    async def package(self) -> dict[str, Any]:
        return {
            "status": self.status(),
            "panel": self.panel(),
            "policy": self.policy(),
            "use_cases": self.use_cases(),
            "route_summary": {
                "summary_private": self.route_decision("summary_private"),
                "memory_delta": self.route_decision("memory_delta"),
                "code_review_light": self.route_decision("code_review_light"),
                "offline_next_steps": self.route_decision("offline_next_steps"),
            },
        }


ollama_local_brain_adapter_service = OllamaLocalBrainAdapterService()
