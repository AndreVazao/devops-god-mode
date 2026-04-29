from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import uuid4

from app.services.memory_context_router_service import memory_context_router_service
from app.utils.atomic_json_store import AtomicJsonStore

DATA_DIR = Path("data")
REGISTRY_FILE = DATA_DIR / "project_memory_registry.json"
REGISTRY_STORE = AtomicJsonStore(
    REGISTRY_FILE,
    default_factory=lambda: {
        "version": 1,
        "policy": "canonical_project_memory_registry_no_project_left_behind",
        "projects": [],
        "sync_runs": [],
        "audits": [],
    },
)


class ProjectMemoryRegistryService:
    """Canonical registry for God Mode's real projects.

    This fixes missing project memory coverage and gives the system a stable list
    of priority projects to initialize, audit, sync to AndreOS/Obsidian and keep
    updated over time.
    """

    DEFAULT_PROJECTS = [
        {
            "project_id": "GOD_MODE",
            "display_name": "God Mode",
            "status": "active",
            "priority": 1,
            "category": "core_platform",
            "description": "Cérebro principal PC + APK para executar projetos reais, gerir memória, providers, builds, updates e automação.",
            "expected_memory_path": "memory/vault/AndreOS/02_PROJETOS/GOD_MODE",
            "repo_hints": ["AndreVazao/devops-god-mode"],
            "conversation_hints": ["God Mode", "DevOps God Mode"],
            "next_actions": ["self-update manager", "real install validation", "repo executor real"],
        },
        {
            "project_id": "BOT_FACTORY",
            "display_name": "Bot Factory",
            "status": "active",
            "priority": 2,
            "category": "bot_generation",
            "description": "Framework para criar bots autónomos para jogos/programas, com engenharia reversa assistida, memória e packaging.",
            "expected_memory_path": "memory/vault/AndreOS/02_PROJETOS/BOT_FACTORY",
            "repo_hints": [],
            "conversation_hints": ["Bot Factory", "boot factory", "engenharia reversa"],
            "next_actions": ["mapear conversas antigas", "ligar a providers", "definir executor seguro"],
        },
        {
            "project_id": "PERSONA_FORGE",
            "display_name": "Persona Forge",
            "status": "active",
            "priority": 3,
            "category": "content_ai",
            "description": "Sistema para personagens/personas, vozes, identidades persistentes e conteúdos com continuidade.",
            "expected_memory_path": "memory/vault/AndreOS/02_PROJETOS/PERSONA_FORGE",
            "repo_hints": [],
            "conversation_hints": ["Persona Forge", "personas", "personagens", "identidades"],
            "next_actions": ["criar memória base", "ligar a VerbaForge", "inventariar requisitos"],
        },
        {
            "project_id": "VOX",
            "display_name": "Vox",
            "status": "active",
            "priority": 4,
            "category": "chat_voice_ai",
            "description": "Chat/voz/assistente conversacional para interação natural, potencialmente com TTS/STT e integração com providers.",
            "expected_memory_path": "memory/vault/AndreOS/02_PROJETOS/VOX",
            "repo_hints": [],
            "conversation_hints": ["Vox", "chat de voz", "voice", "TTS", "STT"],
            "next_actions": ["criar memória base", "definir stack voz", "ligar a modo condutor"],
        },
        {
            "project_id": "VERBAFORGE",
            "display_name": "VerbaForge",
            "status": "active",
            "priority": 5,
            "category": "content_publishing",
            "description": "Gerador/publicador autónomo de conteúdos, ebooks, vídeos, redes sociais, anúncios e monetização.",
            "expected_memory_path": "memory/vault/AndreOS/02_PROJETOS/VERBAFORGE",
            "repo_hints": [],
            "conversation_hints": ["VerbaForge", "ViralVazao", "conteúdo", "ebooks", "vídeos"],
            "next_actions": ["organizar módulos", "ligar Persona Forge", "mapear plataformas"],
        },
        {
            "project_id": "BARIBUDOS_STUDIO",
            "display_name": "Baribudos Studio",
            "status": "active",
            "priority": 6,
            "category": "content_studio",
            "description": "Estúdio criativo para família Baribudos, histórias infantis, vídeos, vozes e continuidade narrativa.",
            "expected_memory_path": "memory/vault/AndreOS/02_PROJETOS/BARIBUDOS_STUDIO",
            "repo_hints": [],
            "conversation_hints": ["Baribudos", "Baribudos Studio", "Baribudos conversa"],
            "next_actions": ["extrair conversas antigas", "arquivar contexto concluído", "validar estado do programa"],
        },
        {
            "project_id": "PROVENTIL",
            "display_name": "ProVentil",
            "status": "active",
            "priority": 7,
            "category": "business_ops",
            "description": "Sistema empresarial para ventilação, extração de fumos, videoporteiros, orçamentos, DXF/CAD e operações em Portugal.",
            "expected_memory_path": "memory/vault/AndreOS/02_PROJETOS/PROVENTIL",
            "repo_hints": [],
            "conversation_hints": ["ProVentil", "video porteiro", "extração de fumos", "ClimaStore"],
            "next_actions": ["consolidar regras negócio", "mapear fornecedores", "preparar módulos de orçamento"],
        },
        {
            "project_id": "LORDS_MOBILE_BOT",
            "display_name": "Lords Mobile Bot / Farm",
            "status": "active",
            "priority": 8,
            "category": "game_automation",
            "description": "Bot/farm/headless para Lords Mobile, gestão de castelos, guilda, comandos, eventos, rally/DN e aprendizagem.",
            "expected_memory_path": "memory/vault/AndreOS/02_PROJETOS/LORDS_MOBILE_BOT",
            "repo_hints": [],
            "conversation_hints": ["Lords Mobile", "FugasDark", "FugasLoco", "guild", "DN"],
            "next_actions": ["separar estratégia de implementação", "validar limites seguros", "ligar pesquisa web do jogo"],
        },
        {
            "project_id": "ECU_REPRO",
            "display_name": "ECU Repro / Diagnóstico",
            "status": "active",
            "priority": 9,
            "category": "automotive_tools",
            "description": "Diagnóstico OBD2/ELM327 e conceito de repro ECU com backups, presets, limites seguros e relatórios.",
            "expected_memory_path": "memory/vault/AndreOS/02_PROJETOS/ECU_REPRO",
            "repo_hints": [],
            "conversation_hints": ["ECU", "OBD2", "ELM327", "Konnwei", "reprogramação"],
            "next_actions": ["reforçar segurança", "separar diagnóstico de repro", "mapear hardware"],
        },
        {
            "project_id": "GCODE_CNC",
            "display_name": "GCode / CNC Converter",
            "status": "active",
            "priority": 10,
            "category": "manufacturing_tools",
            "description": "Conversor SVG/DXF/PNG/JPG/BMP/PDF/TXT para GCode CNC/laser/engraver com preview, escala e contornos.",
            "expected_memory_path": "memory/vault/AndreOS/02_PROJETOS/GCODE_CNC",
            "repo_hints": [],
            "conversation_hints": ["GCode", "CNC", "DXF", "SVG", "laser", "OpenCV"],
            "next_actions": ["mapear formatos", "validar pipeline contours", "preparar UI preview"],
        },
        {
            "project_id": "ANDREOS_MEMORY",
            "display_name": "AndreOS / Obsidian Memory",
            "status": "active",
            "priority": 11,
            "category": "memory_system",
            "description": "Memória extensível em Obsidian/AndreOS para projetos, decisões, conversas, contexto compacto e histórico.",
            "expected_memory_path": "memory/vault/AndreOS/00_SISTEMA",
            "repo_hints": ["AndreVazao/devops-god-mode"],
            "conversation_hints": ["AndreOS", "Obsidian", "memória infinita", "vault"],
            "next_actions": ["auditar qualidade", "evitar duplicados", "sincronizar registry"],
        },
    ]

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def seed_defaults(self, overwrite_existing: bool = False) -> Dict[str, Any]:
        state = REGISTRY_STORE.load()
        existing = {p.get("project_id"): p for p in state.get("projects", [])}
        added: List[Dict[str, Any]] = []
        updated: List[Dict[str, Any]] = []
        projects = list(state.get("projects", []))
        for default in self.DEFAULT_PROJECTS:
            item = dict(default)
            item.setdefault("created_at", self._now())
            item["updated_at"] = self._now()
            item["memory_required"] = True
            item["registry_source"] = "phase136_defaults"
            if item["project_id"] in existing:
                if overwrite_existing:
                    for idx, project in enumerate(projects):
                        if project.get("project_id") == item["project_id"]:
                            merged = {**project, **item, "created_at": project.get("created_at", item.get("created_at"))}
                            projects[idx] = merged
                            updated.append(merged)
                continue
            projects.append(item)
            added.append(item)
        projects.sort(key=lambda p: p.get("priority", 9999))
        state["projects"] = projects
        REGISTRY_STORE.save(state)
        run = {
            "sync_run_id": f"project-registry-seed-{uuid4().hex[:12]}",
            "created_at": self._now(),
            "added_count": len(added),
            "updated_count": len(updated),
            "project_count": len(projects),
            "added_project_ids": [p["project_id"] for p in added],
            "updated_project_ids": [p["project_id"] for p in updated],
        }
        self._store("sync_runs", run)
        return {"ok": True, "mode": "project_memory_registry_seed", "run": run, "projects": projects}

    def list_projects(self, status: Optional[str] = None) -> Dict[str, Any]:
        projects = REGISTRY_STORE.load().get("projects", [])
        if not projects:
            projects = self.seed_defaults().get("projects", [])
        if status:
            projects = [p for p in projects if p.get("status") == status]
        return {"ok": True, "mode": "project_memory_registry_list", "project_count": len(projects), "projects": projects}

    def upsert_project(self, project: Dict[str, Any]) -> Dict[str, Any]:
        project_id = self._normalize_project(project.get("project_id") or project.get("display_name") or "PROJECT")
        incoming = dict(project)
        incoming["project_id"] = project_id
        incoming.setdefault("display_name", project_id.replace("_", " ").title())
        incoming.setdefault("status", "active")
        incoming.setdefault("priority", 999)
        incoming.setdefault("category", "custom")
        incoming.setdefault("expected_memory_path", f"memory/vault/AndreOS/02_PROJETOS/{project_id}")
        incoming["updated_at"] = self._now()
        state = REGISTRY_STORE.load()
        projects = state.get("projects", [])
        for idx, existing in enumerate(projects):
            if existing.get("project_id") == project_id:
                merged = {**existing, **incoming, "created_at": existing.get("created_at", self._now())}
                projects[idx] = merged
                state["projects"] = sorted(projects, key=lambda p: p.get("priority", 9999))
                REGISTRY_STORE.save(state)
                return {"ok": True, "mode": "project_memory_registry_upsert", "action": "updated", "project": merged}
        incoming["created_at"] = self._now()
        projects.append(incoming)
        state["projects"] = sorted(projects, key=lambda p: p.get("priority", 9999))
        REGISTRY_STORE.save(state)
        return {"ok": True, "mode": "project_memory_registry_upsert", "action": "created", "project": incoming}

    def sync_memory_contexts(self, limit: int = 50) -> Dict[str, Any]:
        projects = self.list_projects().get("projects", [])[: max(1, min(limit, 200))]
        results = []
        for project in projects:
            idea = self._project_memory_idea(project)
            result = memory_context_router_service.prepare_project_context(
                project_id=project["project_id"],
                source="project_memory_registry_sync",
                idea=idea,
                max_chars=8000,
            )
            results.append({
                "project_id": project["project_id"],
                "ok": bool(result.get("ok", False)),
                "context_pack_id": (result.get("context_pack") or {}).get("context_pack_id"),
                "expected_memory_path": project.get("expected_memory_path"),
            })
        run = {
            "sync_run_id": f"project-memory-sync-{uuid4().hex[:12]}",
            "created_at": self._now(),
            "project_count": len(projects),
            "results": results,
        }
        self._store("sync_runs", run)
        return {"ok": True, "mode": "project_memory_registry_sync", "run": run}

    def audit(self) -> Dict[str, Any]:
        projects = self.list_projects().get("projects", [])
        required_ids = {p["project_id"] for p in self.DEFAULT_PROJECTS}
        present_ids = {p.get("project_id") for p in projects}
        missing = sorted(required_ids - present_ids)
        active = [p for p in projects if p.get("status") == "active"]
        without_memory_path = [p.get("project_id") for p in projects if not p.get("expected_memory_path")]
        without_next_actions = [p.get("project_id") for p in projects if not p.get("next_actions")]
        audit = {
            "audit_id": f"project-registry-audit-{uuid4().hex[:12]}",
            "created_at": self._now(),
            "ok": not missing and not without_memory_path,
            "project_count": len(projects),
            "active_count": len(active),
            "missing_required_project_ids": missing,
            "without_memory_path": without_memory_path,
            "without_next_actions": without_next_actions,
            "required_project_ids": sorted(required_ids),
        }
        self._store("audits", audit)
        return {"ok": audit["ok"], "mode": "project_memory_registry_audit", "audit": audit}

    def _project_memory_idea(self, project: Dict[str, Any]) -> str:
        return "\n".join([
            f"Projeto: {project.get('display_name')} ({project.get('project_id')})",
            f"Estado: {project.get('status')}",
            f"Prioridade: {project.get('priority')}",
            f"Categoria: {project.get('category')}",
            f"Descrição: {project.get('description')}",
            f"Repos: {', '.join(project.get('repo_hints') or [])}",
            f"Conversas/pistas: {', '.join(project.get('conversation_hints') or [])}",
            f"Próximas ações: {', '.join(project.get('next_actions') or [])}",
            "Regra: manter este projeto no registry e atualizar memória conforme novas decisões surgirem.",
        ])

    def _normalize_project(self, value: str) -> str:
        return (value or "PROJECT").strip().upper().replace("-", "_").replace(" ", "_")

    def _store(self, key: str, value: Dict[str, Any]) -> None:
        def mutate(state: Dict[str, Any]) -> Dict[str, Any]:
            state.setdefault(key, [])
            state[key].append(value)
            state[key] = state[key][-100:]
            return state
        REGISTRY_STORE.update(mutate)

    def latest(self) -> Dict[str, Any]:
        state = REGISTRY_STORE.load()
        return {
            "ok": True,
            "mode": "project_memory_registry_latest",
            "project_count": len(state.get("projects") or []),
            "latest_sync_run": (state.get("sync_runs") or [None])[-1],
            "latest_audit": (state.get("audits") or [None])[-1],
        }

    def panel(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "mode": "project_memory_registry_panel",
            "headline": "Registry de projetos principais",
            "latest": self.latest(),
            "audit": self.audit().get("audit"),
            "projects": self.list_projects().get("projects", []),
            "safe_buttons": [
                {"id": "seed", "label": "Garantir projetos base", "endpoint": "/api/project-memory-registry/seed", "priority": "critical"},
                {"id": "audit", "label": "Auditar registry", "endpoint": "/api/project-memory-registry/audit", "priority": "critical"},
                {"id": "sync", "label": "Sincronizar memória", "endpoint": "/api/project-memory-registry/sync-memory", "priority": "critical"},
                {"id": "list", "label": "Ver projetos", "endpoint": "/api/project-memory-registry/projects", "priority": "high"},
            ],
        }

    def get_status(self) -> Dict[str, Any]:
        audit = self.audit().get("audit", {})
        return {
            "ok": audit.get("ok", False),
            "mode": "project_memory_registry_status",
            "project_count": audit.get("project_count", 0),
            "active_count": audit.get("active_count", 0),
            "missing_required_project_ids": audit.get("missing_required_project_ids", []),
            "without_memory_path": audit.get("without_memory_path", []),
        }

    def get_package(self) -> Dict[str, Any]:
        return {"ok": True, "mode": "project_memory_registry_package", "package": {"status": self.get_status(), "panel": self.panel(), "latest": self.latest()}}


project_memory_registry_service = ProjectMemoryRegistryService()
