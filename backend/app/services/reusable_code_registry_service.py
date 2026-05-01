from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from app.utils.atomic_json_store import AtomicJsonStore

STORE_PATH = Path("data/reusable_code_registry.json")


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _default_store() -> dict[str, Any]:
    return {
        "assets": [],
        "aliases": {},
        "last_updated_at": None,
    }


class ReusableCodeRegistryService:
    """Registry for reusable code assets created across projects/repos."""

    def __init__(self) -> None:
        self.store = AtomicJsonStore(STORE_PATH, default_factory=_default_store)

    def _load(self) -> dict[str, Any]:
        payload = self.store.load()
        if not isinstance(payload, dict):
            return _default_store()
        payload.setdefault("assets", [])
        payload.setdefault("aliases", {})
        payload.setdefault("last_updated_at", None)
        return payload

    def _save(self, payload: dict[str, Any]) -> None:
        payload["last_updated_at"] = _utc_now()
        self.store.save(payload)

    def status(self) -> dict[str, Any]:
        payload = self._load()
        return {
            "ok": True,
            "service": "reusable_code_registry",
            "store_path": str(STORE_PATH),
            "asset_count": len(payload.get("assets", [])),
            "alias_count": len(payload.get("aliases", {})),
            "last_updated_at": payload.get("last_updated_at"),
        }

    def panel(self) -> dict[str, Any]:
        return {
            **self.status(),
            "headline": "Reusable Code Registry",
            "description": "Catálogo de código já feito para o God Mode reaproveitar/adaptar em vez de pedir tudo outra vez.",
            "primary_actions": [
                {
                    "label": "Pesquisar componente",
                    "endpoint": "/api/reusable-code-registry/search",
                    "method": "POST",
                    "safe": True,
                },
                {
                    "label": "Registar componente",
                    "endpoint": "/api/reusable-code-registry/register",
                    "method": "POST",
                    "safe": True,
                },
                {
                    "label": "Listar catálogo",
                    "endpoint": "/api/reusable-code-registry/assets",
                    "method": "GET",
                    "safe": True,
                },
            ],
            "examples": [
                "OCR/ACR visual recognition pipeline",
                "ADB Android device bridge automation",
                "GitHub workflow artifact downloader",
                "FastAPI route/service pattern",
                "Obsidian to GitHub memory sync",
            ],
        }

    def register(
        self,
        purpose: str,
        repo: str,
        files: list[str],
        project: str | None = None,
        description: str | None = None,
        tags: list[str] | None = None,
        aliases: list[str] | None = None,
        status: str = "available",
        notes: str | None = None,
    ) -> dict[str, Any]:
        payload = self._load()
        normalized_tags = self._normalize_list(tags)
        normalized_aliases = self._normalize_list(aliases)
        asset_id = f"code-{uuid4().hex[:10]}"
        asset = {
            "id": asset_id,
            "purpose": purpose,
            "project": project,
            "repo": repo,
            "files": files,
            "description": description or purpose,
            "tags": normalized_tags,
            "aliases": normalized_aliases,
            "status": status,
            "notes": notes,
            "created_at": _utc_now(),
            "updated_at": _utc_now(),
            "reuse_count": 0,
        }
        payload["assets"].append(asset)
        for alias in normalized_aliases + normalized_tags + [purpose]:
            key = self._key(alias)
            if key:
                payload["aliases"][key] = asset_id
        self._save(payload)
        return {
            "ok": True,
            "asset": asset,
            "next_action": "use_search_before_generating_new_code",
        }

    def _normalize_list(self, values: list[str] | None) -> list[str]:
        result: list[str] = []
        for value in values or []:
            clean = value.strip()
            if clean and clean not in result:
                result.append(clean)
        return result

    def _key(self, value: str | None) -> str:
        if not value:
            return ""
        return value.strip().lower().replace("_", " ").replace("-", " ")

    def assets(self, limit: int = 100, tag: str | None = None, project: str | None = None) -> dict[str, Any]:
        payload = self._load()
        assets = list(payload.get("assets", []))
        if tag:
            key = self._key(tag)
            assets = [asset for asset in assets if key in [self._key(item) for item in asset.get("tags", [])]]
        if project:
            pkey = self._key(project)
            assets = [asset for asset in assets if self._key(asset.get("project")) == pkey]
        return {
            "ok": True,
            "count": len(assets[:limit]),
            "assets": assets[:limit],
        }

    def search(self, query: str, project: str | None = None, limit: int = 10) -> dict[str, Any]:
        payload = self._load()
        query_key = self._key(query)
        words = [word for word in query_key.split() if len(word) >= 2]
        assets = list(payload.get("assets", []))
        scored: list[dict[str, Any]] = []
        for asset in assets:
            if project and self._key(asset.get("project")) not in {"", self._key(project)}:
                continue
            haystack = " ".join(
                [
                    asset.get("purpose") or "",
                    asset.get("description") or "",
                    asset.get("repo") or "",
                    " ".join(asset.get("files", [])),
                    " ".join(asset.get("tags", [])),
                    " ".join(asset.get("aliases", [])),
                    asset.get("notes") or "",
                ]
            ).lower()
            score = 0
            if query_key and query_key in haystack:
                score += 50
            for word in words:
                if word in haystack:
                    score += 10
            for alias in asset.get("aliases", []):
                if self._key(alias) == query_key:
                    score += 80
            if score > 0:
                scored.append({"score": score, "asset": asset})
        scored.sort(key=lambda item: item["score"], reverse=True)
        return {
            "ok": True,
            "query": query,
            "count": len(scored[:limit]),
            "matches": scored[:limit],
            "recommendation": "reuse_or_adapt_existing_code" if scored else "no_match_register_new_asset_after_build",
        }

    def mark_reused(
        self,
        asset_id: str,
        target_project: str,
        target_repo: str | None = None,
        notes: str | None = None,
    ) -> dict[str, Any]:
        payload = self._load()
        for asset in payload.get("assets", []):
            if asset.get("id") == asset_id:
                asset["reuse_count"] = int(asset.get("reuse_count") or 0) + 1
                asset["updated_at"] = _utc_now()
                history = asset.setdefault("reuse_history", [])
                history.append(
                    {
                        "used_at": _utc_now(),
                        "target_project": target_project,
                        "target_repo": target_repo,
                        "notes": notes,
                    }
                )
                asset["reuse_history"] = history[-50:]
                self._save(payload)
                return {"ok": True, "asset": asset}
        return {"ok": False, "error_type": "asset_not_found", "asset_id": asset_id}

    def import_seed_assets(self) -> dict[str, Any]:
        seeds = [
            {
                "purpose": "OCR/ACR visual recognition pipeline",
                "repo": "AndreVazao/devops-god-mode",
                "files": [],
                "project": "GOD_MODE",
                "description": "Pipeline reutilizável para reconhecimento visual/OCR/ACR quando existir implementação concreta no repo.",
                "tags": ["ocr", "acr", "vision", "recognition", "reusable"],
                "aliases": ["reconhecimento visual", "ocr", "acr", "image recognition"],
                "status": "placeholder_until_real_file_linked",
            },
            {
                "purpose": "FastAPI service plus route pattern",
                "repo": "AndreVazao/devops-god-mode",
                "files": [
                    "backend/app/services/memory_boundary_service.py",
                    "backend/app/routes/memory_boundary.py",
                ],
                "project": "GOD_MODE",
                "description": "Padrão serviço+rota usado para expor módulos internos no backend.",
                "tags": ["fastapi", "service", "route", "backend", "pattern"],
                "aliases": ["fastapi pattern", "backend module pattern"],
                "status": "available",
            },
            {
                "purpose": "Windows EXE boot smoke test",
                "repo": "AndreVazao/devops-god-mode",
                "files": [".github/workflows/windows-exe-real-build.yml"],
                "project": "GOD_MODE",
                "description": "Workflow pattern que compila EXE, arranca no runner e valida /health antes de publicar artifact.",
                "tags": ["github actions", "windows", "pyinstaller", "smoke test", "artifact"],
                "aliases": ["exe smoke test", "windows build validation"],
                "status": "available",
            },
        ]
        created = []
        for seed in seeds:
            existing = self.search(seed["purpose"], limit=1)
            if existing.get("matches"):
                continue
            created.append(self.register(**seed)["asset"])
        return {"ok": True, "created_count": len(created), "created": created}

    def export_markdown(self) -> dict[str, Any]:
        payload = self._load()
        lines = ["# Reusable Code Registry", "", f"Updated: {_utc_now()}", ""]
        for asset in payload.get("assets", []):
            lines.extend(
                [
                    f"## {asset.get('purpose')}",
                    "",
                    f"- ID: `{asset.get('id')}`",
                    f"- Projeto: {asset.get('project') or 'n/a'}",
                    f"- Repo: `{asset.get('repo')}`",
                    f"- Estado: {asset.get('status')}",
                    f"- Reutilizações: {asset.get('reuse_count', 0)}",
                    f"- Tags: {', '.join(asset.get('tags', []))}",
                    "- Ficheiros:",
                    *[f"  - `{path}`" for path in asset.get("files", [])],
                    "",
                    asset.get("description") or "",
                    "",
                ]
            )
        return {"ok": True, "markdown": "\n".join(lines).strip()}

    def package(self) -> dict[str, Any]:
        return {
            "status": self.status(),
            "panel": self.panel(),
            "assets": self.assets(limit=50),
            "markdown": self.export_markdown(),
        }


reusable_code_registry_service = ReusableCodeRegistryService()
