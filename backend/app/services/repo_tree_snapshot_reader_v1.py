import httpx

from app.config import settings


class RepoTreeSnapshotReaderV1:
    def __init__(self) -> None:
        self.supabase_url = settings.SUPABASE_URL
        self.supabase_key = settings.SUPABASE_KEY

    def is_configured(self) -> bool:
        return bool(self.supabase_url and self.supabase_key)

    def _headers(self) -> dict[str, str]:
        return {
            "apikey": str(self.supabase_key),
            "Authorization": f"Bearer {self.supabase_key}",
        }

    async def latest_snapshot(self, repo_full_name: str):
        if not self.is_configured():
            return {"ok": False, "reason": "supabase_not_configured"}

        async with httpx.AsyncClient(timeout=30.0) as client:
            repo_resp = await client.get(
                f"{self.supabase_url}/rest/v1/repos?select=id,full_name&full_name=eq.{repo_full_name}",
                headers=self._headers(),
            )
            repo_resp.raise_for_status()
            repo_rows = repo_resp.json()
            if not repo_rows:
                return {"ok": False, "reason": "repo_not_found", "repo_full_name": repo_full_name}

            repo_id = repo_rows[0]["id"]
            snap_resp = await client.get(
                f"{self.supabase_url}/rest/v1/repo_tree_snapshots?select=*&repo_id=eq.{repo_id}&order=created_at.desc&limit=1",
                headers=self._headers(),
            )
            snap_resp.raise_for_status()
            snap_rows = snap_resp.json()
            if not snap_rows:
                return {"ok": False, "reason": "snapshot_not_found", "repo_full_name": repo_full_name, "repo_id": repo_id}

            row = snap_rows[0]
            return {
                "ok": True,
                "repo_full_name": repo_full_name,
                "repo_id": repo_id,
                "snapshot": {
                    "id": row.get("id"),
                    "depth": row.get("depth"),
                    "analysis_status": row.get("analysis_status"),
                    "structural_hash": row.get("structural_hash"),
                    "frameworks": row.get("detected_frameworks_json") or [],
                    "repo_types": row.get("detected_repo_types_json") or [],
                    "risks": row.get("risk_flags_json") or [],
                    "recommendations": row.get("recommendations_json") or [],
                    "created_at": row.get("created_at"),
                    "updated_at": row.get("updated_at"),
                    "root_path": row.get("root_path"),
                },
            }


repo_tree_snapshot_reader_v1 = RepoTreeSnapshotReaderV1()
