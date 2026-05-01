from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import uuid4

from app.services.github_memory_sync_service import github_memory_sync_service
from app.services.github_service import github_service
from app.services.memory_core_service import memory_core_service
from app.services.repo_file_patch_hub_service import repo_file_patch_hub_service
from app.utils.atomic_json_store import AtomicJsonStore

DATA_DIR = Path("data")
EXECUTOR_FILE = DATA_DIR / "repo_file_patch_executor.json"
EXECUTOR_STORE = AtomicJsonStore(
    EXECUTOR_FILE,
    default_factory=lambda: {
        "version": 1,
        "policy": "execute_approved_repo_patch_plan_to_branch_and_pull_request",
        "executions": [],
    },
)


class RepoFilePatchExecutorService:
    """Real executor for approved Repo File Patch Hub plans.

    This executor creates/uses the approved target branch, writes the exact safe
    files from the approved plan, opens a pull request, records the run and syncs
    technical memory to AndreVazao/andreos-memory.
    """

    EXECUTION_PHRASE = "EXECUTE APPROVED REPO PATCH"

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def policy(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "mode": "repo_file_patch_executor_policy",
            "execution_phrase": self.EXECUTION_PHRASE,
            "rules": [
                "execute only approved plans from Repo File Patch Hub",
                "never execute plans with blocked files",
                "create or reuse target branch from base branch",
                "write exact safe file contents only",
                "open pull request instead of pushing directly to main",
                "record run metadata back into Repo File Patch Hub",
                "sync technical programming memory into AndreVazao/andreos-memory",
            ],
        }

    def _find_approved_plan(self, plan_id: str) -> Dict[str, Any]:
        latest = repo_file_patch_hub_service.latest()
        state = repo_file_patch_hub_service.__dict__
        # Access through service helper for plans; approvals are persisted inside the hub store.
        plan = repo_file_patch_hub_service._find("plans", plan_id, "plan_id")
        approval = repo_file_patch_hub_service._find("approvals", plan_id, "plan_id")
        return {"plan": plan, "approval": approval, "latest": latest}

    def _pr_body(self, plan: Dict[str, Any], execution_id: str, written_files: List[Dict[str, Any]]) -> str:
        files = "\n".join(f"- `{item.get('path')}`" for item in written_files) or "- Sem ficheiros escritos."
        validation = "\n".join(f"- `{cmd}`" for cmd in plan.get("validation_commands", [])) or "- Sem validações definidas."
        return (
            f"## God Mode Repo Patch\n\n"
            f"Execution: `{execution_id}`\n"
            f"Plan: `{plan.get('plan_id')}`\n"
            f"Project: `{plan.get('project_id')}`\n"
            f"Goal: {plan.get('goal')}\n\n"
            f"## Files\n{files}\n\n"
            f"## Validation commands\n{validation}\n\n"
            f"## Safety\n"
            f"- Created by approved God Mode Repo File Patch Executor.\n"
            f"- Source plan required preview, checkpoint and approval.\n"
            f"- Sensitive paths are blocked before execution.\n"
            f"- Review this PR before merge.\n"
        )

    async def execute(
        self,
        plan_id: str,
        execution_phrase: str,
        open_pr: bool = True,
        draft_pr: bool = False,
        memory_repo: str = "AndreVazao/andreos-memory",
        dry_run: bool = False,
    ) -> Dict[str, Any]:
        if execution_phrase != self.EXECUTION_PHRASE:
            return {
                "ok": False,
                "mode": "repo_file_patch_executor_execution",
                "error": "execution_phrase_required",
                "required_phrase": self.EXECUTION_PHRASE,
            }
        if not github_service.is_configured():
            return {"ok": False, "mode": "repo_file_patch_executor_execution", "error": "github_not_configured"}

        found = self._find_approved_plan(plan_id)
        plan = found.get("plan")
        approval = found.get("approval")
        if not plan:
            return {"ok": False, "mode": "repo_file_patch_executor_execution", "error": "plan_not_found"}
        if not approval:
            return {"ok": False, "mode": "repo_file_patch_executor_execution", "error": "plan_not_approved"}
        if plan.get("blocked_files"):
            return {"ok": False, "mode": "repo_file_patch_executor_execution", "error": "blocked_files_present", "blocked_files": plan.get("blocked_files")}

        execution_id = f"repo-patch-execution-{uuid4().hex[:12]}"
        repo = plan.get("target_repo")
        base_branch = plan.get("base_branch") or "main"
        target_branch = plan.get("target_branch") or f"godmode-auto/{uuid4().hex[:8]}"
        safe_files = plan.get("safe_files") or []

        branch_result: Dict[str, Any] = {"dry_run": True, "target_branch": target_branch}
        written_files: List[Dict[str, Any]] = []
        pr_result: Dict[str, Any] = {"skipped": True}

        if not dry_run:
            branch_result = await github_service.ensure_branch_from_base(repo, base_branch, target_branch)
            if not branch_result.get("ok"):
                return {"ok": False, "mode": "repo_file_patch_executor_execution", "error": "branch_prepare_failed", "branch_result": branch_result}

        for file_change in safe_files:
            path = file_change.get("path")
            new_content = file_change.get("new_content")
            if not path or not isinstance(new_content, str):
                written_files.append({"ok": False, "path": path, "error": "missing_path_or_new_content"})
                continue
            existing = {"ok": False, "file_status": "not_checked_dry_run"}
            if not dry_run:
                existing = await github_service.get_repository_file(repo, path, ref=target_branch)
                result = await github_service.create_or_update_repository_file(
                    repository_full_name=repo,
                    path=path,
                    content_text=new_content,
                    commit_message=f"{plan.get('goal')}: {path}",
                    branch=target_branch,
                    sha=existing.get("sha") if existing.get("ok") else None,
                )
            else:
                result = {"ok": True, "mode": "dry_run_file_write", "repository_full_name": repo, "path": path, "branch": target_branch, "write_status": "planned"}
            written_files.append(result)

        failed_files = [item for item in written_files if not item.get("ok")]
        if failed_files:
            status = "failed"
        else:
            status = "dry_run" if dry_run else "completed"

        if open_pr and not dry_run and not failed_files:
            pr_result = await github_service.create_pull_request(
                repository_full_name=repo,
                title=f"God Mode patch: {plan.get('goal')}",
                body=self._pr_body(plan, execution_id, written_files),
                head_branch=target_branch,
                base_branch=base_branch,
                draft=draft_pr,
            )

        run_record = repo_file_patch_hub_service.record_run(
            plan_id=plan_id,
            status=status,
            pr_url=pr_result.get("html_url") if isinstance(pr_result, dict) else None,
            validation_result={
                "validation_commands": plan.get("validation_commands", []),
                "executor_note": "commands_registered_for_operator_or_ci_execution",
                "dry_run": dry_run,
            },
            rollback_available=True,
        )

        project_id = plan.get("project_id") or "GOD_MODE"
        memory_core_service.write_history(
            project_id,
            action=f"Executed approved repo patch plan {plan_id} on {repo}",
            result=f"Status: {status}\nBranch: {target_branch}\nPR: {pr_result.get('html_url') if isinstance(pr_result, dict) else ''}",
        )
        memory_core_service.update_last_session(
            project_id,
            summary=f"Repo patch executor ran plan {plan_id} for {repo} with status {status}.",
            next_steps="Review PR, run validations, merge only after approval, then archive/record final outcome.",
        )
        memory_sync = await github_memory_sync_service.record_repo_work_and_sync(
            project_name=project_id,
            repo_full_name=repo,
            summary=f"Executed approved repo patch plan {plan_id}",
            result=f"Status: {status}; branch: {target_branch}; PR: {pr_result.get('html_url') if isinstance(pr_result, dict) else ''}",
            next_steps="Review PR and validation results before merge.",
            memory_repo=memory_repo,
            dry_run=dry_run,
        )

        execution = {
            "execution_id": execution_id,
            "created_at": self._now(),
            "plan_id": plan_id,
            "project_id": project_id,
            "target_repo": repo,
            "base_branch": base_branch,
            "target_branch": target_branch,
            "dry_run": dry_run,
            "status": status,
            "branch_result": branch_result,
            "written_files": written_files,
            "pr_result": pr_result,
            "run_record": run_record,
            "memory_sync": memory_sync,
        }
        self._store(execution)
        return {"ok": status in {"completed", "dry_run"}, "mode": "repo_file_patch_executor_execution", "execution": execution}

    def _store(self, execution: Dict[str, Any]) -> None:
        def mutate(state: Dict[str, Any]) -> Dict[str, Any]:
            state.setdefault("version", 1)
            state.setdefault("policy", "execute_approved_repo_patch_plan_to_branch_and_pull_request")
            state.setdefault("executions", [])
            state["executions"].append(execution)
            state["executions"] = state["executions"][-200:]
            return state

        EXECUTOR_STORE.update(mutate)

    def latest(self) -> Dict[str, Any]:
        state = EXECUTOR_STORE.load()
        executions = state.get("executions") or []
        return {
            "ok": True,
            "mode": "repo_file_patch_executor_latest",
            "latest_execution": executions[-1] if executions else None,
            "execution_count": len(executions),
        }

    def get_status(self) -> Dict[str, Any]:
        latest = self.latest()
        return {
            "ok": True,
            "mode": "repo_file_patch_executor_status",
            "github_configured": github_service.is_configured(),
            "execution_phrase": self.EXECUTION_PHRASE,
            "execution_count": latest.get("execution_count", 0),
            "latest_status": ((latest.get("latest_execution") or {}).get("status")),
        }

    def panel(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "mode": "repo_file_patch_executor_panel",
            "headline": "Executor real de patches aprovados para repos",
            "policy": self.policy(),
            "status": self.get_status(),
            "latest": self.latest(),
            "safe_buttons": [
                {"id": "status", "label": "Estado", "endpoint": "/api/repo-file-patch-executor/status", "priority": "high"},
                {"id": "execute", "label": "Executar plano aprovado", "endpoint": "/api/repo-file-patch-executor/execute", "priority": "critical"},
                {"id": "latest", "label": "Última execução", "endpoint": "/api/repo-file-patch-executor/latest", "priority": "high"},
            ],
        }


repo_file_patch_executor_service = RepoFilePatchExecutorService()
