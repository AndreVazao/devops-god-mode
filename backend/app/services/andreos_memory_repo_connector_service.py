from __future__ import annotations

from datetime import datetime, timezone
from pathlib import PurePosixPath
from typing import Any

from app.services.github_service import github_service


REPOSITORY_FULL_NAME = "AndreVazao/andreos-memory"
DEFAULT_BRANCH = "main"
VAULT_ROOT = "AndreOS"
APPROVAL_PHRASE = "SYNC ANDREOS MEMORY"

BASE_PROJECTS: dict[str, dict[str, Any]] = {
    "GOD_MODE": {
        "display_name": "God Mode",
        "priority": "principal",
        "folder": "AndreOS/02_PROJETOS/GOD_MODE",
        "required_files": [
            "MEMORIA_MESTRE.md",
            "DECISOES.md",
            "ARQUITETURA.md",
            "BACKLOG.md",
            "HISTORICO.md",
            "ULTIMA_SESSAO.md",
            "PROMPTS.md",
            "ERROS.md",
        ],
    },
    "PROVENTIL": {
        "display_name": "ProVentil",
        "priority": "principal",
        "folder": "AndreOS/02_PROJETOS/PROVENTIL",
        "required_files": ["MEMORIA_MESTRE.md"],
    },
    "VERBAFORGE": {
        "display_name": "VerbaForge",
        "priority": "principal",
        "folder": "AndreOS/02_PROJETOS/VERBAFORGE",
        "required_files": ["MEMORIA_MESTRE.md"],
    },
    "BOT_LORDS_MOBILE": {
        "display_name": "Bot Lords Mobile",
        "priority": "principal",
        "folder": "AndreOS/02_PROJETOS/BOT_LORDS_MOBILE",
        "required_files": ["MEMORIA_MESTRE.md"],
    },
    "ECU_REPRO": {
        "display_name": "ECU Repro",
        "priority": "principal",
        "folder": "AndreOS/02_PROJETOS/ECU_REPRO",
        "required_files": ["MEMORIA_MESTRE.md"],
    },
    "BUILD_CONTROL_CENTER": {
        "display_name": "Build Control Center",
        "priority": "apoio",
        "folder": "AndreOS/02_PROJETOS/BUILD_CONTROL_CENTER",
        "required_files": ["MEMORIA_MESTRE.md"],
    },
    "PERSONA_FORGE": {
        "display_name": "Persona Forge",
        "priority": "principal",
        "folder": "AndreOS/02_PROJETOS/PERSONA_FORGE",
        "required_files": ["MEMORIA_MESTRE.md", "BACKLOG.md", "ULTIMA_SESSAO.md"],
        "seed_needed": True,
    },
    "VOX": {
        "display_name": "Vox",
        "priority": "principal",
        "folder": "AndreOS/02_PROJETOS/VOX",
        "required_files": ["MEMORIA_MESTRE.md", "BACKLOG.md", "ULTIMA_SESSAO.md"],
        "seed_needed": True,
    },
    "BOT_FACTORY": {
        "display_name": "Bot Factory",
        "priority": "principal",
        "folder": "AndreOS/02_PROJETOS/BOT_FACTORY",
        "required_files": ["MEMORIA_MESTRE.md", "ARQUITETURA.md", "BACKLOG.md", "ULTIMA_SESSAO.md"],
        "seed_needed": True,
    },
}

GLOBAL_FILES = [
    "README.md",
    "AndreOS/00_INBOX/README.md",
    "AndreOS/01_MEMORIA_NUCLEAR/PERFIL_ANDRE.md",
    "AndreOS/01_MEMORIA_NUCLEAR/REGRAS_GERAIS_DA_IA.md",
    "AndreOS/01_MEMORIA_NUCLEAR/STACK_PADRAO.md",
    "AndreOS/01_MEMORIA_NUCLEAR/SEGURANCA_E_PERMISSOES.md",
    "AndreOS/01_MEMORIA_NUCLEAR/DECISOES_GLOBAIS.md",
    "AndreOS/01_MEMORIA_NUCLEAR/MODELO_DE_NEGOCIO.md",
    "AndreOS/05_LOGS_IA/ACOES_EXECUTADAS.md",
    "AndreOS/templates/PROJECT_MEMORY_TEMPLATE.md",
    "AndreOS/templates/DECISOES_TEMPLATE.md",
    "AndreOS/templates/BACKLOG_TEMPLATE.md",
    "AndreOS/templates/ULTIMA_SESSAO_TEMPLATE.md",
    "AndreOS/memory.config.json",
]


class AndreOSMemoryRepoConnectorService:
    def status(self) -> dict[str, Any]:
        return {
            "ok": True,
            "service": "andreos_memory_repo_connector",
            "repository_full_name": REPOSITORY_FULL_NAME,
            "visibility_expected": "private",
            "default_branch": DEFAULT_BRANCH,
            "vault_root": VAULT_ROOT,
            "github_backend_configured": github_service.is_configured(),
            "approval_phrase": APPROVAL_PHRASE,
            "mode": "external_memory_repo_bridge",
        }

    def panel(self) -> dict[str, Any]:
        return {
            **self.status(),
            "headline": "AndreOS Memory Repo ligado ao God Mode",
            "description": "Usa o repo privado AndreVazao/andreos-memory como memória Markdown persistente para Obsidian, ChatGPT, God Mode e outros providers.",
            "primary_actions": [
                {
                    "label": "Ver estrutura AndreOS",
                    "endpoint": "/api/andreos-memory-repo/structure",
                    "method": "GET",
                    "safe": True,
                },
                {
                    "label": "Auditar memória externa",
                    "endpoint": "/api/andreos-memory-repo/audit",
                    "method": "GET",
                    "safe": True,
                },
                {
                    "label": "Ler projeto GOD_MODE",
                    "endpoint": "/api/andreos-memory-repo/project/GOD_MODE",
                    "method": "GET",
                    "safe": True,
                },
                {
                    "label": "Plano de seed dos projetos em falta",
                    "endpoint": "/api/andreos-memory-repo/seed-plan",
                    "method": "GET",
                    "safe": True,
                },
            ],
            "operator_rule": "Ler é seguro. Escrever no repo de memória exige confirmação explícita e nunca deve gravar dados sensíveis.",
        }

    def structure(self) -> dict[str, Any]:
        projects: list[dict[str, Any]] = []
        for project_id, project in BASE_PROJECTS.items():
            projects.append(
                {
                    "project_id": project_id,
                    "display_name": project["display_name"],
                    "priority": project["priority"],
                    "folder": project["folder"],
                    "required_paths": [
                        f"{project['folder']}/{filename}" for filename in project["required_files"]
                    ],
                    "seed_needed": bool(project.get("seed_needed", False)),
                }
            )
        return {
            "ok": True,
            "repository_full_name": REPOSITORY_FULL_NAME,
            "global_files": GLOBAL_FILES,
            "projects": projects,
        }

    def _safe_path(self, path: str) -> bool:
        if not path or path.startswith("/"):
            return False
        parsed = PurePosixPath(path)
        if ".." in parsed.parts:
            return False
        allowed_prefixes = ("AndreOS/", "README.md")
        if not any(path == prefix or path.startswith(prefix) for prefix in allowed_prefixes):
            return False
        lowered = path.lower()
        blocked_markers = [
            ".env",
            "id_rsa",
            "private_key",
            "credential",
            "secrets",
            "cookies",
        ]
        return not any(marker in lowered for marker in blocked_markers)

    def _assert_safe_path(self, path: str) -> None:
        if not self._safe_path(path):
            raise ValueError("unsafe_memory_repo_path")

    def _redact_payload(self, value: str) -> str:
        lines = value.splitlines()
        cleaned: list[str] = []
        blocked_markers = [
            "authorization:",
            "bearer ",
            "api_key",
            "apikey",
            "password=",
            "token=",
            "cookie=",
            "-----begin",
        ]
        for line in lines:
            lowered = line.lower()
            if any(marker in lowered for marker in blocked_markers):
                cleaned.append("[REDACTED AndreOS memory connector]")
            else:
                cleaned.append(line)
        return "\n".join(cleaned).strip() + "\n"

    async def read_path(self, path: str) -> dict[str, Any]:
        self._assert_safe_path(path)
        if not github_service.is_configured():
            return {
                "ok": False,
                "repository_full_name": REPOSITORY_FULL_NAME,
                "path": path,
                "error_type": "github_backend_not_configured",
                "message": "O backend local ainda não tem configuração GitHub para ler o repo privado.",
            }
        return await github_service.get_repository_file(REPOSITORY_FULL_NAME, path, ref=DEFAULT_BRANCH)

    async def read_project(self, project_id: str) -> dict[str, Any]:
        normalized = project_id.strip().upper()
        project = BASE_PROJECTS.get(normalized)
        if not project:
            return {
                "ok": False,
                "error_type": "unknown_project",
                "project_id": normalized,
                "known_projects": sorted(BASE_PROJECTS.keys()),
            }
        results: list[dict[str, Any]] = []
        missing: list[str] = []
        for filename in project["required_files"]:
            path = f"{project['folder']}/{filename}"
            result = await self.read_path(path)
            results.append(
                {
                    "path": path,
                    "ok": result.get("ok", False),
                    "file_status": result.get("file_status"),
                    "sha": result.get("sha"),
                    "size": result.get("size"),
                    "preview": (result.get("content_text") or "")[:1200] if result.get("ok") else None,
                    "error_type": result.get("error_type"),
                }
            )
            if not result.get("ok"):
                missing.append(path)
        return {
            "ok": len(missing) == 0,
            "partial": len(missing) > 0,
            "project_id": normalized,
            "project": project,
            "files": results,
            "missing_paths": missing,
        }

    async def audit(self) -> dict[str, Any]:
        global_results: list[dict[str, Any]] = []
        missing_global: list[str] = []
        for path in GLOBAL_FILES:
            result = await self.read_path(path)
            global_results.append(
                {
                    "path": path,
                    "ok": result.get("ok", False),
                    "sha": result.get("sha"),
                    "size": result.get("size"),
                    "error_type": result.get("error_type"),
                }
            )
            if not result.get("ok"):
                missing_global.append(path)

        project_results: list[dict[str, Any]] = []
        missing_project_paths: list[str] = []
        for project_id in BASE_PROJECTS:
            result = await self.read_project(project_id)
            project_results.append(
                {
                    "project_id": project_id,
                    "ok": result.get("ok", False),
                    "partial": result.get("partial", False),
                    "missing_paths": result.get("missing_paths", []),
                    "seed_needed": bool(BASE_PROJECTS[project_id].get("seed_needed", False)),
                }
            )
            missing_project_paths.extend(result.get("missing_paths", []))

        return {
            "ok": not missing_global and not missing_project_paths,
            "partial": bool(missing_global or missing_project_paths),
            "repository_full_name": REPOSITORY_FULL_NAME,
            "github_backend_configured": github_service.is_configured(),
            "missing_global_paths": missing_global,
            "missing_project_paths": missing_project_paths,
            "global_results": global_results,
            "project_results": project_results,
            "next_action": "seed_missing_project_files" if missing_project_paths else "memory_repo_ready",
        }

    def seed_plan(self) -> dict[str, Any]:
        items: list[dict[str, Any]] = []
        for project_id, project in BASE_PROJECTS.items():
            if not project.get("seed_needed"):
                continue
            for filename in project["required_files"]:
                path = f"{project['folder']}/{filename}"
                items.append(
                    {
                        "project_id": project_id,
                        "path": path,
                        "action": "create_if_missing",
                        "content_template": self._template_for(project_id, filename),
                    }
                )
        return {
            "ok": True,
            "repository_full_name": REPOSITORY_FULL_NAME,
            "approval_phrase": APPROVAL_PHRASE,
            "items": items,
            "safe": True,
            "destructive": False,
        }

    def _template_for(self, project_id: str, filename: str) -> str:
        project = BASE_PROJECTS[project_id]
        now = datetime.now(timezone.utc).isoformat()
        title = project["display_name"]
        if filename == "MEMORIA_MESTRE.md":
            return f"# {title} — Memória Mestre\n\n## Estado\n\nA iniciar memória AndreOS para este projeto.\n\n## Objetivo\n\nDefinir e manter contexto persistente para o projeto {title}.\n\n## Última atualização\n\n{now}\n"
        if filename == "BACKLOG.md":
            return f"# {title} — Backlog\n\n## Próximas ações\n\n- Consolidar contexto do projeto.\n- Ligar conversas e repos relevantes.\n\n## Última atualização\n\n{now}\n"
        if filename == "ULTIMA_SESSAO.md":
            return f"# {title} — Última Sessão\n\nAinda sem sessão registada pelo God Mode.\n\nÚltima atualização: {now}\n"
        if filename == "ARQUITETURA.md":
            return f"# {title} — Arquitetura\n\nArquitetura ainda a mapear pelo God Mode.\n\nÚltima atualização: {now}\n"
        return f"# {title} — {filename}\n\nCriado pelo AndreOS Memory Repo Connector.\n\nÚltima atualização: {now}\n"

    async def write_memory_note(
        self,
        project_id: str,
        target_file: str,
        content: str,
        approval_phrase: str,
        mode: str = "append",
    ) -> dict[str, Any]:
        if approval_phrase != APPROVAL_PHRASE:
            return {
                "ok": False,
                "error_type": "approval_required",
                "required_phrase": APPROVAL_PHRASE,
            }
        normalized = project_id.strip().upper()
        project = BASE_PROJECTS.get(normalized)
        if not project:
            return {"ok": False, "error_type": "unknown_project", "project_id": normalized}
        if target_file not in project["required_files"]:
            return {
                "ok": False,
                "error_type": "target_file_not_allowed_for_project",
                "allowed_files": project["required_files"],
            }
        path = f"{project['folder']}/{target_file}"
        self._assert_safe_path(path)
        if not github_service.is_configured():
            return {
                "ok": False,
                "error_type": "github_backend_not_configured",
                "message": "Configura o acesso GitHub no backend local para escrever no repo privado.",
            }
        cleaned = self._redact_payload(content)
        existing = await github_service.get_repository_file(REPOSITORY_FULL_NAME, path, ref=DEFAULT_BRANCH)
        existing_text = existing.get("content_text") if existing.get("ok") else ""
        sha = existing.get("sha") if existing.get("ok") else None
        now = datetime.now(timezone.utc).isoformat()
        if mode == "replace":
            new_text = cleaned
        else:
            new_text = (existing_text or "").rstrip() + f"\n\n---\n\n## Registo God Mode — {now}\n\n" + cleaned
        return await github_service.create_or_update_repository_file(
            repository_full_name=REPOSITORY_FULL_NAME,
            path=path,
            content_text=new_text,
            commit_message=f"AndreOS memory update: {normalized} {target_file}",
            branch=DEFAULT_BRANCH,
            sha=sha,
        )

    async def seed_missing_projects(self, approval_phrase: str) -> dict[str, Any]:
        if approval_phrase != APPROVAL_PHRASE:
            return {
                "ok": False,
                "error_type": "approval_required",
                "required_phrase": APPROVAL_PHRASE,
            }
        if not github_service.is_configured():
            return {
                "ok": False,
                "error_type": "github_backend_not_configured",
            }
        written: list[dict[str, Any]] = []
        skipped: list[dict[str, Any]] = []
        for item in self.seed_plan()["items"]:
            path = item["path"]
            existing = await github_service.get_repository_file(REPOSITORY_FULL_NAME, path, ref=DEFAULT_BRANCH)
            if existing.get("ok"):
                skipped.append({"path": path, "reason": "already_exists"})
                continue
            result = await github_service.create_or_update_repository_file(
                repository_full_name=REPOSITORY_FULL_NAME,
                path=path,
                content_text=item["content_template"],
                commit_message=f"AndreOS seed: {item['project_id']} {PurePosixPath(path).name}",
                branch=DEFAULT_BRANCH,
            )
            written.append(result)
        return {
            "ok": True,
            "written_count": len(written),
            "skipped_count": len(skipped),
            "written": written,
            "skipped": skipped,
        }

    def handoff_prompt(self, project_id: str = "GOD_MODE") -> dict[str, Any]:
        normalized = project_id.strip().upper()
        return {
            "ok": True,
            "project_id": normalized,
            "prompt": (
                "Usa a memória AndreOS no repo AndreVazao/andreos-memory antes de responder.\n"
                f"Projeto: {normalized}.\n"
                "Pedido: continua com base no contexto persistente, sem guardar dados sensíveis."
            ),
        }

    async def package(self) -> dict[str, Any]:
        return {
            "status": self.status(),
            "panel": self.panel(),
            "structure": self.structure(),
            "seed_plan": self.seed_plan(),
            "handoff_prompt": self.handoff_prompt("GOD_MODE"),
        }


andreos_memory_repo_connector_service = AndreOSMemoryRepoConnectorService()
