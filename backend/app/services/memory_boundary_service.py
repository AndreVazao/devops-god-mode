from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class MemoryBoundaryService:
    """Defines the operational boundary between GitHub memory and local Obsidian memory."""

    def status(self) -> dict[str, Any]:
        return {
            "ok": True,
            "service": "memory_boundary",
            "created_at": _utc_now(),
            "github_memory": {
                "role": "programming_repo_memory",
                "primary_repo": "AndreVazao/andreos-memory",
                "purpose": "Programação, engenharia, arquitetura, PRs, builds, bugs e estado técnico das repos/programas.",
                "source_of_truth_for": [
                    "estado técnico das repos",
                    "arquitetura dos programas",
                    "decisões de implementação",
                    "backlog técnico",
                    "histórico de PRs/builds/releases",
                    "prompts técnicos para IA externa",
                ],
                "must_not_store": [
                    "tokens",
                    "passwords",
                    "cookies",
                    "chaves API",
                    "notas privadas sem relação técnica",
                ],
            },
            "obsidian_memory": {
                "role": "local_operational_evolution_memory",
                "purpose": "Trabalho local, operação diária, evolução, prioridades, observações reais do PC/APK e aprendizagem local.",
                "source_of_truth_for": [
                    "prioridades atuais do André",
                    "observações locais de testes",
                    "notas em progresso",
                    "tarefas locais",
                    "aprendizagem local do God Mode",
                    "contexto que ainda não deve ir para GitHub",
                ],
                "sync_to_github_when": [
                    "vira bug técnico",
                    "vira feature",
                    "vira decisão de arquitetura",
                    "vira alteração de repo",
                    "vira requisito de build/release",
                ],
            },
            "orchestrator": "God Mode",
        }

    def panel(self) -> dict[str, Any]:
        status = self.status()
        return {
            **status,
            "headline": "Memória: GitHub para código, Obsidian para trabalho local",
            "description": "Separação rígida para o God Mode não misturar memória técnica de programação com memória operacional local.",
            "rules": self.rules(),
            "safe_actions": [
                {
                    "label": "Ver fronteira de memória",
                    "endpoint": "/api/memory-boundary/status",
                    "method": "GET",
                    "safe": True,
                },
                {
                    "label": "Preparar prompt para IA externa",
                    "endpoint": "/api/memory-boundary/ai-handoff-template",
                    "method": "POST",
                    "safe": True,
                },
                {
                    "label": "Classificar nota local",
                    "endpoint": "/api/memory-boundary/classify-note",
                    "method": "POST",
                    "safe": True,
                },
            ],
        }

    def rules(self) -> list[str]:
        return [
            "GitHub memory é para programação das repos e programas.",
            "Obsidian local é para trabalho local, operação e evolução contínua.",
            "O God Mode é o orquestrador das duas memórias.",
            "Para pedir código a uma IA, usar contexto técnico da GitHub memory.",
            "Para decidir prioridade local, usar Obsidian.",
            "Se houver conflito: GitHub vence no estado técnico; Obsidian vence nas prioridades/observações locais.",
            "Nada sensível vai para GitHub memory sem filtragem.",
            "Notas Obsidian só sobem para GitHub quando viram requisito técnico, bug, feature, decisão, PR ou release.",
        ]

    def classify_note(self, title: str, body: str | None = None) -> dict[str, Any]:
        text = f"{title}\n{body or ''}".lower()
        technical_markers = [
            "repo",
            "github",
            "branch",
            "pull request",
            "pr",
            "commit",
            "build",
            "workflow",
            "artifact",
            "script",
            "backend",
            "frontend",
            "api",
            "endpoint",
            "bug",
            "erro",
            "feature",
            "arquitetura",
            "release",
        ]
        local_markers = [
            "pc",
            "telemóvel",
            "apk",
            "obsidian",
            "prioridade",
            "testei",
            "instalei",
            "local",
            "uso diário",
            "nota",
            "ideia",
        ]
        technical_score = sum(1 for marker in technical_markers if marker in text)
        local_score = sum(1 for marker in local_markers if marker in text)
        if technical_score > local_score:
            target = "github_memory"
        elif local_score > technical_score:
            target = "obsidian_memory"
        else:
            target = "obsidian_memory_first_then_review"
        return {
            "ok": True,
            "title": title,
            "target": target,
            "technical_score": technical_score,
            "local_score": local_score,
            "recommendation": self._recommendation(target),
        }

    def _recommendation(self, target: str) -> str:
        if target == "github_memory":
            return "Guardar como memória técnica GitHub porque afeta programação/repo/build/release."
        if target == "obsidian_memory":
            return "Guardar no Obsidian local porque é operacional, local ou evolução em curso."
        return "Guardar primeiro no Obsidian e pedir reconciliação antes de sincronizar para GitHub."

    def ai_handoff_template(
        self,
        project: str,
        repo: str,
        goal: str,
        memory_path: str | None = None,
        branch_or_pr: str | None = None,
    ) -> dict[str, Any]:
        memory_path = memory_path or f"AndreOS/02_PROJETOS/{project.upper()}/MEMORIA_MESTRE.md"
        prompt = f"""Usa a memória técnica AndreOS antes de responder.

Projeto: {project}
Repo alvo: {repo}
Branch/PR: {branch_or_pr or 'a definir'}
Memória GitHub: AndreVazao/andreos-memory/{memory_path}

Objetivo:
{goal}

Regras:
- Não inventes estado do repo que não esteja confirmado.
- Não peças tokens, passwords, cookies ou chaves API.
- Se precisares de contexto operacional local, pede ao God Mode um resumo do Obsidian.
- Devolve alterações técnicas objetivas, ficheiros afetados, riscos e testes.
- No fim, indica o que deve ser registado na GitHub memory e o que deve ficar no Obsidian local.
""".strip()
        return {
            "ok": True,
            "project": project,
            "repo": repo,
            "memory_path": memory_path,
            "branch_or_pr": branch_or_pr,
            "goal": goal,
            "prompt": prompt,
            "write_back_rules": {
                "github_memory": "resultado técnico, decisão, ficheiros, PR, build, bug, release",
                "obsidian_memory": "observação local, prioridade, nota de teste real, evolução operacional",
            },
        }


memory_boundary_service = MemoryBoundaryService()
