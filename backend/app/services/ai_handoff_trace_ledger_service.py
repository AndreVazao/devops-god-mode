from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from app.services.andreos_context_orchestrator_service import andreos_context_orchestrator_service
from app.utils.atomic_json_store import AtomicJsonStore


TRACE_STORE = Path("data/ai_handoff_trace_ledger.json")
APPROVAL_PHRASE = "TRACE AI HANDOFF"

PROJECT_REPO_HINTS = {
    "GOD_MODE": ["AndreVazao/devops-god-mode"],
    "PROVENTIL": ["AndreVazao/proventil", "AndreVazao/proventil.pt"],
    "VERBAFORGE": ["AndreVazao/verbaforge"],
    "BOT_LORDS_MOBILE": ["AndreVazao/bot-lords-mobile", "AndreVazao/lords-mobile-bot"],
    "ECU_REPRO": ["AndreVazao/ecu-repro"],
    "BUILD_CONTROL_CENTER": ["AndreVazao/build-control-center"],
    "PERSONA_FORGE": ["AndreVazao/persona-forge"],
    "VOX": ["AndreVazao/vox"],
    "BOT_FACTORY": ["AndreVazao/bot-factory"],
}


class AIHandoffTraceLedgerService:
    def __init__(self) -> None:
        self.store = AtomicJsonStore(TRACE_STORE, default={"events": [], "last": None})

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def _load(self) -> dict[str, Any]:
        payload = self.store.read()
        if not isinstance(payload, dict):
            return {"events": [], "last": None}
        payload.setdefault("events", [])
        return payload

    def _save_event(self, event: dict[str, Any]) -> dict[str, Any]:
        payload = self._load()
        events = payload.get("events", [])
        events.append(event)
        payload["events"] = events[-500:]
        payload["last"] = event
        self.store.write(payload)
        return event

    def status(self) -> dict[str, Any]:
        payload = self._load()
        return {
            "ok": True,
            "service": "ai_handoff_trace_ledger",
            "mode": "repo_memory_provider_handoff_trace",
            "trace_store": str(TRACE_STORE),
            "event_count": len(payload.get("events", [])),
            "last_event": payload.get("last"),
            "approval_phrase": APPROVAL_PHRASE,
        }

    def panel(self) -> dict[str, Any]:
        return {
            **self.status(),
            "headline": "AI Handoff Trace Ledger",
            "description": "Prepara pedidos para ChatGPT/outros providers com repo e memória AndreOS, e mantém rastreabilidade do que foi pedido e feito.",
            "primary_actions": [
                {
                    "label": "Preparar handoff GOD_MODE",
                    "endpoint": "/api/ai-handoff-trace/prepare",
                    "method": "POST",
                    "safe": True,
                },
                {
                    "label": "Ver ledger",
                    "endpoint": "/api/ai-handoff-trace/ledger",
                    "method": "GET",
                    "safe": True,
                },
                {
                    "label": "Política de rastreio",
                    "endpoint": "/api/ai-handoff-trace/policy",
                    "method": "GET",
                    "safe": True,
                },
            ],
        }

    def policy(self) -> dict[str, Any]:
        return {
            "ok": True,
            "rules": [
                "Toda conversa com IA sobre um projeto deve levar repo alvo e localização da memória AndreOS.",
                "Toda alteração proposta por IA deve voltar ao God Mode para validação, preview e PR.",
                "O provider não é fonte final de verdade; o God Mode reconcilia com repo/código real.",
                "Cada pedido externo deve gerar trace_id.",
                "Cada resposta importante deve ser registada como evento resumido.",
                "Nunca copiar dados sensíveis para o provider nem para memória Markdown.",
                "Se houver mudança de repo/app, ligar trace_id ao branch, PR, commit, artifact ou rollback.",
            ],
            "required_fields_for_handoff": [
                "trace_id",
                "project_id",
                "target_repo",
                "memory_repo",
                "memory_paths",
                "task",
                "context_pack",
                "return_format",
                "safety_rules",
            ],
            "return_contract": {
                "summary": "o que foi decidido/feito",
                "files_to_change": "lista de ficheiros sugeridos",
                "patch_strategy": "como aplicar sem destruir",
                "validation": "como testar",
                "risks": "riscos e bloqueios",
                "memory_delta": "resumo curto para AndreOS",
            },
        }

    def repo_hints(self, project_id: str) -> list[str]:
        normalized = andreos_context_orchestrator_service.normalize_project_id(project_id)
        return PROJECT_REPO_HINTS.get(normalized, [])

    async def prepare_handoff(
        self,
        project_id: str = "GOD_MODE",
        task: str = "Continuar o projeto com segurança.",
        provider: str = "chatgpt",
        target_repo: str | None = None,
        operator_note: str | None = None,
    ) -> dict[str, Any]:
        normalized = andreos_context_orchestrator_service.normalize_project_id(project_id)
        trace_id = f"handoff-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}-{uuid4().hex[:8]}"
        context_pack = await andreos_context_orchestrator_service.context_pack(normalized)
        repo_candidates = self.repo_hints(normalized)
        selected_repo = target_repo or (repo_candidates[0] if repo_candidates else "DEFINE_TARGET_REPO")
        memory_paths = []
        for item in context_pack.get("selected_files", []):
            path = item.get("path")
            if path:
                memory_paths.append(path)
        prompt = self._build_prompt(
            trace_id=trace_id,
            project_id=normalized,
            provider=provider,
            target_repo=selected_repo,
            repo_candidates=repo_candidates,
            memory_paths=memory_paths,
            task=task,
            operator_note=operator_note,
            compact_context=context_pack.get("compact_context", ""),
        )
        event = self._save_event(
            {
                "trace_id": trace_id,
                "type": "handoff_prepared",
                "created_at": self._now(),
                "project_id": normalized,
                "provider": provider,
                "target_repo": selected_repo,
                "repo_candidates": repo_candidates,
                "memory_repo": "AndreVazao/andreos-memory",
                "memory_paths": memory_paths,
                "task": task,
                "operator_note_present": bool(operator_note),
                "status": "prepared",
            }
        )
        return {
            "ok": True,
            "trace_id": trace_id,
            "project_id": normalized,
            "provider": provider,
            "target_repo": selected_repo,
            "repo_candidates": repo_candidates,
            "memory_repo": "AndreVazao/andreos-memory",
            "memory_paths": memory_paths,
            "prompt": prompt,
            "event": event,
            "next_action": "send_prompt_to_provider_then_record_result",
        }

    def _build_prompt(
        self,
        trace_id: str,
        project_id: str,
        provider: str,
        target_repo: str,
        repo_candidates: list[str],
        memory_paths: list[str],
        task: str,
        operator_note: str | None,
        compact_context: str,
    ) -> str:
        repo_list = "\n".join(f"- {repo}" for repo in repo_candidates) or "- DEFINE_TARGET_REPO"
        memory_list = "\n".join(f"- {path}" for path in memory_paths) or "- AndreOS/02_PROJETOS/{project_id}/MEMORIA_MESTRE.md"
        note_block = f"\nNota do operador:\n{operator_note}\n" if operator_note else ""
        return (
            f"Trace ID: {trace_id}\n"
            f"Provider alvo: {provider}\n"
            f"Projeto: {project_id}\n"
            f"Repo alvo principal: {target_repo}\n"
            "Repos relacionados possíveis:\n"
            f"{repo_list}\n\n"
            "Repo de memória persistente AndreOS:\n"
            "- AndreVazao/andreos-memory\n\n"
            "Ficheiros de memória relevantes:\n"
            f"{memory_list}\n\n"
            "Pedido do operador/God Mode:\n"
            f"{task}\n"
            f"{note_block}\n"
            "Regras obrigatórias:\n"
            "- Responder em Português de Portugal.\n"
            "- Considerar o repo alvo e a memória AndreOS antes de propor alterações.\n"
            "- Não inventar ficheiros, commits, branches ou estado que não esteja no contexto.\n"
            "- Não pedir nem guardar tokens, passwords, cookies, API keys ou segredos.\n"
            "- Se precisares mexer no código, devolver plano, ficheiros e patch/estratégia para o God Mode aplicar com PR.\n"
            "- Se houver risco, bloquear e explicar o motivo.\n"
            "- No fim devolver uma secção `MEMORY_DELTA` curta para guardar na memória AndreOS.\n\n"
            "Formato de resposta obrigatório:\n"
            "1. Resumo\n"
            "2. Decisão técnica\n"
            "3. Ficheiros/repos afetados\n"
            "4. Passos para o God Mode aplicar\n"
            "5. Testes/validação\n"
            "6. Riscos/bloqueios\n"
            "7. MEMORY_DELTA\n\n"
            "Contexto AndreOS compacto:\n"
            f"{compact_context}\n"
        )

    def record_result(
        self,
        trace_id: str,
        provider: str,
        project_id: str,
        summary: str,
        outcome: str = "received",
        target_repo: str | None = None,
        branch: str | None = None,
        pr_number: int | None = None,
        commit_sha: str | None = None,
        memory_delta: str | None = None,
    ) -> dict[str, Any]:
        normalized = andreos_context_orchestrator_service.normalize_project_id(project_id)
        event = self._save_event(
            {
                "trace_id": trace_id,
                "type": "provider_result_recorded",
                "created_at": self._now(),
                "provider": provider,
                "project_id": normalized,
                "target_repo": target_repo,
                "branch": branch,
                "pr_number": pr_number,
                "commit_sha": commit_sha,
                "summary": summary[:2000],
                "outcome": outcome,
                "memory_delta": (memory_delta or "")[:2000],
            }
        )
        return {"ok": True, "event": event, "next_action": "reconcile_validate_and_store_memory_delta"}

    def ledger(self, limit: int = 50, project_id: str | None = None) -> dict[str, Any]:
        payload = self._load()
        events = list(payload.get("events", []))
        if project_id:
            normalized = andreos_context_orchestrator_service.normalize_project_id(project_id)
            events = [event for event in events if event.get("project_id") == normalized]
        events = events[-max(1, min(limit, 200)):]
        return {
            "ok": True,
            "count": len(events),
            "events": events,
            "last": payload.get("last"),
        }

    def trace(self, trace_id: str) -> dict[str, Any]:
        payload = self._load()
        events = [event for event in payload.get("events", []) if event.get("trace_id") == trace_id]
        return {
            "ok": bool(events),
            "trace_id": trace_id,
            "events": events,
            "count": len(events),
        }

    async def package(self) -> dict[str, Any]:
        return {
            "status": self.status(),
            "panel": self.panel(),
            "policy": self.policy(),
            "ledger": self.ledger(limit=10),
        }


ai_handoff_trace_ledger_service = AIHandoffTraceLedgerService()
