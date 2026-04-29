from __future__ import annotations

import json
import shutil
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import uuid4

from app.services.local_cleanup_optimizer_service import local_cleanup_optimizer_service
from app.utils.atomic_json_store import AtomicJsonStore

DATA_DIR = Path("data")
BENCH_FILE = DATA_DIR / "ollama_model_benchmark.json"
BENCH_STORE = AtomicJsonStore(
    BENCH_FILE,
    default_factory=lambda: {
        "version": 1,
        "policy": "benchmark_ollama_models_and_keep_only_best_working_models",
        "benchmark_runs": [],
        "recommendations": [],
    },
)


class OllamaModelBenchmarkService:
    """Benchmark installed Ollama models and recommend what to keep/remove.

    This is designed for both weak old PCs and stronger future PCs. It never
    removes a model by itself; it recommends a keep/remove list that feeds the
    Local Cleanup Optimizer.
    """

    DEFAULT_TEST_PROMPT = (
        "Responde em português, curto e direto: explica em 3 linhas como ajudarias "
        "um projeto de software a corrigir um erro simples de Python."
    )

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def policy(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "mode": "ollama_model_benchmark_policy",
            "goal": "deixar no PC apenas modelos Ollama úteis, rápidos e funcionais",
            "weak_pc_default_timeout_seconds": 45,
            "strong_pc_default_timeout_seconds": 90,
            "default_keep_if_score_at_least": 65,
            "default_max_keep_weak_pc": 2,
            "default_max_keep_strong_pc": 5,
            "never_remove_without_cleanup_phase": True,
        }

    def list_models(self) -> Dict[str, Any]:
        scan = local_cleanup_optimizer_service.scan().get("scan", {})
        ollama = scan.get("ollama", {})
        return {"ok": True, "mode": "ollama_model_list", "ollama": ollama, "models": ollama.get("models", [])}

    def benchmark(
        self,
        pc_profile: str = "auto",
        test_prompt: Optional[str] = None,
        timeout_seconds: Optional[int] = None,
        max_models: int = 20,
    ) -> Dict[str, Any]:
        ollama_path = shutil.which("ollama")
        if not ollama_path:
            return {"ok": False, "mode": "ollama_model_benchmark", "error": "ollama_not_found"}
        models = self.list_models().get("models", [])[: max(1, min(max_models, 50))]
        timeout = timeout_seconds or (90 if pc_profile in {"strong", "new", "powerful"} else 45)
        prompt = test_prompt or self.DEFAULT_TEST_PROMPT
        results: List[Dict[str, Any]] = []
        for model in models:
            name = model.get("name")
            if not name:
                continue
            results.append(self._benchmark_one(ollama_path, name, prompt, timeout))
        recommendation = self._recommend(results, pc_profile=pc_profile)
        run = {
            "benchmark_id": f"ollama-benchmark-{uuid4().hex[:12]}",
            "created_at": self._now(),
            "pc_profile": pc_profile,
            "timeout_seconds": timeout,
            "prompt_chars": len(prompt),
            "model_count": len(models),
            "results": results,
            "recommendation": recommendation,
        }
        self._store("benchmark_runs", run)
        self._store("recommendations", recommendation)
        return {"ok": True, "mode": "ollama_model_benchmark", "run": run}

    def _benchmark_one(self, ollama_path: str, model_name: str, prompt: str, timeout: int) -> Dict[str, Any]:
        started = time.monotonic()
        try:
            completed = subprocess.run(
                [ollama_path, "run", model_name, prompt],
                capture_output=True,
                text=True,
                timeout=timeout,
                check=False,
            )
            duration = round(time.monotonic() - started, 2)
            stdout = (completed.stdout or "").strip()
            stderr = (completed.stderr or "").strip()
            ok = completed.returncode == 0 and len(stdout) >= 40
            return {
                "model": model_name,
                "ok": ok,
                "returncode": completed.returncode,
                "duration_seconds": duration,
                "stdout_preview": stdout[:1000],
                "stderr_preview": stderr[:1000],
                "score": self._score(ok=ok, duration=duration, output=stdout, stderr=stderr, timed_out=False),
                "classification": self._classification(ok=ok, duration=duration, score=self._score(ok=ok, duration=duration, output=stdout, stderr=stderr, timed_out=False)),
            }
        except subprocess.TimeoutExpired as exc:
            duration = round(time.monotonic() - started, 2)
            return {
                "model": model_name,
                "ok": False,
                "timed_out": True,
                "duration_seconds": duration,
                "stdout_preview": ((exc.stdout or "") if isinstance(exc.stdout, str) else "")[:1000],
                "stderr_preview": ((exc.stderr or "") if isinstance(exc.stderr, str) else "")[:1000],
                "score": self._score(ok=False, duration=duration, output="", stderr="timeout", timed_out=True),
                "classification": "remove_or_skip_too_slow",
            }
        except Exception as exc:
            duration = round(time.monotonic() - started, 2)
            return {
                "model": model_name,
                "ok": False,
                "duration_seconds": duration,
                "error": exc.__class__.__name__,
                "detail": str(exc)[:500],
                "score": 0,
                "classification": "remove_or_skip_error",
            }

    def _score(self, ok: bool, duration: float, output: str, stderr: str, timed_out: bool) -> int:
        if timed_out:
            return 0
        if not ok:
            return 10 if output else 0
        score = 100
        if duration > 60:
            score -= 40
        elif duration > 30:
            score -= 25
        elif duration > 15:
            score -= 12
        if len(output) < 120:
            score -= 15
        if stderr:
            score -= 10
        if "python" not in output.lower() and "erro" not in output.lower() and "projeto" not in output.lower():
            score -= 10
        return max(0, min(100, score))

    def _classification(self, ok: bool, duration: float, score: int) -> str:
        if not ok:
            return "remove_or_skip_failed"
        if score >= 80:
            return "keep_best"
        if score >= 65:
            return "keep_usable"
        if duration > 45:
            return "remove_or_skip_too_slow"
        return "review_low_score"

    def _recommend(self, results: List[Dict[str, Any]], pc_profile: str) -> Dict[str, Any]:
        max_keep = 5 if pc_profile in {"strong", "new", "powerful"} else 2
        sorted_results = sorted(results, key=lambda item: item.get("score", 0), reverse=True)
        keep = [item["model"] for item in sorted_results if item.get("score", 0) >= 65][:max_keep]
        remove = [item["model"] for item in results if item.get("model") not in keep and item.get("score", 0) < 65]
        review = [item["model"] for item in results if item.get("model") not in keep and item.get("model") not in remove]
        return {
            "recommendation_id": f"ollama-recommendation-{uuid4().hex[:12]}",
            "created_at": self._now(),
            "pc_profile": pc_profile,
            "max_keep": max_keep,
            "keep_models": keep,
            "remove_models": remove,
            "review_models": review,
            "best_model": keep[0] if keep else None,
            "cleanup_payload": {
                "keep_ollama_models": keep,
                "broken_ollama_models": remove,
                "allow_auto_ollama_remove": True,
                "allow_windows_tuning_script": False,
            },
            "next_endpoint": "/api/local-cleanup/plan",
        }

    def cleanup_plan_from_latest(self) -> Dict[str, Any]:
        latest = self.latest().get("latest_recommendation")
        if not latest:
            return {"ok": False, "mode": "ollama_cleanup_plan_from_latest", "error": "no_recommendation"}
        payload = latest.get("cleanup_payload") or {}
        return local_cleanup_optimizer_service.plan(
            keep_ollama_models=payload.get("keep_ollama_models"),
            broken_ollama_models=payload.get("broken_ollama_models"),
            allow_auto_ollama_remove=payload.get("allow_auto_ollama_remove", True),
            allow_windows_tuning_script=payload.get("allow_windows_tuning_script", False),
        )

    def _store(self, key: str, value: Dict[str, Any]) -> None:
        def mutate(state: Dict[str, Any]) -> Dict[str, Any]:
            state.setdefault(key, [])
            state[key].append(value)
            state[key] = state[key][-100:]
            return state
        BENCH_STORE.update(mutate)

    def latest(self) -> Dict[str, Any]:
        state = BENCH_STORE.load()
        return {
            "ok": True,
            "mode": "ollama_model_benchmark_latest",
            "latest_run": (state.get("benchmark_runs") or [None])[-1],
            "latest_recommendation": (state.get("recommendations") or [None])[-1],
            "run_count": len(state.get("benchmark_runs") or []),
            "recommendation_count": len(state.get("recommendations") or []),
        }

    def panel(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "mode": "ollama_model_benchmark_panel",
            "headline": "Testar modelos Ollama e manter os melhores",
            "policy": self.policy(),
            "models": self.list_models().get("models", []),
            "latest": self.latest(),
            "safe_buttons": [
                {"id": "list", "label": "Listar modelos", "endpoint": "/api/ollama-model-benchmark/models", "priority": "high"},
                {"id": "benchmark", "label": "Testar modelos", "endpoint": "/api/ollama-model-benchmark/run", "priority": "critical"},
                {"id": "cleanup_plan", "label": "Plano limpeza", "endpoint": "/api/ollama-model-benchmark/cleanup-plan", "priority": "critical"},
                {"id": "latest", "label": "Último teste", "endpoint": "/api/ollama-model-benchmark/latest", "priority": "high"},
            ],
        }

    def get_status(self) -> Dict[str, Any]:
        latest = self.latest()
        rec = latest.get("latest_recommendation") or {}
        return {
            "ok": True,
            "mode": "ollama_model_benchmark_status",
            "run_count": latest.get("run_count", 0),
            "recommendation_count": latest.get("recommendation_count", 0),
            "best_model": rec.get("best_model"),
            "keep_models": rec.get("keep_models", []),
            "remove_models": rec.get("remove_models", []),
        }

    def get_package(self) -> Dict[str, Any]:
        return {"ok": True, "mode": "ollama_model_benchmark_package", "package": {"status": self.get_status(), "panel": self.panel(), "latest": self.latest()}}


ollama_model_benchmark_service = OllamaModelBenchmarkService()
