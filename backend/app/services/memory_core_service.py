from __future__ import annotations

import json
import re
import urllib.parse
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

MEMORY_ROOT = Path("memory")
CONFIG_FILE = MEMORY_ROOT / "config" / "memory.config.json"
VAULT_ROOT = MEMORY_ROOT / "vault" / "AndreOS"
PROJECTS_ROOT = VAULT_ROOT / "02_PROJETOS"
LOGS_ROOT = VAULT_ROOT / "05_LOGS_IA"
PROJECT_FILES = [
    "MEMORIA_MESTRE.md",
    "DECISOES.md",
    "BACKLOG.md",
    "ROADMAP.md",
    "ARQUITETURA.md",
    "HISTORICO.md",
    "PROMPTS.md",
    "ERROS.md",
    "ULTIMA_SESSAO.md",
]
BASE_PROJECTS = ["GOD_MODE", "PROVENTIL", "VERBAFORGE", "BOT_LORDS_MOBILE", "ECU_REPRO", "BUILD_CONTROL_CENTER"]
DEFAULT_BLOCKED_KEYWORDS = [
    "password", "senha", "token", "api_key", "apikey", "secret", "client_secret", "private_key",
    "github_pat", "openai", "stripe_secret", "paypal_secret", "cookie", "authorization", "bearer",
]


class ApprovalGate:
    def __init__(self, blocked_keywords: List[str] | None = None) -> None:
        self.blocked_keywords = [item.lower() for item in (blocked_keywords or DEFAULT_BLOCKED_KEYWORDS)]

    def validate_safe_text(self, text: str) -> Dict[str, Any]:
        lowered = text.lower()
        hits = [keyword for keyword in self.blocked_keywords if re.search(rf"(?<![a-z0-9_]){re.escape(keyword)}(?![a-z0-9_])", lowered)]
        return {"ok": not hits, "blocked_keywords": hits, "message": "blocked_secret_keyword" if hits else "safe"}

    def require_non_destructive_or_approved(self, destructive: bool, approved: bool) -> Dict[str, Any]:
        if destructive and not approved:
            return {"ok": False, "error": "destructive_action_requires_explicit_approval"}
        return {"ok": True}


class MarkdownMemoryStore:
    def __init__(self, root: Path = MEMORY_ROOT) -> None:
        self.root = root

    def ensure_dir(self, path: Path) -> None:
        path.mkdir(parents=True, exist_ok=True)

    def read_text(self, path: Path) -> str:
        if not path.exists():
            return ""
        return path.read_text(encoding="utf-8")

    def write_text(self, path: Path, content: str) -> None:
        self.ensure_dir(path.parent)
        path.write_text(content, encoding="utf-8")

    def append_entry(self, path: Path, title: str, body: str) -> None:
        self.ensure_dir(path.parent)
        stamp = datetime.now(timezone.utc).isoformat()
        entry = f"\n\n## {title}\n\n- Data: {stamp}\n\n{body.strip()}\n"
        with path.open("a", encoding="utf-8") as handle:
            handle.write(entry)


class ObsidianUriWriter:
    def __init__(self, vault_name: str = "AndreOS") -> None:
        self.vault_name = vault_name

    def note_uri(self, note_path: str, content: str | None = None, append: bool = False) -> str:
        params = {"vault": self.vault_name, "file": note_path.replace("\\", "/")}
        if content is not None:
            params["content"] = content
        if append:
            params["append"] = "true"
        return "obsidian://new?" + urllib.parse.urlencode(params)

    def open_uri(self, note_path: str) -> str:
        return "obsidian://open?" + urllib.parse.urlencode({"vault": self.vault_name, "file": note_path.replace("\\", "/")})


class ProjectMemoryManager:
    def __init__(self, store: MarkdownMemoryStore, gate: ApprovalGate) -> None:
        self.store = store
        self.gate = gate

    def normalize_project(self, project_name: str) -> str:
        return re.sub(r"[^A-Z0-9_]+", "_", project_name.upper()).strip("_") or "GERAL"

    def project_dir(self, project_name: str) -> Path:
        return PROJECTS_ROOT / self.normalize_project(project_name)

    def create_project(self, project_name: str) -> Dict[str, Any]:
        normalized = self.normalize_project(project_name)
        folder = self.project_dir(normalized)
        self.store.ensure_dir(folder)
        for file_name in PROJECT_FILES:
            target = folder / file_name
            if not target.exists():
                self.store.write_text(target, self.default_file_content(normalized, file_name))
        return {"ok": True, "project": normalized, "path": str(folder), "files": PROJECT_FILES}

    def default_file_content(self, project: str, file_name: str) -> str:
        title = file_name.replace(".md", "").replace("_", " ")
        return f"# {project} - {title}\n\n> Memória persistente AndréOS para o projeto {project}.\n\n## Estado inicial\n\nCriado para manter continuidade, decisões, histórico, backlog, arquitetura, prompts, erros e última sessão.\n"

    def read_project_memory(self, project_name: str) -> Dict[str, str]:
        project = self.normalize_project(project_name)
        self.create_project(project)
        folder = self.project_dir(project)
        return {file_name: self.store.read_text(folder / file_name) for file_name in PROJECT_FILES}

    def append_to_file(self, project_name: str, file_name: str, title: str, body: str) -> Dict[str, Any]:
        validation = self.gate.validate_safe_text(f"{title}\n{body}")
        if not validation["ok"]:
            return {"ok": False, "error": validation["message"], "blocked_keywords": validation["blocked_keywords"]}
        project = self.normalize_project(project_name)
        self.create_project(project)
        self.store.append_entry(self.project_dir(project) / file_name, title, body)
        return {"ok": True, "project": project, "file": file_name}

    def update_last_session(self, project_name: str, summary: str, next_steps: str = "") -> Dict[str, Any]:
        validation = self.gate.validate_safe_text(f"{summary}\n{next_steps}")
        if not validation["ok"]:
            return {"ok": False, "error": validation["message"], "blocked_keywords": validation["blocked_keywords"]}
        project = self.normalize_project(project_name)
        self.create_project(project)
        content = f"# {project} - ÚLTIMA SESSÃO\n\n## Atualizado em\n{datetime.now(timezone.utc).isoformat()}\n\n## Resumo\n{summary.strip()}\n\n## Próximos passos\n{next_steps.strip() or 'Sem próximos passos definidos.'}\n"
        self.store.write_text(self.project_dir(project) / "ULTIMA_SESSAO.md", content)
        return {"ok": True, "project": project, "file": "ULTIMA_SESSAO.md"}


class DecisionLogger:
    def __init__(self, manager: ProjectMemoryManager) -> None:
        self.manager = manager

    def log_decision(self, project_name: str, decision: str, reason: str = "") -> Dict[str, Any]:
        return self.manager.append_to_file(project_name, "DECISOES.md", "Decisão registada", f"### Decisão\n{decision}\n\n### Motivo\n{reason or 'Não especificado.'}")


class ActionLogger:
    def __init__(self, manager: ProjectMemoryManager) -> None:
        self.manager = manager

    def log_history(self, project_name: str, action: str, result: str = "") -> Dict[str, Any]:
        return self.manager.append_to_file(project_name, "HISTORICO.md", "Alteração registada", f"### Ação\n{action}\n\n### Resultado\n{result or 'Registado.'}")

    def log_error(self, project_name: str, error: str, context: str = "") -> Dict[str, Any]:
        return self.manager.append_to_file(project_name, "ERROS.md", "Erro registado", f"### Erro\n{error}\n\n### Contexto\n{context or 'Não especificado.'}")


class ContextAssembler:
    def __init__(self, manager: ProjectMemoryManager, priority_files: List[str] | None = None) -> None:
        self.manager = manager
        self.priority_files = priority_files or ["MEMORIA_MESTRE.md", "DECISOES.md", "ARQUITETURA.md", "BACKLOG.md", "ULTIMA_SESSAO.md"]

    def compact_context(self, project_name: str, max_chars: int = 12000) -> Dict[str, Any]:
        memory = self.manager.read_project_memory(project_name)
        chunks: List[str] = []
        for file_name in self.priority_files:
            content = memory.get(file_name, "").strip()
            if content:
                chunks.append(f"\n<!-- {file_name} -->\n{content}")
        assembled = "\n".join(chunks).strip()
        if len(assembled) > max_chars:
            assembled = assembled[-max_chars:]
        return {"ok": True, "project": self.manager.normalize_project(project_name), "context": assembled, "chars": len(assembled)}


class MemoryBridge:
    def __init__(self) -> None:
        self.config = self.load_config()
        blocked = self.config.get("blocked_secret_keywords", DEFAULT_BLOCKED_KEYWORDS)
        self.gate = ApprovalGate(blocked)
        self.store = MarkdownMemoryStore()
        self.manager = ProjectMemoryManager(self.store, self.gate)
        self.decisions = DecisionLogger(self.manager)
        self.actions = ActionLogger(self.manager)
        self.context = ContextAssembler(self.manager, self.config.get("context_files_priority"))
        self.obsidian = ObsidianUriWriter(self.config.get("vault_name", "AndreOS"))

    def load_config(self) -> Dict[str, Any]:
        if CONFIG_FILE.exists():
            return json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
        return {"vault_name": "AndreOS", "default_project": "GOD_MODE", "blocked_secret_keywords": DEFAULT_BLOCKED_KEYWORDS}

    def ensure_structure(self) -> Dict[str, Any]:
        folders = [
            MEMORY_ROOT / "config", MEMORY_ROOT / "templates", MEMORY_ROOT / "schemas", VAULT_ROOT / "00_INBOX",
            VAULT_ROOT / "01_MEMORIA_NUCLEAR", PROJECTS_ROOT, VAULT_ROOT / "03_CODIGO", VAULT_ROOT / "04_NEGOCIOS",
            LOGS_ROOT, VAULT_ROOT / "99_ARQUIVO",
        ]
        for folder in folders:
            self.store.ensure_dir(folder)
        for project in BASE_PROJECTS:
            self.manager.create_project(project)
        return {"ok": True, "memory_root": str(MEMORY_ROOT), "vault_root": str(VAULT_ROOT), "projects": BASE_PROJECTS}


class MemoryCore:
    def __init__(self) -> None:
        self.bridge = MemoryBridge()

    def get_status(self) -> Dict[str, Any]:
        config = self.bridge.config
        return {"ok": True, "mode": "andreos_memory_core_status", "memory_name": config.get("memory_name", "AndreOS Memory Core"), "vault_root": str(VAULT_ROOT), "default_project": config.get("default_project", "GOD_MODE")}

    def initialize(self) -> Dict[str, Any]:
        return self.bridge.ensure_structure()

    def create_project(self, project_name: str) -> Dict[str, Any]:
        return self.bridge.manager.create_project(project_name)

    def read_project(self, project_name: str) -> Dict[str, Any]:
        return {"ok": True, "project": self.bridge.manager.normalize_project(project_name), "memory": self.bridge.manager.read_project_memory(project_name)}

    def write_decision(self, project_name: str, decision: str, reason: str = "") -> Dict[str, Any]:
        return self.bridge.decisions.log_decision(project_name, decision, reason)

    def write_history(self, project_name: str, action: str, result: str = "") -> Dict[str, Any]:
        return self.bridge.actions.log_history(project_name, action, result)

    def update_last_session(self, project_name: str, summary: str, next_steps: str = "") -> Dict[str, Any]:
        return self.bridge.manager.update_last_session(project_name, summary, next_steps)

    def add_backlog_task(self, project_name: str, task: str, priority: str = "medium") -> Dict[str, Any]:
        return self.bridge.manager.append_to_file(project_name, "BACKLOG.md", f"Tarefa {priority}", f"- [ ] {task.strip()}\n- Prioridade: {priority}")

    def compact_context(self, project_name: str, max_chars: int = 12000) -> Dict[str, Any]:
        return self.bridge.context.compact_context(project_name, max_chars=max_chars)

    def obsidian_link(self, project_name: str, file_name: str = "MEMORIA_MESTRE.md") -> Dict[str, Any]:
        project = self.bridge.manager.normalize_project(project_name)
        note_path = f"02_PROJETOS/{project}/{file_name}"
        return {"ok": True, "project": project, "file": file_name, "open_uri": self.bridge.obsidian.open_uri(note_path), "new_uri": self.bridge.obsidian.note_uri(note_path)}

    def get_package(self) -> Dict[str, Any]:
        self.initialize()
        return {"ok": True, "mode": "andreos_memory_core_package", "package": {"status": self.get_status(), "god_mode_context": self.compact_context("GOD_MODE", max_chars=6000)}}


memory_core_service = MemoryCore()
