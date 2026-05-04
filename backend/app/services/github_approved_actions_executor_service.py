from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import uuid4

from app.services.github_service import github_service
from app.services.repo_file_patch_hub_service import repo_file_patch_hub_service
from app.utils.atomic_json_store import AtomicJsonStore

DATA_DIR = Path("data")
EXECUTOR_FILE = DATA_DIR / "github_approved_actions_executor.json"
EXECUTOR_STORE = AtomicJsonStore(
    EXECUTOR_FILE,
    default_factory=lambda: {
        "version": 1,
        "policy": "approved_github_patch_executor_no_merge_no_release_without_owner_gate",
        "executions": [],
    },
)


class GitHubApprovedActionsExecutorService:
    """Executes approved GitHub patch actions with hard safety gates.

    Phase 168 closes the gap between the Repo/File Patch Hub and a real GitHub
    executor. It may create/ensure a branch, write approved files, commit through
    the GitHub contents API and open a pull request. It never merges, releases,
    deletes files, changes credentials or bypasses checks.
    """

    SERVICE_ID = "github_approved_actions_executor"
    PLAYBOOK_ID = "approved_github_patch"
    APPROVAL_PHRASE = repo_file_patch_hub_service.APPROVAL_PHRASE
    BLOCKED_ACTIONS = {
        "merge",
        "release",
        "delete",
        "destroy",
        "force_push",
        "credential_change",
        "secret_change",
        "license_change",
        "payment_change",
    }
    BLOCKED_COMMAND_PARTS = [
        "git push --force",
        "git push -f",
        "gh release",
        "npm publish",
        "twine upload",
        "docker push",
        "rm -rf",
        "del /f",
        "rmdir /s",
    ]

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def status(self) -> Dict[str, Any]:
        state = EXECUTOR_STORE.load()
        return {
            "ok": True,
            "service": self.SERVICE_ID,
            "created_at": self._now(),
            "github_configured": github_service.is_configured(),
            "playbook": self.PLAYBOOK_ID,
            "approval_phrase": self.APPROVAL_PHRASE,
            "execution_count": len(state.get("executions") or []),
            "policy": "branch_commit_pr_only",
            "merge_allowed": False,
            "release_allowed": False,
        }

    def rules(self) -> List[str]:
        return [
            "Executa apenas planos aprovados do Repo/File Patch Hub.",
            f"A frase de aprovação obrigatória é {self.APPROVAL_PHRASE!r}.",
            "Pode criar/garantir branch, escrever ficheiros aprovados e abrir PR.",
            "Nunca faz merge, release, force push, delete, alterações de credenciais, pagamentos ou licenças.",
            "PR fica pronto para GitHub Actions; merge só depois de checks verdes e aprovação explícita do Oner.",
            "Ficheiros sensíveis e caminhos bloqueados são recusados antes da escrita.",
            "Cada execução cria registo local e também regista o run no Repo/File Patch Hub.",
        ]

    def panel(self) -> Dict[str, Any]:
        return {
            **self.status(),
            "headline": "GitHub Approved Actions Executor",
            "description": "Executor real para patches GitHub aprovados: branch, ficheiros, commits e PR, sem merge/release automáticos.",
            "primary_actions": [
                {"label": "Ver política", "endpoint": "/api/github-approved-actions/policy", "method": "GET", "safe": True},
                {"label": "Dry-run execução", "endpoint": "/api/github-approved-actions/execute", "method": "POST", "safe": True},
                {"label": "Executar aprovado", "endpoint": "/api/github-approved-actions/execute", "method": "POST", "safe": False},
            ],
            "playbook_binding": {
                "template_id": self.PLAYBOOK_ID,
                "expected_flow": "approved_github_patch -> repo_file_patch_plan -> preview -> checkpoint -> approval -> executor -> PR -> GitHub Actions -> Oner merge approval",
            },
            "rules": self.rules(),
        }

    def policy(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "service": self.SERVICE_ID,
            "playbook": self.PLAYBOOK_ID,
            "approval_phrase": self.APPROVAL_PHRASE,
            "allowed_actions": ["ensure_branch", "create_or_update_approved_files", "open_pull_request", "record_run"],
            "blocked_actions": sorted(self.BLOCKED_ACTIONS),
            "blocked_command_parts": self.BLOCKED_COMMAND_PARTS,
            "required_gates": [
                "repo_file_patch_plan_exists",
                "no_blocked_files",
                "approval_phrase_exact",
                "checkpoint_created",
                "branch_is_not_base_branch",
                "no_delete_or_sensitive_path",
                "pull_request_opened_before_checks",
                "owner_explicit_merge_approval_after_green_checks",
            ],
        }

    def latest(self) -> Dict[str, Any]:
        state = EXECUTOR_STORE.load()
        executions = state.get("executions") or []
        return {
            "ok": True,
            "service": self.SERVICE_ID,
            "latest_execution": executions[-1] if executions else None,
            "execution_count": len(executions),
        }

    async def execute(
        self,
        plan_id: str,
        approval_phrase: str,
        pr_title: Optional[str] = None,
        pr_body: Optional[str] = None,
        draft_pr: bool = False,
        dry_run: bool = True,
    ) -> Dict[str, Any]:
        plan = repo_file_patch_hub_service._find("plans", plan_id, "plan_id")
        if not plan:
            return self._error("plan_not_found", plan_id=plan_id)

        gate = self._validate_plan(plan=plan, approval_phrase=approval_phrase)
        if not gate.get("ok"):
            return gate

        approval = repo_file_patch_hub_service.approve(plan_id=plan_id, approval_phrase=approval_phrase)
        if not approval.get("ok"):
            return {"ok": False, "service": self.SERVICE_ID, "error": "repo_patch_approval_failed", "detail": approval}

        execution_id = f"github-approved-exec-{uuid4().hex[:12]}"
        files = plan.get("safe_files") or []
        validation_commands = plan.get("validation_commands") or []
        execution: Dict[str, Any] = {
            "execution_id": execution_id,
            "created_at": self._now(),
            "plan_id": plan_id,
            "target_repo": plan.get("target_repo"),
            "base_branch": plan.get("base_branch"),
            "target_branch": plan.get("target_branch"),
            "file_count": len(files),
            "dry_run": dry_run,
            "draft_pr": draft_pr,
            "validation_commands": validation_commands,
            "status": "planned" if dry_run else "running",
            "approval_id": ((approval.get("approval") or {}).get("approval_id")),
            "written_files": [],
            "blocked_actions": sorted(self.BLOCKED_ACTIONS),
            "merge_performed": False,
            "release_performed": False,
        }

        if dry_run:
            execution["planned_actions"] = self._planned_actions(plan)
            execution["status"] = "dry_run_completed"
            self._store(execution)
            repo_file_patch_hub_service.record_run(
                plan_id=plan_id,
                status="dry_run_completed",
                pr_url=None,
                validation_result={"dry_run": True, "planned_actions": execution["planned_actions"]},
                rollback_available=True,
            )
            return {"ok": True, "service": self.SERVICE_ID, "execution": execution}

        if not github_service.is_configured():
            return self._error("github_not_configured", execution=execution)

        target_repo = str(plan.get("target_repo") or "").strip()
        base_branch = str(plan.get("base_branch") or "main").strip()
        target_branch = str(plan.get("target_branch") or "").strip()

        branch = await github_service.ensure_branch_from_base(
            repository_full_name=target_repo,
            base_branch=base_branch,
            target_branch=target_branch,
        )
        if not branch.get("ok"):
            execution.update({"status": "branch_failed", "branch_result": branch})
            self._store(execution)
            return {"ok": False, "service": self.SERVICE_ID, "execution": execution}
        execution["branch_result"] = branch

        for item in files:
            write = await self._write_file(target_repo=target_repo, target_branch=target_branch, item=item)
            execution["written_files"].append(write)
            if not write.get("ok"):
                execution["status"] = "file_write_failed"
                self._store(execution)
                repo_file_patch_hub_service.record_run(
                    plan_id=plan_id,
                    status="file_write_failed",
                    pr_url=None,
                    validation_result={"failed_file": write},
                    rollback_available=True,
                )
                return {"ok": False, "service": self.SERVICE_ID, "execution": execution}

        title = pr_title or f"Phase patch: {plan.get('goal') or plan_id}"
        body = pr_body or self._default_pr_body(plan=plan, execution=execution)
        pr = await github_service.create_pull_request(
            repository_full_name=target_repo,
            title=title[:250],
            body=body,
            head_branch=target_branch,
            base_branch=base_branch,
            draft=draft_pr,
        )
        execution["pull_request"] = pr
        execution["status"] = "pr_opened" if pr.get("ok") else "pr_failed"
        execution["completed_at"] = self._now()
        self._store(execution)

        repo_file_patch_hub_service.record_run(
            plan_id=plan_id,
            status=execution["status"],
            pr_url=pr.get("html_url") if pr.get("ok") else None,
            validation_result={
                "github_actions_required": True,
                "validation_commands": validation_commands,
                "merge_blocked_until_green_checks_and_owner_approval": True,
                "pr": pr,
            },
            rollback_available=True,
        )
        return {"ok": bool(pr.get("ok")), "service": self.SERVICE_ID, "execution": execution}

    async def _write_file(self, target_repo: str, target_branch: str, item: Dict[str, Any]) -> Dict[str, Any]:
        path = str(item.get("path") or "").strip()
        change_type = str(item.get("change_type") or "update").lower().strip()
        if change_type == "delete":
            return {"ok": False, "path": path, "error": "delete_is_blocked_by_phase_168_executor"}
        existing = await github_service.get_repository_file(target_repo, path, ref=target_branch)
        sha = existing.get("sha") if existing.get("ok") else None
        result = await github_service.create_or_update_repository_file(
            repository_full_name=target_repo,
            path=path,
            content_text=str(item.get("new_content") or ""),
            commit_message=f"godmode: apply approved patch for {path}",
            branch=target_branch,
            sha=sha,
        )
        return {
            "ok": result.get("ok") is True,
            "path": path,
            "change_type": "update" if sha else "create",
            "commit_sha": result.get("commit_sha"),
            "content_sha": result.get("content_sha"),
            "write_status": result.get("write_status"),
        }

    def _validate_plan(self, plan: Dict[str, Any], approval_phrase: str) -> Dict[str, Any]:
        if approval_phrase != self.APPROVAL_PHRASE:
            return self._error("approval_phrase_required", required_phrase=self.APPROVAL_PHRASE)
        if plan.get("blocked_files"):
            return self._error("blocked_files_present", blocked_files=plan.get("blocked_files"))
        if not plan.get("safe_files"):
            return self._error("no_safe_files_to_apply")
        if plan.get("target_branch") == plan.get("base_branch"):
            return self._error("target_branch_must_not_equal_base_branch")
        if self._has_blocked_validation_command(plan.get("validation_commands") or []):
            return self._error("blocked_validation_command_present", validation_commands=plan.get("validation_commands") or [])
        for item in plan.get("safe_files") or []:
            if not item.get("safe_path"):
                return self._error("unsafe_file_in_safe_files", file=item)
            if str(item.get("change_type") or "").lower().strip() == "delete":
                return self._error("delete_change_type_blocked", file=item.get("path"))
        return {"ok": True}

    def _has_blocked_validation_command(self, commands: List[str]) -> bool:
        joined = "\n".join(commands).lower()
        return any(part in joined for part in self.BLOCKED_COMMAND_PARTS)

    def _planned_actions(self, plan: Dict[str, Any]) -> List[Dict[str, Any]]:
        return [
            {"action": "ensure_branch", "target_branch": plan.get("target_branch"), "base_branch": plan.get("base_branch")},
            {"action": "write_approved_files", "count": len(plan.get("safe_files") or []), "paths": [item.get("path") for item in plan.get("safe_files") or []]},
            {"action": "open_pull_request", "target_repo": plan.get("target_repo"), "head": plan.get("target_branch"), "base": plan.get("base_branch")},
            {"action": "wait_for_github_actions", "merge_blocked": True, "release_blocked": True},
        ]

    def _default_pr_body(self, plan: Dict[str, Any], execution: Dict[str, Any]) -> str:
        paths = "\n".join(f"- `{item.get('path')}`" for item in plan.get("safe_files") or [])
        validations = "\n".join(f"- `{cmd}`" for cmd in plan.get("validation_commands") or []) or "- GitHub Actions required"
        return (
            "## Resumo\n\n"
            f"Execução aprovada pelo God Mode para o plano `{plan.get('plan_id')}`.\n\n"
            "## Ficheiros\n\n"
            f"{paths}\n\n"
            "## Validação esperada\n\n"
            f"{validations}\n\n"
            "## Segurança\n\n"
            "- Este executor só criou branch/commits/PR.\n"
            "- Não fez merge.\n"
            "- Não fez release.\n"
            "- Não alterou segredos, credenciais, pagamentos ou licenças.\n"
            "- Merge continua bloqueado até GitHub Actions verdes e aprovação explícita do Oner.\n\n"
            f"Execution ID: `{execution.get('execution_id')}`\n"
        )

    def _store(self, execution: Dict[str, Any]) -> None:
        def mutate(state: Dict[str, Any]) -> Dict[str, Any]:
            state.setdefault("version", 1)
            state.setdefault("policy", "approved_github_patch_executor_no_merge_no_release_without_owner_gate")
            state.setdefault("executions", [])
            state["executions"].append(execution)
            state["executions"] = state["executions"][-200:]
            return state

        EXECUTOR_STORE.update(mutate)

    def _error(self, error: str, **extra: Any) -> Dict[str, Any]:
        return {"ok": False, "service": self.SERVICE_ID, "error": error, **extra}

    def package(self) -> Dict[str, Any]:
        return {"status": self.status(), "panel": self.panel(), "policy": self.policy(), "latest": self.latest()}


github_approved_actions_executor_service = GitHubApprovedActionsExecutorService()
