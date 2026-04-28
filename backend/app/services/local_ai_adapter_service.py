from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from datetime import datetime, timezone
from typing import Any, Dict, List


class LocalAiAdapterService:
    """Optional local AI bridge for Ollama-compatible runtimes.

    The adapter is deliberately non-critical. If the local model is unavailable,
    God Mode keeps working with deterministic routing and cloud/remote logic.
    """

    DEFAULT_BASE_URL = "http://127.0.0.1:11434"
    DEFAULT_MODEL = "gemma2:2b"
    TIMEOUT_SECONDS = 3

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def _base_url(self) -> str:
        return os.environ.get("GODMODE_LOCAL_AI_URL", self.DEFAULT_BASE_URL).rstrip("/")

    def _model(self) -> str:
        return os.environ.get("GODMODE_LOCAL_AI_MODEL", self.DEFAULT_MODEL)

    def _request_json(self, path: str, payload: Dict[str, Any] | None = None, timeout: int | None = None) -> Dict[str, Any]:
        url = f"{self._base_url()}{path}"
        data = None
        headers = {"Content-Type": "application/json"}
        method = "GET"
        if payload is not None:
            data = json.dumps(payload).encode("utf-8")
            method = "POST"
        request = urllib.request.Request(url=url, data=data, headers=headers, method=method)
        with urllib.request.urlopen(request, timeout=timeout or self.TIMEOUT_SECONDS) as response:
            body = response.read().decode("utf-8")
        return json.loads(body) if body else {}

    def list_models(self) -> Dict[str, Any]:
        try:
            result = self._request_json("/api/tags")
            models = result.get("models", []) if isinstance(result, dict) else []
            names = [item.get("name") for item in models if item.get("name")]
            return {
                "ok": True,
                "mode": "local_ai_models",
                "base_url": self._base_url(),
                "model_count": len(names),
                "models": names,
                "recommended_model": self._recommended_model(names),
            }
        except Exception as exc:
            return {
                "ok": False,
                "mode": "local_ai_models",
                "base_url": self._base_url(),
                "error": exc.__class__.__name__,
                "detail": str(exc)[:220],
                "models": [],
                "recommended_model": self.DEFAULT_MODEL,
            }

    def _recommended_model(self, names: List[str]) -> str:
        lowered = {name.lower(): name for name in names}
        for preferred in ["gemma2:2b", "gemma:2b", "qwen2.5:3b", "llama3.2:3b", "phi3:mini"]:
            if preferred in lowered:
                return lowered[preferred]
        for name in names:
            low = name.lower()
            if "2b" in low or "3b" in low or "mini" in low:
                return name
        return names[0] if names else self.DEFAULT_MODEL

    def generate_short(self, prompt: str, model: str | None = None, max_chars: int = 700) -> Dict[str, Any]:
        safe_prompt = (prompt or "").strip()[:2500]
        if not safe_prompt:
            return {"ok": False, "mode": "local_ai_generate", "error": "empty_prompt"}
        selected_model = model or self._model()
        payload = {
            "model": selected_model,
            "prompt": safe_prompt,
            "stream": False,
            "options": {
                "temperature": 0.1,
                "num_predict": 180,
            },
        }
        try:
            result = self._request_json("/api/generate", payload=payload, timeout=8)
            text = (result.get("response") or "").strip()[:max_chars]
            return {
                "ok": bool(text),
                "mode": "local_ai_generate",
                "base_url": self._base_url(),
                "model": selected_model,
                "response": text,
                "chars": len(text),
            }
        except Exception as exc:
            return {
                "ok": False,
                "mode": "local_ai_generate",
                "base_url": self._base_url(),
                "model": selected_model,
                "error": exc.__class__.__name__,
                "detail": str(exc)[:220],
            }

    def classify_operator_text(self, text: str) -> Dict[str, Any]:
        prompt = (
            "Classifica esta ordem do operador para um backend DevOps local. "
            "Responde só com uma linha curta no formato: intent=<intent>; risk=<low|medium|high>; next=<short>.\n\n"
            f"Ordem: {text[:1200]}"
        )
        local = self.generate_short(prompt=prompt, max_chars=220)
        if local.get("ok"):
            return {"ok": True, "mode": "local_ai_classification", "source": "local_ai", "result": local.get("response"), "model": local.get("model")}
        fallback = self._deterministic_classification(text)
        return {"ok": True, "mode": "local_ai_classification", "source": "deterministic_fallback", "result": fallback, "local_ai_error": local.get("error")}

    def _deterministic_classification(self, text: str) -> str:
        low = (text or "").lower()
        if any(word in low for word in ["apaga", "delete", "remove", "destruir", "reset"]):
            return "intent=requires_review; risk=high; next=ask_operator_confirmation"
        if any(word in low for word in ["instalar", "apk", "exe", "ligar", "pc"]):
            return "intent=install_or_connect; risk=medium; next=open_start_now"
        if any(word in low for word in ["continua", "corrige", "arranja", "faz"]):
            return "intent=work_execution; risk=medium; next=route_daily_command"
        return "intent=status_or_summary; risk=low; next=show_home_summary"

    def build_panel(self) -> Dict[str, Any]:
        models = self.list_models()
        available = models.get("ok") is True and models.get("model_count", 0) > 0
        recommended = models.get("recommended_model") or self._model()
        return {
            "ok": True,
            "mode": "local_ai_panel",
            "created_at": self._now(),
            "status": "available" if available else "offline_or_not_installed",
            "base_url": self._base_url(),
            "default_model": self._model(),
            "recommended_model": recommended,
            "models": models.get("models", []),
            "model_count": models.get("model_count", 0),
            "benefits": [
                "resumos rápidos locais",
                "classificação de comandos",
                "explicação curta de erros",
                "funcionamento parcial sem internet",
                "menos dependência de IA externa em tarefas simples",
            ],
            "limits": [
                "não substitui revisão forte de código",
                "modelos pequenos podem alucinar",
                "ações críticas continuam a exigir validação do backend",
                "não guardar segredos no prompt local",
            ],
            "recommended_use": self._recommended_use(available=available, recommended_model=recommended),
            "models_probe": models,
        }

    def _recommended_use(self, available: bool, recommended_model: str) -> Dict[str, Any]:
        if not available:
            return {
                "enabled_for_autopilot": False,
                "label": "IA local opcional offline",
                "next": "Instalar/abrir Ollama no PC e usar modelo pequeno como gemma2:2b.",
            }
        return {
            "enabled_for_autopilot": True,
            "label": f"Usar {recommended_model} como ajudante local leve",
            "next": "Usar para resumir, classificar ordens e explicar erros; manter decisões críticas no backend validado.",
        }

    def get_status(self) -> Dict[str, Any]:
        panel = self.build_panel()
        return {
            "ok": True,
            "mode": "local_ai_status",
            "status": panel["status"],
            "base_url": panel["base_url"],
            "recommended_model": panel["recommended_model"],
            "model_count": panel["model_count"],
            "enabled_for_autopilot": panel["recommended_use"]["enabled_for_autopilot"],
        }

    def get_package(self) -> Dict[str, Any]:
        return {"ok": True, "mode": "local_ai_package", "package": {"status": self.get_status(), "panel": self.build_panel()}}


local_ai_adapter_service = LocalAiAdapterService()
