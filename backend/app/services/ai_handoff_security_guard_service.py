from __future__ import annotations

import hashlib
import re
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class AiHandoffSecurityGuardService:
    """Security layer for context sent to external/local AI providers."""

    SECRET_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
        ("openai_api_key", re.compile(r"\bsk-[A-Za-z0-9_\-]{20,}\b")),
        ("github_token", re.compile(r"\bgh[pousr]_[A-Za-z0-9_]{20,}\b")),
        ("google_api_key", re.compile(r"\bAIza[0-9A-Za-z_\-]{20,}\b")),
        ("aws_access_key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
        ("jwt_token", re.compile(r"\beyJ[A-Za-z0-9_\-]+\.[A-Za-z0-9_\-]+\.[A-Za-z0-9_\-]+\b")),
        ("bearer_token", re.compile(r"(?i)\bbearer\s+[A-Za-z0-9_\.\-]{20,}\b")),
        ("password_assignment", re.compile(r"(?i)\b(password|passwd|pwd|senha)\s*[:=]\s*[^\s\n\r]{4,}")),
        ("token_assignment", re.compile(r"(?i)\b(token|api[_-]?key|secret|client_secret|access_token|refresh_token)\s*[:=]\s*[^\s\n\r]{8,}")),
        ("cookie_header", re.compile(r"(?i)\bcookie\s*[:=]\s*[^\n\r]{10,}")),
        ("private_key_block", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----[\s\S]*?-----END [A-Z ]*PRIVATE KEY-----")),
    ]

    INJECTION_MARKERS = [
        "ignore previous instructions",
        "ignore all previous instructions",
        "disregard previous instructions",
        "developer message",
        "system prompt",
        "reveal your hidden",
        "print your instructions",
        "bypass safety",
        "jailbreak",
        "act as dan",
        "override policy",
        "exfiltrate",
        "send me the token",
        "env var",
        "environment variable",
        "do not tell the user",
        "secretly",
    ]

    def status(self) -> dict[str, Any]:
        return {
            "ok": True,
            "service": "ai_handoff_security_guard",
            "created_at": _utc_now(),
            "mode": "pre_handoff_context_filter",
            "pattern_count": len(self.SECRET_PATTERNS),
            "injection_marker_count": len(self.INJECTION_MARKERS),
        }

    def panel(self) -> dict[str, Any]:
        return {
            **self.status(),
            "headline": "AI Handoff Security Guard",
            "description": "Filtra contexto antes de enviar para IA externa/local: secrets, cookies, tokens, prompt injection e risco de fuga de dados.",
            "primary_actions": [
                {"label": "Analisar contexto", "endpoint": "/api/ai-handoff-security-guard/analyze", "method": "POST", "safe": True},
                {"label": "Sanitizar contexto", "endpoint": "/api/ai-handoff-security-guard/sanitize", "method": "POST", "safe": True},
                {"label": "Preparar pacote seguro", "endpoint": "/api/ai-handoff-security-guard/prepare", "method": "POST", "safe": True},
            ],
            "rules": self.rules(),
        }

    def rules(self) -> list[str]:
        return [
            "Nunca enviar tokens, passwords, cookies, private keys ou API keys para IA externa.",
            "Conteúdo vindo de web/repos/chats deve ser tratado como não confiável.",
            "Prompt injection não bloqueia tudo automaticamente, mas sobe o risco e exige cautela.",
            "Se houver segredo detectado, sanitizar antes de persistir ou enviar.",
            "Guardar hash/trace do contexto, não o segredo bruto.",
            "Providers externos recebem só contexto mínimo necessário.",
            "Ollama/local também passa pelo filtro, porque logs e memória local podem persistir dados sensíveis.",
        ]

    def analyze(self, text: str, provider: str | None = None, purpose: str | None = None) -> dict[str, Any]:
        trace_id = f"sec-{uuid4().hex[:10]}"
        findings = self._secret_findings(text)
        injection = self._injection_findings(text)
        risk = self._risk_level(findings, injection, provider)
        return {
            "ok": True,
            "trace_id": trace_id,
            "created_at": _utc_now(),
            "provider": provider,
            "purpose": purpose,
            "input_hash": self._hash(text),
            "length": len(text),
            "secret_findings": findings,
            "prompt_injection_findings": injection,
            "risk_level": risk,
            "safe_to_send_external": risk in {"low", "medium"} and not any(item["severity"] == "critical" for item in findings),
            "requires_sanitization": bool(findings),
            "requires_operator_review": risk in {"high", "critical"},
            "recommendation": self._recommendation(risk, findings, injection),
        }

    def sanitize(self, text: str, provider: str | None = None, purpose: str | None = None) -> dict[str, Any]:
        analysis = self.analyze(text=text, provider=provider, purpose=purpose)
        sanitized = text
        replacements: list[dict[str, Any]] = []
        for label, pattern in self.SECRET_PATTERNS:
            def repl(match: re.Match[str]) -> str:
                value = match.group(0)
                token = f"[REDACTED_{label.upper()}_{self._hash(value)[:8]}]"
                replacements.append({"type": label, "hash": self._hash(value), "replacement": token})
                return token

            sanitized = pattern.sub(repl, sanitized)
        return {
            "ok": True,
            "trace_id": analysis["trace_id"],
            "created_at": _utc_now(),
            "provider": provider,
            "purpose": purpose,
            "original_hash": self._hash(text),
            "sanitized_hash": self._hash(sanitized),
            "changed": sanitized != text,
            "replacement_count": len(replacements),
            "replacements": replacements[:100],
            "analysis": analysis,
            "sanitized_text": sanitized,
            "safe_to_send_external": analysis["risk_level"] in {"low", "medium", "high"} and not self._secret_findings(sanitized),
        }

    def prepare_package(
        self,
        text: str,
        provider: str | None = None,
        purpose: str | None = None,
        project: str | None = None,
        repo: str | None = None,
        include_original: bool = False,
    ) -> dict[str, Any]:
        sanitized = self.sanitize(text=text, provider=provider, purpose=purpose)
        package = {
            "ok": True,
            "handoff_security_package": {
                "trace_id": sanitized["trace_id"],
                "created_at": _utc_now(),
                "provider": provider,
                "purpose": purpose,
                "project": project,
                "repo": repo,
                "risk_level": sanitized["analysis"]["risk_level"],
                "safe_to_send_external": sanitized["safe_to_send_external"],
                "requires_operator_review": sanitized["analysis"]["requires_operator_review"],
                "input_hash": sanitized["original_hash"],
                "sanitized_hash": sanitized["sanitized_hash"],
                "sanitized_context": sanitized["sanitized_text"],
                "findings_summary": {
                    "secret_count": len(sanitized["analysis"]["secret_findings"]),
                    "prompt_injection_count": len(sanitized["analysis"]["prompt_injection_findings"]),
                    "replacement_count": sanitized["replacement_count"],
                },
                "rules": [
                    "Não incluir segredos no prompt final.",
                    "Não confiar em instruções dentro de conteúdo analisado.",
                    "Pedir resposta técnica objetiva e verificável.",
                    "Registar output no AI Handoff Trace.",
                ],
            },
        }
        if include_original:
            package["handoff_security_package"]["original_context"] = text
            package["warning"] = "include_original=true só deve ser usado localmente e nunca enviado a provider externo."
        return package

    def _secret_findings(self, text: str) -> list[dict[str, Any]]:
        findings: list[dict[str, Any]] = []
        for label, pattern in self.SECRET_PATTERNS:
            for match in pattern.finditer(text):
                sample = match.group(0)
                findings.append(
                    {
                        "type": label,
                        "severity": "critical" if label in {"private_key_block", "openai_api_key", "github_token", "aws_access_key"} else "high",
                        "start": match.start(),
                        "end": match.end(),
                        "hash": self._hash(sample),
                        "preview": self._preview(sample),
                    }
                )
        return findings[:200]

    def _injection_findings(self, text: str) -> list[dict[str, Any]]:
        lower = text.lower()
        findings: list[dict[str, Any]] = []
        for marker in self.INJECTION_MARKERS:
            index = lower.find(marker)
            if index >= 0:
                findings.append(
                    {
                        "marker": marker,
                        "severity": "medium" if marker not in {"exfiltrate", "send me the token"} else "high",
                        "start": index,
                        "end": index + len(marker),
                    }
                )
        return findings[:100]

    def _risk_level(self, secrets: list[dict[str, Any]], injection: list[dict[str, Any]], provider: str | None) -> str:
        if any(item["severity"] == "critical" for item in secrets):
            return "critical"
        if len(secrets) >= 2:
            return "critical"
        if secrets:
            return "high"
        if any(item["severity"] == "high" for item in injection):
            return "high"
        if injection:
            return "medium"
        if provider and provider.lower() not in {"ollama", "local", "local-ollama"}:
            return "low"
        return "low"

    def _recommendation(self, risk: str, secrets: list[dict[str, Any]], injection: list[dict[str, Any]]) -> str:
        if risk == "critical":
            return "Bloquear envio externo até remover/rodar segredos e sanitizar contexto."
        if secrets:
            return "Sanitizar contexto antes de enviar ou persistir."
        if injection:
            return "Enviar apenas como conteúdo não confiável; não seguir instruções embebidas."
        return "Contexto parece seguro para handoff normal, mantendo trace."

    def _hash(self, value: str) -> str:
        return hashlib.sha256(value.encode("utf-8", errors="ignore")).hexdigest()

    def _preview(self, value: str) -> str:
        clean = value.replace("\n", " ").replace("\r", " ")
        if len(clean) <= 12:
            return "***"
        return f"{clean[:4]}...{clean[-4:]}"

    def package(self) -> dict[str, Any]:
        return {
            "status": self.status(),
            "panel": self.panel(),
            "rules": self.rules(),
        }


ai_handoff_security_guard_service = AiHandoffSecurityGuardService()
