from __future__ import annotations

import json
import os
import shutil
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import uuid4

from app.services.local_tool_capability_scan_service import local_tool_capability_scan_service
from app.utils.atomic_json_store import AtomicJsonStore

DATA_DIR = Path("data")
BACKUP_DIR = DATA_DIR / "backups"
BOOTSTRAP_FILE = DATA_DIR / "local_bootstrap_backup.json"
BOOTSTRAP_STORE = AtomicJsonStore(
    BOOTSTRAP_FILE,
    default_factory=lambda: {
        "version": 1,
        "policy": "approved_local_bootstrap_and_portable_backup_restore",
        "bootstrap_plans": [],
        "backup_runs": [],
        "restore_previews": [],
    },
)


class LocalBootstrapBackupService:
    """Prepare local tool installation/configuration and portable backup packs.

    Installation is planned and script-generated, not silently executed. Backup is
    real but allowlisted and excludes sensitive access material by default.
    """

    REQUIRED_TOOLS = [
        {
            "tool_id": "git",
            "label": "Git",
            "priority": "critical",
            "reason": "clone, diff, local commits and GitHub handoff",
            "winget": "Git.Git",
            "fallback": "manual_download",
            "light_pc": True,
        },
        {
            "tool_id": "python",
            "label": "Python",
            "priority": "critical",
            "reason": "backend, validators and local scripts",
            "winget": "Python.Python.3.12",
            "fallback": "manual_download",
            "light_pc": True,
        },
        {
            "tool_id": "vscode",
            "label": "Visual Studio Code",
            "priority": "high",
            "reason": "manual review and local code editing",
            "winget": "Microsoft.VisualStudioCode",
            "fallback": "manual_download",
            "light_pc": True,
        },
        {
            "tool_id": "node",
            "label": "Node.js LTS",
            "priority": "high",
            "reason": "frontend/mobile shell builds",
            "winget": "OpenJS.NodeJS.LTS",
            "fallback": "manual_download",
            "light_pc": True,
        },
        {
            "tool_id": "obsidian",
            "label": "Obsidian",
            "priority": "high",
            "reason": "AndreOS project memory and operator context",
            "winget": "Obsidian.Obsidian",
            "fallback": "manual_download",
            "light_pc": True,
        },
        {
            "tool_id": "chrome_edge",
            "label": "Browser modernizado",
            "priority": "high",
            "reason": "manual login, provider sessions and web review",
            "winget": "Google.Chrome",
            "fallback": "use_edge_if_available",
            "light_pc": True,
        },
        {
            "tool_id": "android_sdk",
            "label": "Android SDK / ADB",
            "priority": "medium",
            "reason": "phone pairing, APK install and Android debug",
            "winget": "Google.PlatformTools",
            "fallback": "github_actions_for_builds",
            "light_pc": False,
        },
        {
            "tool_id": "ollama",
            "label": "Ollama / Local AI",
            "priority": "optional",
            "reason": "offline summaries and local drafts on stronger PCs",
            "winget": "Ollama.Ollama",
            "fallback": "skip_on_weak_pc",
            "light_pc": False,
        },
    ]

    BACKUP_ALLOWLIST = [
        "memory",
        "data",
        "docs",
        "frontend/mobile-shell/backend-presets.example.json",
        "frontend/mobile-shell/apk-launch-config.json",
        "desktop/GodModeDesktop.spec",
        "desktop/windows_autostart_bootstrap.ps1",
        "desktop/windows_autostart_remove.ps1",
        "desktop/windows_shortcut_bootstrap.ps1",
        "scripts/windows",
        "README.md",
        "PROJECT_TREE.txt",
    ]

    SENSITIVE_NAME_PARTS = [
        ".env",
        "secret",
        "token",
        "password",
        "cookie",
        "credential",
        "authorization",
        "bearer",
        "api_key",
        "apikey",
        "private_key",
    ]

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def _repo_root(self) -> Path:
        return Path.cwd()

    def _is_windows(self) -> bool:
        return os.name == "nt"

    def _is_sensitive_path(self, path: Path) -> bool:
        lowered = str(path).lower().replace("\\", "/")
        return any(part in lowered for part in self.SENSITIVE_NAME_PARTS)

    def requirements(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "mode": "local_bootstrap_requirements",
            "required_tools": self.REQUIRED_TOOLS,
            "backup_allowlist": self.BACKUP_ALLOWLIST,
            "sensitive_exclusions_enabled": True,
        }

    def bootstrap_plan(self, pc_profile: str = "auto") -> Dict[str, Any]:
        scan = local_tool_capability_scan_service.scan().get("scan", {})
        tools = {tool.get("tool_id"): tool for tool in scan.get("tools", [])}
        weak_pc = self._infer_weak_pc(pc_profile, scan)
        missing: List[Dict[str, Any]] = []
        available: List[Dict[str, Any]] = []
        skipped: List[Dict[str, Any]] = []
        configure_steps: List[Dict[str, Any]] = []

        for requirement in self.REQUIRED_TOOLS:
            tool = tools.get(requirement["tool_id"], {})
            item = {**requirement, "detected_status": tool.get("status", "not_found"), "detected_paths": tool.get("path_hits", []) + tool.get("command_hits", [])}
            if tool.get("available"):
                available.append(item)
                configure_steps.extend(self._configure_steps_for(requirement["tool_id"], already_available=True))
            elif weak_pc and not requirement.get("light_pc", True):
                item["skip_reason"] = "weak_pc_prefer_cloud_or_manual"
                skipped.append(item)
            else:
                missing.append(item)
                configure_steps.extend(self._configure_steps_for(requirement["tool_id"], already_available=False))

        plan = {
            "plan_id": f"local-bootstrap-plan-{uuid4().hex[:12]}",
            "created_at": self._now(),
            "pc_profile": pc_profile,
            "weak_pc_detected": weak_pc,
            "status": "ready_for_operator_review",
            "available_tools": available,
            "missing_tools": missing,
            "skipped_tools": skipped,
            "configure_steps": configure_steps,
            "install_script_preview": self._powershell_script(missing, configure_steps, execute=False),
            "manual_strategy": self._manual_strategy(missing, skipped),
            "approval_required_before_install": True,
            "read_only_until_operator_approves": True,
            "operator_next": {
                "label": "Gerar script de instalação/configuração",
                "endpoint": "/api/local-bootstrap-backup/install-script",
                "route": "/app/home",
            },
        }
        self._store_plan(plan)
        return {"ok": True, "mode": "local_bootstrap_plan", "plan": plan}

    def _infer_weak_pc(self, pc_profile: str, scan: Dict[str, Any]) -> bool:
        if pc_profile in {"weak", "old", "legacy"}:
            return True
        if pc_profile in {"strong", "new", "powerful"}:
            return False
        # Conservative auto mode: if Android SDK/Node are absent and partial Android is present, prefer cloud for heavy tasks.
        tools = {tool.get("tool_id"): tool for tool in scan.get("tools", [])}
        android_partial = tools.get("android_studio", {}).get("status") == "partial_or_broken"
        android_sdk_missing = tools.get("android_sdk", {}).get("status") == "not_found"
        return bool(android_partial and android_sdk_missing)

    def _configure_steps_for(self, tool_id: str, already_available: bool) -> List[Dict[str, Any]]:
        prefix = "verify" if already_available else "configure_after_install"
        mapping = {
            "git": ["check_git_version", "set_safe_directory_policy", "prepare_local_workspace"],
            "python": ["check_python_version", "prepare_venv_policy", "verify_pip"],
            "node": ["check_node_version", "verify_npm", "prepare_frontend_cache_policy"],
            "vscode": ["verify_code_command", "prepare_manual_review_workspace"],
            "obsidian": ["verify_andreos_vault_path", "prepare_obsidian_uri_links"],
            "chrome_edge": ["verify_browser_available", "prepare_manual_login_policy"],
            "android_sdk": ["verify_adb", "prepare_phone_pairing_policy", "prefer_github_actions_if_sdk_missing"],
            "ollama": ["verify_local_ai_service", "mark_optional_local_summary_support"],
        }
        return [
            {
                "step_id": f"{prefix}_{step}",
                "tool_id": tool_id,
                "label": step.replace("_", " "),
                "approval_required": False,
            }
            for step in mapping.get(tool_id, ["verify_tool_available"])
        ]

    def _manual_strategy(self, missing: List[Dict[str, Any]], skipped: List[Dict[str, Any]]) -> Dict[str, Any]:
        return {
            "if_winget_unavailable": "mostrar lista manual de downloads/instalação e continuar com o que existir",
            "if_pc_is_weak": "instalar apenas ferramentas leves e usar GitHub Actions para builds pesados",
            "if_tool_fails": "marcar como partial_or_broken e não insistir",
            "missing_tool_ids": [item["tool_id"] for item in missing],
            "skipped_tool_ids": [item["tool_id"] for item in skipped],
        }

    def install_script(self, pc_profile: str = "auto", destination_path: Optional[str] = None) -> Dict[str, Any]:
        plan = self.bootstrap_plan(pc_profile=pc_profile).get("plan", {})
        script = self._powershell_script(plan.get("missing_tools", []), plan.get("configure_steps", []), execute=True)
        scripts_dir = DATA_DIR / "generated_scripts"
        scripts_dir.mkdir(parents=True, exist_ok=True)
        target = Path(destination_path) if destination_path else scripts_dir / "godmode_local_bootstrap.ps1"
        if target.exists() and target.is_dir():
            target = target / "godmode_local_bootstrap.ps1"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(script, encoding="utf-8")
        return {
            "ok": True,
            "mode": "local_bootstrap_install_script",
            "script_path": str(target),
            "plan_id": plan.get("plan_id"),
            "approval_required_before_running": True,
            "how_to_use": [
                "Rever o script no painel/ficheiro.",
                "Executar apenas se o operador aprovar.",
                "Se uma ferramenta falhar, continuar com restantes e atualizar scan.",
            ],
        }

    def _powershell_script(self, missing: List[Dict[str, Any]], configure_steps: List[Dict[str, Any]], execute: bool) -> str:
        lines = [
            "$ErrorActionPreference = 'Continue'",
            "Write-Host 'God Mode local bootstrap - approved operator script'",
            "Write-Host 'This script installs/configures only selected local tools.'",
            "",
            "function Has-Winget { return [bool](Get-Command winget -ErrorAction SilentlyContinue) }",
            "function Install-WingetPackage($Id, $Label) {",
            "  if (-not (Has-Winget)) { Write-Host \"winget not available. Manual install needed for $Label\"; return }",
            "  Write-Host \"Installing $Label ($Id)...\"",
            "  winget install --id $Id --exact --accept-package-agreements --accept-source-agreements",
            "}",
            "",
        ]
        if not missing:
            lines.append("Write-Host 'No missing critical tools detected in latest plan.'")
        for item in missing:
            package_id = item.get("winget")
            label = item.get("label")
            if package_id:
                if execute:
                    lines.append(f"Install-WingetPackage -Id '{package_id}' -Label '{label}'")
                else:
                    lines.append(f"# Install-WingetPackage -Id '{package_id}' -Label '{label}'")
            else:
                lines.append(f"Write-Host 'Manual install required: {label}'")
        lines.extend([
            "",
            "Write-Host 'Configuration checks:'",
        ])
        for step in configure_steps:
            lines.append(f"Write-Host '- {step.get('tool_id')}: {step.get('label')}'")
        lines.extend([
            "",
            "Write-Host 'Run /api/local-tool-capability/scan after installation to refresh capabilities.'",
        ])
        return "\n".join(lines) + "\n"

    def create_backup(self, destination_path: Optional[str] = None, include_data: bool = True) -> Dict[str, Any]:
        BACKUP_DIR.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        backup_id = f"godmode-backup-{stamp}-{uuid4().hex[:8]}"
        target = Path(destination_path) if destination_path else BACKUP_DIR / f"{backup_id}.zip"
        if target.exists() and target.is_dir():
            target = target / f"{backup_id}.zip"
        target.parent.mkdir(parents=True, exist_ok=True)
        manifest = {
            "backup_id": backup_id,
            "created_at": self._now(),
            "policy": "portable_backup_without_sensitive_access_material",
            "include_data": include_data,
            "allowlist": self.BACKUP_ALLOWLIST,
            "excluded_sensitive_paths": [],
            "files": [],
        }
        with zipfile.ZipFile(target, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            for entry in self.BACKUP_ALLOWLIST:
                if entry == "data" and not include_data:
                    continue
                self._add_entry_to_zip(zf, Path(entry), manifest)
            zf.writestr("BACKUP_MANIFEST.json", json.dumps(manifest, indent=2, ensure_ascii=False))
            zf.writestr("RESTORE_README.txt", self._restore_readme())
        run = {
            "backup_id": backup_id,
            "created_at": self._now(),
            "zip_path": str(target),
            "file_count": len(manifest["files"]),
            "excluded_sensitive_count": len(manifest["excluded_sensitive_paths"]),
            "include_data": include_data,
        }
        self._store_backup_run(run)
        return {"ok": True, "mode": "local_backup_created", "backup": run, "manifest": manifest}

    def _add_entry_to_zip(self, zf: zipfile.ZipFile, entry: Path, manifest: Dict[str, Any]) -> None:
        root = self._repo_root()
        path = root / entry
        if not path.exists():
            return
        if path.is_file():
            self._add_file_to_zip(zf, path, root, manifest)
            return
        for file_path in path.rglob("*"):
            if file_path.is_file():
                self._add_file_to_zip(zf, file_path, root, manifest)

    def _add_file_to_zip(self, zf: zipfile.ZipFile, file_path: Path, root: Path, manifest: Dict[str, Any]) -> None:
        rel = file_path.relative_to(root)
        if self._is_sensitive_path(rel):
            manifest["excluded_sensitive_paths"].append(str(rel))
            return
        try:
            zf.write(file_path, arcname=str(rel).replace("\\", "/"))
            manifest["files"].append(str(rel).replace("\\", "/"))
        except Exception as exc:
            manifest.setdefault("errors", []).append({"path": str(rel), "error": exc.__class__.__name__, "detail": str(exc)[:200]})

    def _restore_readme(self) -> str:
        return (
            "God Mode portable backup\n"
            "1. Install God Mode on the new PC.\n"
            "2. Copy this zip from USB/disk to the new PC.\n"
            "3. Use /api/local-bootstrap-backup/restore-preview to inspect contents.\n"
            "4. Restore only after operator confirmation.\n"
            "5. Sensitive access material is intentionally excluded by default.\n"
        )

    def restore_preview(self, backup_path: str) -> Dict[str, Any]:
        target = Path(backup_path)
        if not target.exists() or not target.is_file():
            return {"ok": False, "mode": "local_restore_preview", "error": "backup_not_found", "backup_path": backup_path}
        with zipfile.ZipFile(target, "r") as zf:
            names = zf.namelist()
            manifest = {}
            if "BACKUP_MANIFEST.json" in names:
                manifest = json.loads(zf.read("BACKUP_MANIFEST.json").decode("utf-8"))
        preview = {
            "preview_id": f"restore-preview-{uuid4().hex[:12]}",
            "created_at": self._now(),
            "backup_path": str(target),
            "file_count": len(names),
            "manifest": manifest,
            "will_not_overwrite_without_explicit_restore": True,
        }
        self._store_restore_preview(preview)
        return {"ok": True, "mode": "local_restore_preview", "preview": preview}

    def _store_plan(self, plan: Dict[str, Any]) -> None:
        def mutate(state: Dict[str, Any]) -> Dict[str, Any]:
            state.setdefault("bootstrap_plans", [])
            state["bootstrap_plans"].append(plan)
            state["bootstrap_plans"] = state["bootstrap_plans"][-100:]
            return state

        BOOTSTRAP_STORE.update(mutate)

    def _store_backup_run(self, run: Dict[str, Any]) -> None:
        def mutate(state: Dict[str, Any]) -> Dict[str, Any]:
            state.setdefault("backup_runs", [])
            state["backup_runs"].append(run)
            state["backup_runs"] = state["backup_runs"][-100:]
            return state

        BOOTSTRAP_STORE.update(mutate)

    def _store_restore_preview(self, preview: Dict[str, Any]) -> None:
        def mutate(state: Dict[str, Any]) -> Dict[str, Any]:
            state.setdefault("restore_previews", [])
            state["restore_previews"].append(preview)
            state["restore_previews"] = state["restore_previews"][-100:]
            return state

        BOOTSTRAP_STORE.update(mutate)

    def latest(self) -> Dict[str, Any]:
        state = BOOTSTRAP_STORE.load()
        plans = state.get("bootstrap_plans") or []
        backups = state.get("backup_runs") or []
        previews = state.get("restore_previews") or []
        return {
            "ok": True,
            "mode": "local_bootstrap_backup_latest",
            "latest_plan": plans[-1] if plans else None,
            "latest_backup": backups[-1] if backups else None,
            "latest_restore_preview": previews[-1] if previews else None,
            "plan_count": len(plans),
            "backup_count": len(backups),
            "restore_preview_count": len(previews),
        }

    def panel(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "mode": "local_bootstrap_backup_panel",
            "headline": "Instalar/configurar ferramentas e criar backup portátil",
            "status": self.get_status(),
            "latest": self.latest(),
            "safe_buttons": [
                {"id": "bootstrap_plan", "label": "Plano instalação", "endpoint": "/api/local-bootstrap-backup/plan", "priority": "critical"},
                {"id": "install_script", "label": "Gerar script", "endpoint": "/api/local-bootstrap-backup/install-script", "priority": "critical"},
                {"id": "backup", "label": "Criar backup", "endpoint": "/api/local-bootstrap-backup/create-backup", "priority": "critical"},
                {"id": "latest", "label": "Último estado", "endpoint": "/api/local-bootstrap-backup/latest", "priority": "high"},
            ],
        }

    def get_status(self) -> Dict[str, Any]:
        latest = self.latest()
        return {
            "ok": True,
            "mode": "local_bootstrap_backup_status",
            "plan_count": latest.get("plan_count", 0),
            "backup_count": latest.get("backup_count", 0),
            "restore_preview_count": latest.get("restore_preview_count", 0),
            "install_requires_operator_run": True,
            "backup_excludes_sensitive_material": True,
        }

    def get_package(self) -> Dict[str, Any]:
        return {"ok": True, "mode": "local_bootstrap_backup_package", "package": {"status": self.get_status(), "panel": self.panel(), "requirements": self.requirements()}}


local_bootstrap_backup_service = LocalBootstrapBackupService()
