import hashlib
import json
from typing import Any

import httpx

from app.config import settings


class RepoTreeCacheV3:
    def __init__(self) -> None:
        self.supabase_url = settings.SUPABASE_URL
        self.supabase_key = settings.SUPABASE_KEY

    def is_configured(self) -> bool:
        return bool(self.supabase_url and self.supabase_key)

    def _headers(self) -> dict[str, str]:
        return {
            "apikey": str(self.supabase_key),
            "Authorization": f"Bearer {self.supabase_key}",
            "Content-Type": "application/json",
            "Prefer": "return=representation",
        }

    def structural_hash(self, tree_json: dict[str, Any]) -> str:
        encoded = json.dumps(tree_json, sort_keys=True, ensure_ascii=False).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()

    async def _get_repo_id(self, repo_full_name: str) -> str | None:
        if not self.is_configured():
            return None
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{self.supabase_url}/rest/v1/repos?select=id,full_name&full_name=eq.{repo_full_name}",
                headers={
                    "apikey": str(self.supabase_key),
                    "Authorization": f"Bearer {self.supabase_key}",
                },
            )
            response.raise_for_status()
            data = response.json()
            return data[0]["id"] if data else None

    async def ensure_repo_exists(self, repo_full_name: str) -> str | None:
        repo_id = await self._get_repo_id(repo_full_name)
        if repo_id:
            return repo_id
        if not self.is_configured():
            return None
        repo_name = repo_full_name.split("/")[-1]
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{self.supabase_url}/rest/v1/repos",
                headers=self._headers(),
                json=[{
                    "full_name": repo_full_name,
                    "repo_name": repo_name,
                    "status": "tree-scanned",
                }],
            )
            response.raise_for_status()
        return await self._get_repo_id(repo_full_name)

    async def save_snapshot(
        self,
        repo_full_name: str,
        tree_json: dict[str, Any],
        tree_text: str,
        depth: int,
        analysis: dict[str, Any],
        analysis_status: str = "partial",
    ) -> dict[str, Any]:
        if not self.is_configured():
            return {"cached": False, "reason": "supabase_not_configured"}

        repo_id = await self.ensure_repo_exists(repo_full_name)
        if not repo_id:
            return {"cached": False, "reason": "repo_id_not_available"}

        structural_hash = self.structural_hash(tree_json)
        payload = [{
            "repo_id": repo_id,
            "source": "github",
            "depth": depth,
            "root_path": repo_full_name,
            "tree_json": tree_json,
            "tree_text": tree_text,
            "structural_hash": structural_hash,
            "analysis_status": analysis_status,
            "detected_frameworks_json": analysis.get("frameworks", []),
            "detected_repo_types_json": analysis.get("repo_types", []),
            "risk_flags_json": analysis.get("risks", []),
            "recommendations_json": analysis.get("recommendations", []),
        }]

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{self.supabase_url}/rest/v1/repo_tree_snapshots",
                headers=self._headers(),
                json=payload,
            )
            response.raise_for_status()
            rows = response.json() if response.text else []

        return {
            "cached": True,
            "repo_id": repo_id,
            "structural_hash": structural_hash,
            "snapshot_id": rows[0].get("id") if rows else None,
            "analysis_persisted": True,
        }


repo_tree_cache_v3 = RepoTreeCacheV3()
