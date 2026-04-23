from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from app.services.env_vault_import_service import env_vault_import_service


class RepoEnvHarvestService:
    def __init__(self, harvest_store: str = "data/repo_env_harvest_store.json") -> None:
        self.harvest_store = Path(harvest_store)
        self.harvest_store.parent.mkdir(parents=True, exist_ok=True)
        if not self.harvest_store.exists():
            self.harvest_store.write_text(json.dumps({"harvests": []}, ensure_ascii=False, indent=2), encoding="utf-8")

    def _read_store(self) -> Dict[str, Any]:
        return json.loads(self.harvest_store.read_text(encoding="utf-8"))

    def _write_store(self, payload: Dict[str, Any]) -> None:
        self.harvest_store.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    def get_status(self) -> Dict[str, Any]:
        store = self._read_store()
        return {
            "ok": True,
            "mode": "repo_env_harvest_status",
            "store_path": str(self.harvest_store),
            "harvest_count": len(store.get("harvests", [])),
            "status": "repo_env_harvest_ready",
        }

    def harvest_repo_env_sources(
        self,
        repository_name: str,
        target_project: str,
        environment_name: str,
        env_sources: List[Dict[str, str]],
    ) -> Dict[str, Any]:
        harvested: List[Dict[str, Any]] = []
        for source in env_sources:
            source_name = source.get("source_name") or source.get("path") or "unknown-env-source"
            env_text = source.get("env_text") or ""
            path = source.get("path") or source_name
            import_result = env_vault_import_service.import_env_text(
                env_text=env_text,
                source_name=f"{repository_name}:{path}",
                target_project=target_project,
                environment_name=environment_name,
            )
            harvested.append(
                {
                    "source_name": source_name,
                    "path": path,
                    "import_status": import_result.get("import_status"),
                    "imported_count": import_result.get("imported_count", 0),
                }
            )
        store = self._read_store()
        record = {
            "repository_name": repository_name,
            "target_project": target_project,
            "environment_name": environment_name,
            "source_count": len(env_sources),
            "harvested": harvested,
        }
        harvests = store.get("harvests", [])
        harvests.append(record)
        store["harvests"] = harvests
        self._write_store(store)
        return {
            "ok": True,
            "mode": "repo_env_harvest_result",
            "harvest_status": "repo_env_sources_harvested",
            "repository_name": repository_name,
            "target_project": target_project,
            "environment_name": environment_name,
            "source_count": len(env_sources),
            "harvested_count": len(harvested),
            "harvested": harvested,
        }

    def get_package(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "mode": "repo_env_harvest_package",
            "package": {
                "status": self.get_status(),
                "package_status": "repo_env_harvest_ready",
            },
        }


repo_env_harvest_service = RepoEnvHarvestService()
