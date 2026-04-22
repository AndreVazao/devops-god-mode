import base64
from typing import Any, Dict, List

from app.services.external_asset_intake_service import external_asset_intake_service
from app.services.github_service import github_service


class ExternalAssetPublishExecutionService:
    def _resolve_asset_payload(self, staged_asset: Dict[str, Any]) -> Dict[str, Any]:
        content_text = staged_asset.get("content_text")
        content_base64 = staged_asset.get("content_base64")
        content_kind = staged_asset.get("content_kind") or "reference_only"
        if content_text is not None:
            return {
                "payload_mode": "text",
                "content_text": content_text,
                "content_kind": content_kind,
            }
        if content_base64 is not None:
            return {
                "payload_mode": "binary",
                "raw_bytes": base64.b64decode(content_base64),
                "content_kind": content_kind,
            }
        return {
            "payload_mode": "reference_only",
            "content_kind": content_kind,
        }

    def get_status(self) -> Dict[str, Any]:
        package = external_asset_intake_service.get_package()["package"]
        return {
            "ok": True,
            "mode": "external_asset_publish_execution_status",
            "github_configured": github_service.is_configured(),
            "staged_count": package["staged_count"],
            "inline_ready_count": package["inline_ready_count"],
            "status": "external_asset_publish_execution_ready",
        }

    async def execute_publish_plan(
        self,
        repository_full_name: str,
        project_hint: str | None = None,
        branch: str | None = None,
        dry_run: bool = True,
    ) -> Dict[str, Any]:
        plan = external_asset_intake_service.build_github_publish_plan(
            repository_full_name=repository_full_name,
            project_hint=project_hint,
        )
        results: List[Dict[str, Any]] = []
        for item in plan["planned_items"]:
            staged_asset = external_asset_intake_service.get_staged_asset_by_id(
                item["staged_asset_id"]
            )
            if not staged_asset:
                results.append(
                    {
                        **item,
                        "publish_status": "missing_staged_asset",
                    }
                )
                continue

            payload = self._resolve_asset_payload(staged_asset)
            if dry_run or not github_service.is_configured():
                results.append(
                    {
                        **item,
                        "publish_status": "dry_run_ready",
                        "payload_mode": payload["payload_mode"],
                        "github_configured": github_service.is_configured(),
                    }
                )
                continue

            if payload["payload_mode"] == "text":
                write_result = await github_service.create_or_update_repository_file(
                    repository_full_name=repository_full_name,
                    path=item["destination_path"],
                    content_text=payload["content_text"],
                    commit_message=f"Publish asset {item['asset_role']} from God Mode",
                    branch=branch,
                )
            elif payload["payload_mode"] == "binary":
                write_result = await github_service.create_or_update_repository_asset(
                    repository_full_name=repository_full_name,
                    path=item["destination_path"],
                    raw_bytes=payload["raw_bytes"],
                    commit_message=f"Publish asset {item['asset_role']} from God Mode",
                    branch=branch,
                )
            else:
                write_result = {
                    "ok": False,
                    "mode": "github_repository_asset_written",
                    "write_status": "reference_only_asset_needs_fetch",
                }

            results.append(
                {
                    **item,
                    "payload_mode": payload["payload_mode"],
                    "publish_status": write_result.get("write_status", "unknown"),
                    "write_result": write_result,
                }
            )

        return {
            "ok": True,
            "mode": "external_asset_publish_execution_result",
            "repository_full_name": repository_full_name,
            "project_hint": project_hint,
            "branch": branch,
            "dry_run": dry_run,
            "github_configured": github_service.is_configured(),
            "executed_count": len(results),
            "results": results,
        }

    def get_package(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "mode": "external_asset_publish_execution_package",
            "package": {
                "status": self.get_status(),
                "intake_package": external_asset_intake_service.get_package(),
                "package_status": "external_asset_publish_execution_ready",
            },
        }


external_asset_publish_execution_service = ExternalAssetPublishExecutionService()
