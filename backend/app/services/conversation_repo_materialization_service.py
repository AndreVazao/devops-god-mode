from __future__ import annotations

import json
import threading
from pathlib import Path
from typing import Any, Dict, List

from app.services.conversation_bundle_service import conversation_bundle_service
from app.services.conversation_reconciliation_service import conversation_reconciliation_service


class ConversationRepoMaterializationService:
    def __init__(self, workspace_root: str = "data/conversation_repo_materializations") -> None:
        self.workspace_root = Path(workspace_root)
        self.workspace_root.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()

    def get_status(self) -> Dict[str, Any]:
        bundles = [p for p in self.workspace_root.iterdir()] if self.workspace_root.exists() else []
        return {
            "ok": True,
            "mode": "conversation_repo_materialization_status",
            "workspace_root": str(self.workspace_root),
            "materialized_bundle_count": len([p for p in bundles if p.is_dir()]),
            "status": "conversation_repo_materialization_ready",
        }

    def _build_effective_file_plan(self, bundle_id: str, repository_name: str | None) -> Dict[str, Any]:
        report_result = conversation_reconciliation_service.get_report(bundle_id)
        if report_result.get("ok"):
            report = report_result["report"]
            repo_name = repository_name or report.get("project_key") or "repo"
            file_plan = []
            for item in report.get("deduplicated_blocks", []):
                file_plan.append(
                    {
                        "destination_path": item.get("destination_path"),
                        "language": item.get("language"),
                        "line_count": item.get("line_count"),
                        "content_full": item.get("code") or "",
                        "provider": item.get("provider") or "unknown",
                        "source_kind": item.get("source_status") or "reconciled",
                    }
                )
            return {
                "ok": True,
                "plan": {
                    "bundle_id": bundle_id,
                    "repository_name": repo_name,
                    "file_plan": file_plan,
                    "plan_status": "repo_plan_ready",
                    "source_mode": "reconciled_report",
                },
            }

        return conversation_bundle_service.build_repo_materialization_plan(
            bundle_id=bundle_id,
            repository_name=repository_name,
        )

    def materialize_bundle_repo_plan(
        self,
        bundle_id: str,
        repository_name: str | None = None,
        overwrite_existing: bool = True,
    ) -> Dict[str, Any]:
        plan_result = self._build_effective_file_plan(
            bundle_id=bundle_id,
            repository_name=repository_name,
        )
        if not plan_result.get("ok"):
            return {
                "ok": False,
                "mode": "conversation_repo_materialization_result",
                "materialization_status": "bundle_not_found",
                "bundle_id": bundle_id,
            }

        plan = plan_result["plan"]
        repo_name = str(plan.get("repository_name") or "repo")
        bundle_dir = self.workspace_root / f"{bundle_id}_{repo_name}"
        materialized_files: List[Dict[str, Any]] = []

        with self._lock:
            bundle_dir.mkdir(parents=True, exist_ok=True)
            for index, file_plan in enumerate(plan.get("file_plan", []), start=1):
                destination_path = str(file_plan.get("destination_path") or f"generated/snippet_{index}.txt")
                target_path = bundle_dir / destination_path
                target_path.parent.mkdir(parents=True, exist_ok=True)
                if target_path.exists() and not overwrite_existing:
                    continue
                content_full = str(file_plan.get("content_full") or file_plan.get("content_preview") or "")
                language = str(file_plan.get("language") or "text")
                provider = str(file_plan.get("provider") or "unknown")
                source_kind = str(file_plan.get("source_kind") or "conversation_code_block")
                target_path.write_text(
                    f"# materialized_from_conversation_bundle\n"
                    f"# bundle_id: {bundle_id}\n"
                    f"# language: {language}\n"
                    f"# provider: {provider}\n"
                    f"# source_kind: {source_kind}\n\n"
                    f"{content_full}\n",
                    encoding="utf-8",
                )
                materialized_files.append(
                    {
                        "destination_path": destination_path,
                        "materialized_file": str(target_path),
                        "language": language,
                        "line_count": int(file_plan.get("line_count") or 0),
                        "provider": provider,
                        "source_kind": source_kind,
                    }
                )

            manifest_path = bundle_dir / "repo-materialization.manifest.json"
            manifest_path.write_text(
                json.dumps(
                    {
                        "bundle_id": bundle_id,
                        "repository_name": repo_name,
                        "bundle_dir": str(bundle_dir),
                        "source_mode": plan.get("source_mode") or "raw_plan",
                        "materialized_files": materialized_files,
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )

        return {
            "ok": True,
            "mode": "conversation_repo_materialization_result",
            "materialization_status": "repo_plan_materialized",
            "bundle_id": bundle_id,
            "repository_name": repo_name,
            "bundle_dir": str(bundle_dir),
            "manifest_file": str(manifest_path),
            "materialized_count": len(materialized_files),
            "materialized_files": materialized_files,
            "source_mode": plan.get("source_mode") or "raw_plan",
        }

    def get_package(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "mode": "conversation_repo_materialization_package",
            "package": {
                "status": self.get_status(),
                "bundles": conversation_bundle_service.list_bundles(),
                "package_status": "conversation_repo_materialization_ready",
            },
        }


conversation_repo_materialization_service = ConversationRepoMaterializationService()
