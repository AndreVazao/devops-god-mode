from __future__ import annotations

import base64
import json
from typing import Any

import httpx

from app.config import settings

GITHUB_API_BASE = "https://api.github.com"
COMMON_PATHS = [
    "package.json",
    "requirements.txt",
    "pyproject.toml",
    "prisma/schema.prisma",
    "next.config.mjs",
    "next.config.js",
    "render.yaml",
]


class GitHubService:
    def __init__(self) -> None:
        self.token = settings.GITHUB_TOKEN

    def is_configured(self) -> bool:
        return bool(self.token)

    def _headers(self) -> dict[str, str]:
        if not self.token:
            raise RuntimeError("github_not_configured")
        return {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }

    async def _get_json(
        self,
        client: httpx.AsyncClient,
        url: str,
        params: dict[str, Any] | None = None,
    ) -> Any:
        response = await client.get(
            url,
            headers=self._headers(),
            params=params,
            timeout=30.0,
        )
        response.raise_for_status()
        return response.json()

    async def _get_json_safe(
        self,
        client: httpx.AsyncClient,
        url: str,
        params: dict[str, Any] | None = None,
        default: Any = None,
    ) -> Any:
        try:
            return await self._get_json(client, url, params=params)
        except Exception:
            return default

    async def list_repositories(self, per_page: int = 100) -> list[dict[str, Any]]:
        async with httpx.AsyncClient() as client:
            repos = await self._get_json(
                client,
                f"{GITHUB_API_BASE}/user/repos",
                params={
                    "per_page": per_page,
                    "sort": "updated",
                    "affiliation": "owner,collaborator,organization_member",
                },
            )

        return [
            {
                "id": repo.get("id"),
                "name": repo.get("name"),
                "full_name": repo.get("full_name"),
                "private": repo.get("private"),
                "default_branch": repo.get("default_branch"),
                "updated_at": repo.get("updated_at"),
                "html_url": repo.get("html_url"),
                "language": repo.get("language"),
                "size": repo.get("size"),
                "visibility": repo.get("visibility"),
            }
            for repo in repos
        ]

    async def _fetch_content(
        self,
        client: httpx.AsyncClient,
        full_name: str,
        path: str,
        ref: str | None = None,
    ) -> dict[str, Any] | None:
        try:
            response = await client.get(
                f"{GITHUB_API_BASE}/repos/{full_name}/contents/{path}",
                headers=self._headers(),
                params={"ref": ref} if ref else None,
                timeout=20.0,
            )
            if response.status_code == 404:
                return None
            response.raise_for_status()
            return response.json()
        except Exception:
            return None

    def _decode_content(self, payload: dict[str, Any] | None) -> str | None:
        if not payload or payload.get("encoding") != "base64":
            return None
        try:
            return base64.b64decode(payload.get("content", "")).decode(
                "utf-8",
                errors="ignore",
            )
        except Exception:
            return None

    async def get_repository_file(
        self,
        repository_full_name: str,
        path: str,
        ref: str | None = None,
    ) -> dict[str, Any]:
        if not self.is_configured():
            raise RuntimeError("github_not_configured")

        async with httpx.AsyncClient() as client:
            payload = await self._fetch_content(client, repository_full_name, path, ref=ref)

        if not payload:
            return {
                "ok": False,
                "mode": "github_repository_file",
                "repository_full_name": repository_full_name,
                "path": path,
                "ref": ref,
                "file_status": "not_found",
            }

        decoded_text = self._decode_content(payload)
        return {
            "ok": True,
            "mode": "github_repository_file",
            "repository_full_name": repository_full_name,
            "path": path,
            "ref": ref,
            "sha": payload.get("sha"),
            "size": payload.get("size"),
            "download_url": payload.get("download_url"),
            "encoding": payload.get("encoding"),
            "content_text": decoded_text,
            "file_status": "found",
        }

    async def create_or_update_repository_file(
        self,
        repository_full_name: str,
        path: str,
        content_text: str,
        commit_message: str,
        branch: str | None = None,
        sha: str | None = None,
    ) -> dict[str, Any]:
        if not self.is_configured():
            raise RuntimeError("github_not_configured")

        encoded = base64.b64encode(content_text.encode("utf-8")).decode("utf-8")
        payload: dict[str, Any] = {
            "message": commit_message,
            "content": encoded,
        }
        if branch:
            payload["branch"] = branch
        if sha:
            payload["sha"] = sha

        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"{GITHUB_API_BASE}/repos/{repository_full_name}/contents/{path}",
                headers=self._headers(),
                json=payload,
                timeout=30.0,
            )
            response.raise_for_status()
            result = response.json()

        return {
            "ok": True,
            "mode": "github_repository_file_written",
            "repository_full_name": repository_full_name,
            "path": path,
            "branch": branch,
            "commit_sha": ((result.get("commit") or {}).get("sha")),
            "content_sha": ((result.get("content") or {}).get("sha")),
            "write_status": "written",
        }

    async def create_or_update_repository_asset(
        self,
        repository_full_name: str,
        path: str,
        raw_bytes: bytes,
        commit_message: str,
        branch: str | None = None,
        sha: str | None = None,
    ) -> dict[str, Any]:
        if not self.is_configured():
            raise RuntimeError("github_not_configured")

        payload: dict[str, Any] = {
            "message": commit_message,
            "content": base64.b64encode(raw_bytes).decode("utf-8"),
        }
        if branch:
            payload["branch"] = branch
        if sha:
            payload["sha"] = sha

        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"{GITHUB_API_BASE}/repos/{repository_full_name}/contents/{path}",
                headers=self._headers(),
                json=payload,
                timeout=30.0,
            )
            response.raise_for_status()
            result = response.json()

        return {
            "ok": True,
            "mode": "github_repository_asset_written",
            "repository_full_name": repository_full_name,
            "path": path,
            "branch": branch,
            "commit_sha": ((result.get("commit") or {}).get("sha")),
            "content_sha": ((result.get("content") or {}).get("sha")),
            "write_status": "written",
        }

    async def _detect_common_files(
        self,
        client: httpx.AsyncClient,
        full_name: str,
    ) -> dict[str, bool]:
        found: dict[str, bool] = {}
        for path in COMMON_PATHS:
            found[path] = await self._fetch_content(client, full_name, path) is not None
        return found

    async def _fetch_languages(
        self,
        client: httpx.AsyncClient,
        full_name: str,
    ) -> dict[str, int]:
        result = await self._get_json_safe(
            client,
            f"{GITHUB_API_BASE}/repos/{full_name}/languages",
            default={},
        )
        return result or {}

    async def _fetch_recent_commits(
        self,
        client: httpx.AsyncClient,
        full_name: str,
        per_page: int = 5,
    ) -> list[dict[str, Any]]:
        commits = await self._get_json_safe(
            client,
            f"{GITHUB_API_BASE}/repos/{full_name}/commits",
            params={"per_page": per_page},
            default=[],
        )
        if not isinstance(commits, list):
            return []

        return [
            {
                "sha": item.get("sha"),
                "message": ((item.get("commit") or {}).get("message") or "").split("\n")[0],
                "date": (((item.get("commit") or {}).get("committer") or {}).get("date")),
            }
            for item in commits
        ]

    def _classify_stack(
        self,
        package_json_text: str | None,
        common_files: dict[str, bool],
        languages: dict[str, int],
    ) -> dict[str, Any]:
        dependencies: dict[str, Any] = {}
        scripts: dict[str, Any] = {}
        frameworks: list[str] = []
        runtimes: list[str] = []

        if package_json_text:
            try:
                parsed = json.loads(package_json_text)
                dependencies = {
                    **(parsed.get("dependencies") or {}),
                    **(parsed.get("devDependencies") or {}),
                }
                scripts = parsed.get("scripts") or {}
            except json.JSONDecodeError:
                pass

        if (
            common_files.get("requirements.txt")
            or common_files.get("pyproject.toml")
            or "Python" in languages
        ):
            runtimes.append("python")

        if (
            package_json_text
            or common_files.get("next.config.mjs")
            or common_files.get("next.config.js")
            or "TypeScript" in languages
            or "JavaScript" in languages
        ):
            runtimes.append("node")

        if common_files.get("prisma/schema.prisma") or "prisma" in dependencies:
            frameworks.append("prisma")
        if common_files.get("render.yaml"):
            frameworks.append("render")
        if "next" in dependencies:
            frameworks.append("nextjs")
        if "react" in dependencies:
            frameworks.append("react")
        if "vite" in dependencies:
            frameworks.append("vite")
        if "@capacitor/core" in dependencies:
            frameworks.append("capacitor")
        if "@tauri-apps/cli" in dependencies:
            frameworks.append("tauri")
        if "stripe" in dependencies:
            frameworks.append("stripe")
        if "fastapi" in dependencies or common_files.get("requirements.txt"):
            frameworks.append("fastapi")

        return {
            "runtimes": sorted(set(runtimes)),
            "frameworks": sorted(set(frameworks)),
            "scripts": scripts,
        }

    def _to_hybrid_summary(
        self,
        repo: dict[str, Any],
        stack: dict[str, Any],
        common_files: dict[str, bool],
    ) -> dict[str, Any]:
        name = repo.get("name") or "repo"
        frameworks = stack.get("frameworks") or []

        if "nextjs" in frameworks:
            plain = f"{name} parece uma app web pública baseada em Next.js."
        elif "fastapi" in frameworks:
            plain = f"{name} parece um backend Python/FastAPI."
        elif "capacitor" in frameworks or "tauri" in frameworks:
            plain = f"{name} mistura app mobile/desktop com frontend web."
        else:
            plain = f"{name} já foi lido, mas ainda precisa de classificação mais profunda."

        if common_files.get("prisma/schema.prisma"):
            plain += " Usa Prisma, por isso há schema de base de dados a vigiar."

        return {
            "plain": plain,
            "technical": stack,
        }

    async def scan_repositories(self, limit: int = 20) -> dict[str, Any]:
        repositories = await self.list_repositories(per_page=min(max(limit, 1), 100))

        async with httpx.AsyncClient() as client:
            scanned: list[dict[str, Any]] = []
            errors: list[dict[str, Any]] = []

            for repo in repositories[:limit]:
                full_name = repo["full_name"]

                try:
                    common_files = await self._detect_common_files(client, full_name)
                    languages = await self._fetch_languages(client, full_name)
                    package_payload = await self._fetch_content(client, full_name, "package.json")
                    package_json_text = self._decode_content(package_payload)
                    recent_commits = await self._fetch_recent_commits(client, full_name)
                    stack = self._classify_stack(package_json_text, common_files, languages)

                    scanned.append(
                        {
                            **repo,
                            "languages": languages,
                            "common_files": common_files,
                            "stack": stack,
                            "recent_commits": recent_commits,
                            "summary": self._to_hybrid_summary(repo, stack, common_files),
                            "scan_status": "ok",
                        }
                    )
                except Exception as exc:
                    errors.append(
                        {
                            "repo": full_name,
                            "error": str(exc),
                        }
                    )
                    scanned.append(
                        {
                            **repo,
                            "languages": {},
                            "common_files": {},
                            "stack": {"runtimes": [], "frameworks": [], "scripts": {}},
                            "recent_commits": [],
                            "summary": {
                                "plain": f"{full_name} falhou durante a leitura técnica.",
                                "technical": {"error": str(exc)},
                            },
                            "scan_status": "error",
                        }
                    )

        return {
            "ok": True,
            "partial": len(errors) > 0,
            "count": len(scanned),
            "success_count": len([item for item in scanned if item.get("scan_status") == "ok"]),
            "error_count": len(errors),
            "errors": errors,
            "repositories": scanned,
        }


github_service = GitHubService()
