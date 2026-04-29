from __future__ import annotations

import os
import re
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import uuid4

from app.services.local_tool_capability_scan_service import local_tool_capability_scan_service
from app.utils.atomic_json_store import AtomicJsonStore

DATA_DIR = Path("data")
CLEANUP_FILE = DATA_DIR / "local_cleanup_optimizer.json"
GENERATED_SCRIPTS_DIR = DATA_DIR / "generated_scripts"
CLEANUP_STORE = AtomicJsonStore(
    CLEANUP_FILE,
    default_factory=lambda: {
        "version": 1,
        "policy": "safe_local_cleanup_with_allowlist_restore_points_and_exact_targets",
        "scans": [],
        "plans": [],
        "scripts": [],
        "runs": [],
    },
)


class LocalCleanupOptimizerService:
    """Safe local cleanup optimizer for weak/old and new PCs.

    The optimizer can remove exact, allowlisted development artifacts such as
    unwanted Ollama models. Windows/system changes are planned and scripted with
    restore point guidance; critical services are never disabled by this layer.
    """

    DEFAULT_KEEP_OLLAMA_MODELS = ["gemma2:2b", "qwen2.5:7b"]
    APPROVAL_PHRASE = "OPTIMIZE LOCAL PC"

    NEVER_DISABLE_WINDOWS_ITEMS = [
        "Windows Update",
        "Windows Defender / Security Center",
        "Firewall",
        "Network adapters/services",
        "BitLocker/encryption",
        "Windows Installer",
        "User profile/authentication",
        "Device drivers",
        "Backup/restore services",
        "Remote access needed by operator",
    ]

    WINDOWS_NUISANCE_CANDIDATES = [
        {
            "id": "startup_apps_review",
            "label": "Apps de arranque desnecessárias",
            "risk": "medium",
            "strategy": "rever e desativar apenas itens não críticos no Startup Apps",
            "auto_apply": False,
        },
        {
            "id": "gaming_overlay_review",
            "label": "Overlays/jogo/barra Xbox se não forem usados",
            "risk": "low",
            "strategy": "desativar apenas se não fizer falta ao operador",
            "auto_apply": False,
        },
        {
            "id": "indexing_scope_review",
            "label": "Indexação excessiva em PC fraco",
            "risk": "medium",
            "strategy": "reduzir escopo em vez de desligar serviços críticos",
            "auto_apply": False,
        },
        {
            "id": "background_sync_review",
            "label": "Sincronizações pesadas não usadas",
            "risk": "medium",
            "strategy": "desativar arranque automático de apps de sync não usadas",
            "auto_apply": False,
        },
    ]

    SAFE_CACHE_TARGETS = [
        {
            "id": "godmode_generated_scripts",
            "path": "data/generated_scripts",
            "label": "Scripts gerados antigos do God Mode",
            "auto_apply": False,
        },
        {
            "id": "godmode_restore_previews",
            "path": "data/restore",
            "label": "Previews/artefactos antigos de restore",
            "auto_apply": False,
        },
    ]

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def policy(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "mode": "local_cleanup_policy",
            "auto_cleanup_allowed": True,
            "auto_cleanup_scope": [
                "modelos Ollama exatos fora da keeplist e marcados como remover",
                "caches/artefactos locais allowlisted quando configurado",
            ],
            "requires_approval_or_script_review": [
                "alterações Windows",
                "desinstalar programas completos",
                "desativar startup/system settings",
                "limpeza com risco de perder trabalho",
            ],
            "never_disable": self.NEVER_DISABLE_WINDOWS_ITEMS,
            "approval_phrase": self.APPROVAL_PHRASE,
            "default_keep_ollama_models": self.DEFAULT_KEEP_OLLAMA_MODELS,
        }

    def scan(self) -> Dict[str, Any]:
        tool_status = local_tool_capability_scan_service.get_status()
        ollama = self._scan_ollama_models()
        windows = self._windows_candidates()
        caches = self._cache_candidates()
        scan = {
            "scan_id": f"local-cleanup-scan-{uuid4().hex[:12]}",
            "created_at": self._now(),
            "tool_status": tool_status,
            "ollama": ollama,
            "windows_candidates": windows,
            "cache_candidates": caches,
            "policy": self.policy(),
            "read_only": True,
        }
        self._store("scans", scan)
        return {"ok": True, "mode": "local_cleanup_scan", "scan": scan}

    def _scan_ollama_models(self) -> Dict[str, Any]:
        ollama_path = shutil.which("ollama")
        if not ollama_path:
            return {"available": False, "models": [], "note": "ollama_not_found"}
        try:
            completed = subprocess.run(
                [ollama_path, "list"],
                capture_output=True,
                text=True,
                timeout=15,
                check=False,
            )
        except Exception as exc:
            return {"available": True, "models": [], "error": exc.__class__.__name__, "detail": str(exc)[:300]}
        models = self._parse_ollama_list(completed.stdout or "")
        return {
            "available": True,
            "command": "ollama list",
            "returncode": completed.returncode,
            "models": models,
            "raw_line_count": len((completed.stdout or "").splitlines()),
        }

    def _parse_ollama_list(self, output: str) -> List[Dict[str, Any]]:
        models: List[Dict[str, Any]] = []
        for line in output.splitlines():
            stripped = line.strip()
            if not stripped or stripped.lower().startswith("name"):
                continue
            parts = re.split(r"\s{2,}|\t+", stripped)
            name = parts[0].strip() if parts else stripped.split()[0]
            if not name or ":" not in name:
                continue
            models.append({
                "name": name,
                "id": parts[1].strip() if len(parts) > 1 else None,
                "size": parts[2].strip() if len(parts) > 2 else None,
                "modified": parts[3].strip() if len(parts) > 3 else None,
            })
        return models

    def _windows_candidates(self) -> Dict[str, Any]:
        return {
            "platform": os.name,
            "safe_to_apply_automatically": False,
            "candidates": self.WINDOWS_NUISANCE_CANDIDATES,
            "never_disable": self.NEVER_DISABLE_WINDOWS_ITEMS,
            "strategy": "gerar plano/script com restore point; não mexer em serviços críticos",
        }

    def _cache_candidates(self) -> List[Dict[str, Any]]:
        candidates = []
        for item in self.SAFE_CACHE_TARGETS:
            path = Path(item["path"])
            candidates.append({
                **item,
                "exists": path.exists(),
                "file_count": self._count_files(path) if path.exists() else 0,
                "estimated_size_bytes": self._estimate_size(path) if path.exists() else 0,
            })
        return candidates

    def _count_files(self, path: Path) -> int:
        try:
            if path.is_file():
                return 1
            return sum(1 for item in path.rglob("*") if item.is_file())
        except Exception:
            return 0

    def _estimate_size(self, path: Path) -> int:
        try:
            if path.is_file():
                return path.stat().st_size
            return sum(item.stat().st_size for item in path.rglob("*") if item.is_file())
        except Exception:
            return 0

    def plan(
        self,
        keep_ollama_models: Optional[List[str]] = None,
        broken_ollama_models: Optional[List[str]] = None,
        allow_auto_ollama_remove: bool = True,
        allow_windows_tuning_script: bool = True,
    ) -> Dict[str, Any]:
        scan = self.scan().get("scan", {})
        keep = [item.strip() for item in (keep_ollama_models or self.DEFAULT_KEEP_OLLAMA_MODELS) if item.strip()]
        broken = [item.strip() for item in (broken_ollama_models or []) if item.strip()]
        actions: List[Dict[str, Any]] = []
        for model in scan.get("ollama", {}).get("models", []):
            name = model.get("name")
            if not name:
                continue
            if name in keep:
                actions.append(self._action("keep_ollama_model", name, "keep_model_confirmed_useful", auto=False, model=model))
            elif name in broken:
                actions.append(self._action("remove_ollama_model", name, "operator_or_scan_marked_broken", auto=allow_auto_ollama_remove, model=model))
            else:
                actions.append(self._action("review_ollama_model", name, "not_in_keeplist_but_not_marked_broken", auto=False, model=model))
        if allow_windows_tuning_script:
            actions.append({
                "action_id": f"windows-tuning-review-{uuid4().hex[:8]}",
                "kind": "windows_tuning_review_script",
                "target": "windows_nuisance_candidates",
                "reason": "possible_performance_gain_but_requires_review",
                "auto_apply_allowed": False,
                "requires_approval_phrase": self.APPROVAL_PHRASE,
            })
        plan = {
            "plan_id": f"local-cleanup-plan-{uuid4().hex[:12]}",
            "created_at": self._now(),
            "scan_id": scan.get("scan_id"),
            "keep_ollama_models": keep,
            "broken_ollama_models": broken,
            "actions": actions,
            "auto_action_count": len([a for a in actions if a.get("auto_apply_allowed")]),
            "review_action_count": len([a for a in actions if not a.get("auto_apply_allowed")]),
            "script_preview": self._powershell_script(actions, preview=True),
            "policy": self.policy(),
        }
        self._store("plans", plan)
        return {"ok": True, "mode": "local_cleanup_plan", "plan": plan}

    def _action(self, kind: str, target: str, reason: str, auto: bool, model: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return {
            "action_id": f"cleanup-action-{uuid4().hex[:10]}",
            "kind": kind,
            "target": target,
            "reason": reason,
            "auto_apply_allowed": auto,
            "model": model,
            "risk": "low" if kind in {"keep_ollama_model", "remove_ollama_model"} else "medium",
        }

    def generate_script(self, plan_id: Optional[str] = None) -> Dict[str, Any]:
        plan = self._find_plan(plan_id)
        if not plan:
            plan = self.plan().get("plan", {})
        script = self._powershell_script(plan.get("actions", []), preview=False)
        GENERATED_SCRIPTS_DIR.mkdir(parents=True, exist_ok=True)
        path = GENERATED_SCRIPTS_DIR / "godmode_local_cleanup_optimizer.ps1"
        path.write_text(script, encoding="utf-8")
        result = {
            "script_id": f"cleanup-script-{uuid4().hex[:12]}",
            "created_at": self._now(),
            "plan_id": plan.get("plan_id"),
            "script_path": str(path),
            "approval_phrase": self.APPROVAL_PHRASE,
            "operator_review_recommended": True,
        }
        self._store("scripts", result)
        return {"ok": True, "mode": "local_cleanup_script", "script": result}

    def _powershell_script(self, actions: List[Dict[str, Any]], preview: bool) -> str:
        lines = [
            "$ErrorActionPreference = 'Continue'",
            "Write-Host 'God Mode Local Cleanup Optimizer'",
            "Write-Host 'Exact allowlisted cleanup only. Critical Windows services are not disabled.'",
            "",
            "function Remove-OllamaModel($Name) {",
            "  if (-not (Get-Command ollama -ErrorAction SilentlyContinue)) { Write-Host 'Ollama not found'; return }",
            "  Write-Host \"Removing Ollama model: $Name\"",
            "  ollama rm $Name",
            "}",
            "",
        ]
        for action in actions:
            if action.get("kind") == "remove_ollama_model":
                cmd = f"Remove-OllamaModel -Name '{action.get('target')}'"
                lines.append(f"# {cmd}" if preview else cmd)
            elif action.get("kind") == "keep_ollama_model":
                lines.append(f"Write-Host 'Keeping Ollama model: {action.get('target')}'")
            elif action.get("kind") == "review_ollama_model":
                lines.append(f"Write-Host 'Review Ollama model before removal: {action.get('target')}'")
            elif action.get("kind") == "windows_tuning_review_script":
                lines.extend([
                    "",
                    "Write-Host 'Windows tuning candidates require manual review.'",
                    "Write-Host 'Do not disable security, update, firewall, networking, drivers, installer or backup services.'",
                    "Write-Host 'Recommended: create a Windows restore point before changing startup/settings.'",
                ])
        lines.append("Write-Host 'Cleanup script finished.'")
        return "\n".join(lines) + "\n"

    def apply_safe_cleanup(self, plan_id: Optional[str] = None, approval_phrase: str = "") -> Dict[str, Any]:
        plan = self._find_plan(plan_id)
        if not plan:
            return {"ok": False, "mode": "local_cleanup_apply", "error": "plan_not_found"}
        if approval_phrase != self.APPROVAL_PHRASE:
            return {"ok": False, "mode": "local_cleanup_apply", "error": "approval_phrase_required", "required_phrase": self.APPROVAL_PHRASE}
        results = []
        for action in plan.get("actions", []):
            if not action.get("auto_apply_allowed"):
                continue
            if action.get("kind") == "remove_ollama_model":
                results.append(self._apply_ollama_remove(action.get("target")))
        run = {
            "run_id": f"local-cleanup-run-{uuid4().hex[:12]}",
            "created_at": self._now(),
            "plan_id": plan.get("plan_id"),
            "result_count": len(results),
            "results": results,
            "ok": all(item.get("ok") for item in results) if results else True,
        }
        self._store("runs", run)
        return {"ok": run["ok"], "mode": "local_cleanup_apply", "run": run}

    def _apply_ollama_remove(self, model_name: str) -> Dict[str, Any]:
        if not model_name or any(ch in model_name for ch in [";", "&", "|", "`", "$", "\\", "/"]):
            return {"ok": False, "target": model_name, "error": "unsafe_model_name"}
        ollama_path = shutil.which("ollama")
        if not ollama_path:
            return {"ok": False, "target": model_name, "error": "ollama_not_found"}
        try:
            completed = subprocess.run([ollama_path, "rm", model_name], capture_output=True, text=True, timeout=120, check=False)
            return {
                "ok": completed.returncode == 0,
                "target": model_name,
                "returncode": completed.returncode,
                "stdout": (completed.stdout or "")[-1000:],
                "stderr": (completed.stderr or "")[-1000:],
            }
        except Exception as exc:
            return {"ok": False, "target": model_name, "error": exc.__class__.__name__, "detail": str(exc)[:300]}

    def _find_plan(self, plan_id: Optional[str]) -> Optional[Dict[str, Any]]:
        plans = CLEANUP_STORE.load().get("plans", [])
        if plan_id:
            return next((plan for plan in plans if plan.get("plan_id") == plan_id), None)
        return plans[-1] if plans else None

    def _store(self, key: str, value: Dict[str, Any]) -> None:
        def mutate(state: Dict[str, Any]) -> Dict[str, Any]:
            state.setdefault(key, [])
            state[key].append(value)
            state[key] = state[key][-100:]
            return state

        CLEANUP_STORE.update(mutate)

    def latest(self) -> Dict[str, Any]:
        state = CLEANUP_STORE.load()
        return {
            "ok": True,
            "mode": "local_cleanup_latest",
            "latest_scan": (state.get("scans") or [None])[-1],
            "latest_plan": (state.get("plans") or [None])[-1],
            "latest_script": (state.get("scripts") or [None])[-1],
            "latest_run": (state.get("runs") or [None])[-1],
            "scan_count": len(state.get("scans") or []),
            "plan_count": len(state.get("plans") or []),
            "run_count": len(state.get("runs") or []),
        }

    def panel(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "mode": "local_cleanup_panel",
            "headline": "Limpar PC sem partir o Windows",
            "policy": self.policy(),
            "latest": self.latest(),
            "safe_buttons": [
                {"id": "scan", "label": "Scan limpeza", "endpoint": "/api/local-cleanup/scan", "priority": "critical"},
                {"id": "plan", "label": "Plano limpeza", "endpoint": "/api/local-cleanup/plan", "priority": "critical"},
                {"id": "script", "label": "Gerar script", "endpoint": "/api/local-cleanup/script", "priority": "high"},
                {"id": "apply", "label": "Aplicar seguro", "endpoint": "/api/local-cleanup/apply-safe", "priority": "high"},
            ],
        }

    def get_status(self) -> Dict[str, Any]:
        latest = self.latest()
        return {
            "ok": True,
            "mode": "local_cleanup_status",
            "scan_count": latest.get("scan_count", 0),
            "plan_count": latest.get("plan_count", 0),
            "run_count": latest.get("run_count", 0),
            "auto_cleanup_allowed": True,
            "windows_critical_protection": True,
        }

    def get_package(self) -> Dict[str, Any]:
        return {"ok": True, "mode": "local_cleanup_package", "package": {"status": self.get_status(), "panel": self.panel(), "latest": self.latest()}}


local_cleanup_optimizer_service = LocalCleanupOptimizerService()
