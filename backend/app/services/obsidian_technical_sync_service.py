from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


TECHNICAL_MARKERS = [
    "repo",
    "github",
    "branch",
    "pr",
    "pull request",
    "commit",
    "build",
    "workflow",
    "artifact",
    "release",
    "backend",
    "frontend",
    "api",
    "endpoint",
    "route",
    "service",
    "script",
    "código",
    "codigo",
    "bug",
    "erro",
    "feature",
    "arquitetura",
    "módulo",
    "modulo",
    "biblioteca",
    "reutilizável",
    "reutilizavel",
    "ocr",
    "acr",
    "visão",
    "vision",
    "adb",
    "apk",
    "exe",
]

LOCAL_MARKERS = [
    "testei",
    "instalei",
    "pc",
    "telemóvel",
    "telefone",
    "local",
    "obsidian",
    "nota",
    "prioridade",
    "ideia",
    "uso diário",
    "evolução",
    "evolucao",
    "trabalho local",
]


class ObsidianTechnicalSyncService:
    """Classifies local Obsidian notes and prepares safe technical sync to GitHub memory."""

    def status(self) -> dict[str, Any]:
        return {
            "ok": True,
            "service": "obsidian_technical_sync",
            "created_at": _utc_now(),
            "role": "Obsidian é a oficina local; GitHub memory é o arquivo técnico estável.",
            "local_memory": "Obsidian",
            "technical_memory_repo": "AndreVazao/andreos-memory",
            "sync_direction": "obsidian_local_draft_to_github_technical_memory_when_stable",
        }

    def panel(self) -> dict[str, Any]:
        return {
            **self.status(),
            "headline": "Obsidian Technical Sync",
            "description": "Organiza primeiro no Obsidian e promove para GitHub memory só o que for técnico, estável e útil para programação.",
            "rules": self.rules(),
            "primary_actions": [
                {
                    "label": "Classificar nota Obsidian",
                    "endpoint": "/api/obsidian-technical-sync/classify",
                    "method": "POST",
                    "safe": True,
                },
                {
                    "label": "Preparar sync técnico",
                    "endpoint": "/api/obsidian-technical-sync/prepare-sync",
                    "method": "POST",
                    "safe": True,
                },
                {
                    "label": "Template de nota técnica",
                    "endpoint": "/api/obsidian-technical-sync/template",
                    "method": "GET",
                    "safe": True,
                },
            ],
        }

    def rules(self) -> list[str]:
        return [
            "Obsidian recebe primeiro notas técnicas em bruto, testes locais, pedidos, ideias e prompts.",
            "GitHub memory recebe apenas informação técnica estável necessária para programar/manter repos.",
            "O God Mode deve filtrar segredos antes de qualquer sync.",
            "Uma nota Obsidian só sobe para GitHub se virar bug, feature, decisão técnica, componente reutilizável, PR, build ou release.",
            "O sync deve guardar origem Obsidian, projeto, repo, propósito, estado e próximos passos.",
            "Se a nota ainda for especulativa, fica no Obsidian até maturar.",
            "Quando uma IA externa for chamada para código, o God Mode usa GitHub memory técnica como referência e Obsidian só como contexto local filtrado.",
        ]

    def classify(
        self,
        title: str,
        body: str | None = None,
        project: str | None = None,
        repo: str | None = None,
    ) -> dict[str, Any]:
        text = f"{title}\n{body or ''}".lower()
        technical_hits = [marker for marker in TECHNICAL_MARKERS if marker in text]
        local_hits = [marker for marker in LOCAL_MARKERS if marker in text]
        has_repo = bool(repo) or "repo" in text or "github" in text
        has_code = any(marker in text for marker in ["código", "codigo", "script", "endpoint", "api", "service", "backend", "frontend"])
        has_reusable = any(marker in text for marker in ["reutiliz", "já fiz", "ja fiz", "aproveitar", "adaptar", "componente"])
        stable_enough = has_repo or has_code or has_reusable or len(technical_hits) >= 2
        if stable_enough:
            target = "sync_candidate_to_github_memory"
        elif technical_hits and local_hits:
            target = "keep_in_obsidian_and_review_later"
        else:
            target = "obsidian_local_only"
        return {
            "ok": True,
            "title": title,
            "project": project,
            "repo": repo,
            "target": target,
            "technical_hits": technical_hits,
            "local_hits": local_hits,
            "stable_enough": stable_enough,
            "should_create_code_asset": has_reusable,
            "recommendation": self._recommendation(target, has_reusable),
        }

    def _recommendation(self, target: str, has_reusable: bool) -> str:
        if target == "sync_candidate_to_github_memory" and has_reusable:
            return "Promover para GitHub memory e criar/atualizar registo de código reutilizável."
        if target == "sync_candidate_to_github_memory":
            return "Promover para GitHub memory como decisão/bug/feature/estado técnico."
        if target == "keep_in_obsidian_and_review_later":
            return "Manter no Obsidian e rever quando virar requisito técnico estável."
        return "Manter apenas no Obsidian local por agora."

    def template(self, project: str = "GOD_MODE") -> dict[str, Any]:
        content = f"""# Nota Técnica Local — {project}

## Estado
- rascunho_local

## Objetivo

## Contexto local Obsidian

## Repo/programa afetado

## Ficheiros ou módulos relacionados

## Decisão técnica proposta

## Testes/observações locais

## Promover para GitHub memory?
- [ ] bug
- [ ] feature
- [ ] arquitetura
- [ ] componente reutilizável
- [ ] build/release
- [ ] não promover ainda

## Código reutilizável relacionado
- propósito:
- repo:
- ficheiros:
- etiquetas:

## MEMORY_DELTA técnico para GitHub

## Próximos passos
""".strip()
        return {
            "ok": True,
            "project": project,
            "template": content,
        }

    def prepare_sync(
        self,
        title: str,
        body: str,
        project: str,
        repo: str | None = None,
        source_obsidian_path: str | None = None,
        target_github_memory_path: str | None = None,
    ) -> dict[str, Any]:
        classification = self.classify(title=title, body=body, project=project, repo=repo)
        target_path = target_github_memory_path or f"AndreOS/02_PROJETOS/{project.upper()}/HISTORICO.md"
        technical_delta = self._technical_delta(
            title=title,
            body=body,
            project=project,
            repo=repo,
            source_obsidian_path=source_obsidian_path,
            target_path=target_path,
            classification=classification,
        )
        return {
            "ok": True,
            "classification": classification,
            "source": {
                "type": "obsidian_local_note",
                "path": source_obsidian_path,
            },
            "target": {
                "type": "github_technical_memory",
                "repo": "AndreVazao/andreos-memory",
                "path": target_path,
            },
            "technical_delta": technical_delta,
            "safe_to_auto_sync": classification["target"] == "sync_candidate_to_github_memory",
            "requires_secret_filter": True,
        }

    def _technical_delta(
        self,
        title: str,
        body: str,
        project: str,
        repo: str | None,
        source_obsidian_path: str | None,
        target_path: str,
        classification: dict[str, Any],
    ) -> str:
        excerpt = body.strip()
        if len(excerpt) > 1600:
            excerpt = excerpt[:1600].rstrip() + "..."
        return f"""## {title}

- Data: {_utc_now()}
- Projeto: {project}
- Repo: {repo or 'a definir'}
- Origem Obsidian: {source_obsidian_path or 'nota local não especificada'}
- Destino GitHub memory: {target_path}
- Classificação: {classification['target']}
- Criar/atualizar código reutilizável: {classification['should_create_code_asset']}

### Resumo técnico
{excerpt}

### Regras
- Este delta veio do Obsidian local.
- Foi promovido apenas como memória técnica de programação.
- Segredos devem ser filtrados antes de escrita real.
""".strip()


obsidian_technical_sync_service = ObsidianTechnicalSyncService()
