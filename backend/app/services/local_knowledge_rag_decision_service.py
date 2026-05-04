from __future__ import annotations

import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional
from uuid import uuid4

from app.services.capability_reuse_service import capability_reuse_service
from app.services.memory_context_router_service import memory_context_router_service
from app.services.memory_core_service import memory_core_service
from app.utils.atomic_json_store import AtomicJsonStore

DATA_DIR = Path("data")
RAG_FILE = DATA_DIR / "local_knowledge_rag_decision.json"
RAG_STORE = AtomicJsonStore(
    RAG_FILE,
    default_factory=lambda: {
        "version": 1,
        "policy": "local_first_rag_reuse_before_create_no_secret_handoff",
        "indexes": [],
        "searches": [],
        "decisions": [],
    },
)


class LocalKnowledgeRagDecisionService:
    """Local knowledge/RAG decision layer for God Mode.

    Phase 170 gives the orchestrator a native local-first retrieval layer so it
    checks AndreOS memory, Obsidian/local notes, docs and existing code before
    creating new code. V1 is intentionally dependency-light: lexical index,
    source classification and safety-aware snippets. A later phase can add
    embeddings or a vector DB without changing the decision contract.
    """

    SERVICE_ID = "local_knowledge_rag_decision"
    DEFAULT_PROJECT = "GOD_MODE"
    MAX_FILE_BYTES = 300_000
    MAX_SNIPPET_CHARS = 900
    MAX_INDEX_ITEMS = 1500
    INDEXABLE_SUFFIXES = {".py", ".md", ".txt", ".json", ".yml", ".yaml", ".js", ".ts", ".tsx", ".html", ".css", ".ps1", ".bat"}
    DEFAULT_ROOTS = [
        {"root": "memory/vault/AndreOS", "source_type": "andreos_obsidian_local", "priority": 5},
        {"root": "docs", "source_type": "repo_docs", "priority": 4},
        {"root": "backend", "source_type": "repo_backend_code", "priority": 4},
        {"root": "desktop", "source_type": "repo_desktop_code", "priority": 3},
        {"root": "android", "source_type": "repo_android_code", "priority": 3},
        {"root": "data/conversation_repo_materializations", "source_type": "reusable_generated_code", "priority": 2},
    ]
    BLOCKED_PATH_PARTS = [
        ".env",
        "secret",
        "credential",
        "password",
        "cookie",
        "private_key",
        "authorization",
        "bearer",
        ".git/",
        "node_modules/",
        "__pycache__/",
        ".venv/",
        "dist/",
        "build/",
    ]
    SECRET_PATTERNS = [
        re.compile(r"(?i)(api[_-]?key|secret|password|senha|token|authorization|bearer|cookie)\s*[:=]\s*[^\s\n]+"),
        re.compile(r"(?i)(sk_live_|sk_test_|ghp_|github_pat_|xoxb-|ya29\.)[^\s\n]+"),
        re.compile(r"(?i)(access_token|refresh_token)\s*[:=]\s*[^\s\n]+"),
    ]

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def status(self) -> Dict[str, Any]:
        state = RAG_STORE.load()
        return {
            "ok": True,
            "service": self.SERVICE_ID,
            "created_at": self._now(),
            "index_count": len(state.get("indexes") or []),
            "search_count": len(state.get("searches") or []),
            "decision_count": len(state.get("decisions") or []),
            "default_roots": self.DEFAULT_ROOTS,
            "max_index_items": self.MAX_INDEX_ITEMS,
            "index_mode": "lexical_local_first_v1",
            "embedding_required": False,
        }

    def rules(self) -> List[str]:
        return [
            "Pesquisar memória AndreOS, Obsidian/local, docs e código existente antes de criar código novo.",
            "V1 usa índice lexical local sem enviar contexto para providers externos.",
            "Snippets são sanitizados e caminhos sensíveis são ignorados.",
            "Resultados com conteúdo potencialmente sensível são marcados e ficam com snippet limitado/redigido.",
            "Decisões devem preferir reutilizar/adaptar módulos existentes quando houver evidência suficiente.",
            "AndreOS GitHub memory continua para decisões técnicas estáveis; Obsidian/local continua oficina.",
            "Nunca indexar `.env`, credenciais, cookies, secrets, node_modules, builds ou caches.",
        ]

    def policy(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "service": self.SERVICE_ID,
            "purpose": "local_knowledge_search_and_reuse_decision_before_new_code",
            "sources": self.DEFAULT_ROOTS,
            "safe_handoff": {
                "external_ai_context": "only_sanitized_snippets_after_security_review",
                "local_private_context": "kept_local_by_default",
                "secrets_policy": "do_not_index_or_forward_secrets",
            },
            "blocked_path_parts": self.BLOCKED_PATH_PARTS,
            "indexable_suffixes": sorted(self.INDEXABLE_SUFFIXES),
            "rules": self.rules(),
            "future_upgrade_path": ["optional_embeddings", "vector_store", "repo_symbol_index", "obsidian_frontmatter_index"],
        }

    def panel(self) -> Dict[str, Any]:
        return {
            **self.status(),
            "headline": "Local Knowledge/RAG Decision v1",
            "description": "Índice local seguro para pesquisar memória, docs e código existente antes de gerar código novo.",
            "primary_actions": [
                {"label": "Construir índice", "endpoint": "/api/local-knowledge-rag/build-index", "method": "POST", "safe": True},
                {"label": "Pesquisar", "endpoint": "/api/local-knowledge-rag/search", "method": "POST", "safe": True},
                {"label": "Decisão reuse-first", "endpoint": "/api/local-knowledge-rag/decision", "method": "POST", "safe": True},
                {"label": "Reuse check", "endpoint": "/api/local-knowledge-rag/reuse-check", "method": "POST", "safe": True},
            ],
            "policy": self.policy(),
            "latest": self.latest(),
        }

    def build_index(
        self,
        project_name: str = DEFAULT_PROJECT,
        roots: Optional[List[Dict[str, Any]]] = None,
        max_items: int = MAX_INDEX_ITEMS,
    ) -> Dict[str, Any]:
        project = self._normalize_project(project_name)
        selected_roots = roots or self.DEFAULT_ROOTS
        items: List[Dict[str, Any]] = []
        skipped: List[Dict[str, Any]] = []

        for root_spec in selected_roots:
            root = Path(str(root_spec.get("root") or "")).resolve()
            source_type = str(root_spec.get("source_type") or "local_file")
            priority = int(root_spec.get("priority") or 1)
            if not root.exists():
                skipped.append({"root": str(root_spec.get("root")), "reason": "root_not_found"})
                continue
            for path in self._iter_files(root):
                if len(items) >= max(1, min(max_items, self.MAX_INDEX_ITEMS)):
                    break
                if not self._safe_path(path):
                    skipped.append({"path": str(path), "reason": "blocked_path"})
                    continue
                try:
                    if path.stat().st_size > self.MAX_FILE_BYTES:
                        skipped.append({"path": str(path), "reason": "file_too_large"})
                        continue
                    raw = path.read_text(encoding="utf-8", errors="ignore")
                except Exception as exc:
                    skipped.append({"path": str(path), "reason": f"read_error:{exc.__class__.__name__}"})
                    continue
                sanitized = self._sanitize(raw)
                terms = self._terms(f"{path.name} {sanitized}")
                if not terms:
                    continue
                items.append(
                    {
                        "item_id": f"knowledge-item-{uuid4().hex[:10]}",
                        "path": self._display_path(path),
                        "source_type": source_type,
                        "priority": priority,
                        "suffix": path.suffix.lower(),
                        "title": self._title_for(path, sanitized),
                        "snippet": self._snippet(sanitized),
                        "term_counts": dict(Counter(terms).most_common(80)),
                        "contains_sensitive_terms": raw != sanitized,
                        "size": len(raw.encode("utf-8")),
                    }
                )
            if len(items) >= max(1, min(max_items, self.MAX_INDEX_ITEMS)):
                break

        index = {
            "index_id": f"local-knowledge-index-{uuid4().hex[:12]}",
            "created_at": self._now(),
            "project": project,
            "index_mode": "lexical_local_first_v1",
            "roots": selected_roots,
            "item_count": len(items),
            "skipped_count": len(skipped),
            "items": items,
            "skipped_preview": skipped[:50],
            "status": "ready" if items else "empty",
        }
        self._store("indexes", index)
        return {"ok": True, "service": self.SERVICE_ID, "index": index}

    def search(
        self,
        query: str,
        project_name: str = DEFAULT_PROJECT,
        source_types: Optional[List[str]] = None,
        limit: int = 12,
        index_id: Optional[str] = None,
        build_if_missing: bool = True,
    ) -> Dict[str, Any]:
        safe_query = self._sanitize(query).strip()
        if not safe_query:
            return {"ok": False, "service": self.SERVICE_ID, "error": "empty_or_unsafe_query"}
        index = self._get_index(index_id=index_id, project_name=project_name, build_if_missing=build_if_missing)
        if not index:
            return {"ok": False, "service": self.SERVICE_ID, "error": "index_not_found"}

        query_terms = self._terms(safe_query)
        filters = set(source_types or [])
        scored: List[Dict[str, Any]] = []
        for item in index.get("items") or []:
            if filters and item.get("source_type") not in filters:
                continue
            score = self._score(query_terms, item)
            if score <= 0:
                continue
            scored.append(
                {
                    "path": item.get("path"),
                    "source_type": item.get("source_type"),
                    "title": item.get("title"),
                    "score": score,
                    "snippet": item.get("snippet"),
                    "contains_sensitive_terms": item.get("contains_sensitive_terms", False),
                    "reuse_hint": self._reuse_hint(item),
                }
            )
        scored.sort(key=lambda item: (item["score"], item["source_type"], item["path"]), reverse=True)
        search_record = {
            "search_id": f"local-knowledge-search-{uuid4().hex[:12]}",
            "created_at": self._now(),
            "project": self._normalize_project(project_name),
            "query": safe_query,
            "index_id": index.get("index_id"),
            "source_types": source_types or [],
            "result_count": len(scored),
            "results": scored[: max(1, min(limit, 50))],
        }
        self._store("searches", search_record)
        return {"ok": True, "service": self.SERVICE_ID, "search": search_record}

    def reuse_check(
        self,
        capability_name: str,
        target_project: str = DEFAULT_PROJECT,
        limit: int = 10,
    ) -> Dict[str, Any]:
        capability = capability_reuse_service.lookup_capability(capability_name)
        local = self.search(
            query=capability_name,
            project_name=target_project,
            limit=limit,
            build_if_missing=True,
        )
        candidates = []
        for item in (capability.get("matches") or [])[:limit]:
            candidates.append(
                {
                    "source": "capability_reuse_service",
                    "path": item.get("file_path"),
                    "score": item.get("score"),
                    "preview": self._sanitize(str(item.get("preview") or ""))[: self.MAX_SNIPPET_CHARS],
                    "action": "review_and_adapt_existing_capability",
                }
            )
        for item in ((local.get("search") or {}).get("results") or [])[:limit]:
            candidates.append(
                {
                    "source": "local_knowledge_index",
                    "path": item.get("path"),
                    "score": item.get("score"),
                    "preview": item.get("snippet"),
                    "action": "inspect_before_new_code",
                }
            )
        recommendation = "reuse_or_adapt_existing" if candidates else "no_existing_candidate_found_prepare_new_module"
        return {
            "ok": True,
            "service": self.SERVICE_ID,
            "capability_name": capability_name,
            "target_project": target_project,
            "candidate_count": len(candidates),
            "recommendation": recommendation,
            "candidates": candidates[:limit],
        }

    def decision(
        self,
        goal: str,
        project_name: str = DEFAULT_PROJECT,
        capability_name: Optional[str] = None,
        limit: int = 10,
    ) -> Dict[str, Any]:
        project = self._normalize_project(project_name)
        query = capability_name or goal
        search = self.search(query=query, project_name=project, limit=limit, build_if_missing=True)
        reuse = self.reuse_check(capability_name=query, target_project=project, limit=limit)
        memory_context = memory_context_router_service.prepare_project_context(
            project_id=project,
            source="local_knowledge_rag_decision",
            idea=None,
            max_chars=3000,
        )
        results = (search.get("search") or {}).get("results") or []
        candidate_count = reuse.get("candidate_count", 0)
        decision_status = "reuse_first" if candidate_count > 0 or results else "new_code_allowed_after_no_reuse_found"
        next_actions = [
            "Abrir/rever os candidatos encontrados antes de criar ficheiro novo.",
            "Preferir adaptar serviço/rota existente se o score for suficiente.",
            "Se for necessário criar módulo novo, documentar motivo no HISTORICO/DECISOES.",
            "Nunca enviar snippets sensíveis para provider externo sem Security Guard.",
        ]
        decision = {
            "decision_id": f"local-rag-decision-{uuid4().hex[:12]}",
            "created_at": self._now(),
            "project": project,
            "goal": self._sanitize(goal),
            "capability_name": capability_name,
            "decision_status": decision_status,
            "recommendation": reuse.get("recommendation"),
            "search_id": (search.get("search") or {}).get("search_id"),
            "top_results": results[:limit],
            "reuse_candidates": reuse.get("candidates", [])[:limit],
            "context_pack_id": ((memory_context.get("context_pack") or {}).get("context_pack_id")),
            "safe_for_external_ai": False,
            "next_actions": next_actions,
        }
        self._store("decisions", decision)
        return {"ok": True, "service": self.SERVICE_ID, "decision": decision}

    def latest(self) -> Dict[str, Any]:
        state = RAG_STORE.load()
        indexes = state.get("indexes") or []
        searches = state.get("searches") or []
        decisions = state.get("decisions") or []
        return {
            "ok": True,
            "service": self.SERVICE_ID,
            "latest_index": indexes[-1] if indexes else None,
            "latest_search": searches[-1] if searches else None,
            "latest_decision": decisions[-1] if decisions else None,
            "index_count": len(indexes),
            "search_count": len(searches),
            "decision_count": len(decisions),
        }

    def package(self) -> Dict[str, Any]:
        return {"status": self.status(), "panel": self.panel(), "policy": self.policy(), "latest": self.latest()}

    def _iter_files(self, root: Path) -> Iterable[Path]:
        for path in root.rglob("*"):
            if path.is_file() and path.suffix.lower() in self.INDEXABLE_SUFFIXES:
                yield path

    def _safe_path(self, path: Path) -> bool:
        normalized = self._display_path(path).lower().replace("\\", "/")
        return not any(part in normalized for part in self.BLOCKED_PATH_PARTS)

    def _display_path(self, path: Path) -> str:
        try:
            return str(path.relative_to(Path.cwd()))
        except ValueError:
            return str(path)

    def _sanitize(self, text: str) -> str:
        sanitized = text
        for pattern in self.SECRET_PATTERNS:
            sanitized = pattern.sub("[REDACTED_SECRET]", sanitized)
        return sanitized

    def _snippet(self, text: str) -> str:
        compact = re.sub(r"\s+", " ", text).strip()
        return compact[: self.MAX_SNIPPET_CHARS]

    def _title_for(self, path: Path, text: str) -> str:
        for line in text.splitlines():
            clean = line.strip("# \t")
            if clean:
                return clean[:120]
        return path.name

    def _terms(self, text: str) -> List[str]:
        return [term for term in re.findall(r"[a-zA-ZÀ-ÿ0-9_]{3,}", text.lower()) if term not in {"the", "and", "for", "com", "para", "uma", "que", "não", "from", "import"}]

    def _score(self, query_terms: List[str], item: Dict[str, Any]) -> int:
        counts = item.get("term_counts") or {}
        score = 0
        for term in query_terms:
            score += int(counts.get(term, 0)) * 3
            if term in str(item.get("path", "")).lower():
                score += 8
            if term in str(item.get("title", "")).lower():
                score += 5
            if term in str(item.get("snippet", "")).lower():
                score += 2
        score += int(item.get("priority") or 1)
        return score

    def _reuse_hint(self, item: Dict[str, Any]) -> str:
        source_type = item.get("source_type")
        if source_type in {"repo_backend_code", "repo_desktop_code", "repo_android_code", "reusable_generated_code"}:
            return "possible_existing_code_to_reuse"
        if source_type in {"andreos_obsidian_local", "repo_docs"}:
            return "possible_existing_decision_or_documentation"
        return "inspect_before_creation"

    def _get_index(self, index_id: Optional[str], project_name: str, build_if_missing: bool) -> Optional[Dict[str, Any]]:
        state = RAG_STORE.load()
        indexes = state.get("indexes") or []
        if index_id:
            found = next((item for item in indexes if item.get("index_id") == index_id), None)
            if found:
                return found
        if indexes:
            return indexes[-1]
        if build_if_missing:
            return self.build_index(project_name=project_name).get("index")
        return None

    def _normalize_project(self, project_name: str) -> str:
        return re.sub(r"[^A-Z0-9_]+", "_", (project_name or self.DEFAULT_PROJECT).upper()).strip("_") or self.DEFAULT_PROJECT

    def _store(self, key: str, item: Dict[str, Any]) -> None:
        def mutate(state: Dict[str, Any]) -> Dict[str, Any]:
            state.setdefault("version", 1)
            state.setdefault("policy", "local_first_rag_reuse_before_create_no_secret_handoff")
            state.setdefault(key, [])
            state[key].append(item)
            state[key] = state[key][-80:]
            return state

        RAG_STORE.update(mutate)


local_knowledge_rag_decision_service = LocalKnowledgeRagDecisionService()
