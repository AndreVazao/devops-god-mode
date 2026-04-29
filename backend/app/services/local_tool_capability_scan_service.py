from __future__ import annotations

import os
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import uuid4

from app.services.local_pc_runtime_orchestrator_service import local_pc_runtime_orchestrator_service
from app.utils.atomic_json_store import AtomicJsonStore

DATA_DIR = Path("data")
SCAN_FILE = DATA_DIR / "local_tool_capability_scan.json"
SCAN_STORE = AtomicJsonStore(
    SCAN_FILE,
    default_factory=lambda: {
        "version": 1,
        "policy": "discover_local_tools_then_use_best_local_or_remote_path",
        "scans": [],
        "plans": [],
    },
)


class LocalToolCapabilityScanService:
    """First-run local tool inventory for the PC runtime.

    The scan is intentionally read-only. It detects installed/available tools,
    marks broken or partial capabilities, and recommends what God Mode can use
    locally before relying on browser/cloud flows.
    """

    TOOL_DEFINITIONS = [
        {
            "id": "obsidian",
            "label": "Obsidian",
            "kind": "memory",
            "commands": ["obsidian"],
            "windows_paths": [
                "%LOCALAPPDATA%/Obsidian/Obsidian.exe",
                "%PROGRAMFILES%/Obsidian/Obsidian.exe",
                "%PROGRAMFILES(X86)%/Obsidian/Obsidian.exe",
            ],
            "use_cases": ["project_memory", "context_vault", "resume_notes"],
        },
        {
            "id": "vscode",
            "label": "Visual Studio Code",
            "kind": "editor",
            "commands": ["code", "code.cmd"],
            "windows_paths": [
                "%LOCALAPPDATA%/Programs/Microsoft VS Code/Code.exe",
                "%PROGRAMFILES%/Microsoft VS Code/Code.exe",
            ],
            "use_cases": ["local_code_editing", "repo_inspection", "manual_operator_review"],
        },
        {
            "id": "git",
            "label": "Git",
            "kind": "vcs",
            "commands": ["git"],
            "windows_paths": [
                "%PROGRAMFILES%/Git/bin/git.exe",
                "%PROGRAMFILES%/Git/cmd/git.exe",
            ],
            "use_cases": ["clone_repo", "commit", "diff", "local_patch_flow"],
        },
        {
            "id": "python",
            "label": "Python",
            "kind": "runtime",
            "commands": ["python", "py", "python3"],
            "windows_paths": [],
            "use_cases": ["backend", "local_scripts", "validators", "packaging"],
        },
        {
            "id": "node",
            "label": "Node.js",
            "kind": "runtime",
            "commands": ["node", "npm", "npx"],
            "windows_paths": ["%PROGRAMFILES%/nodejs/node.exe"],
            "use_cases": ["frontend", "mobile_shell", "web_builds"],
        },
        {
            "id": "android_studio",
            "label": "Android Studio",
            "kind": "android",
            "commands": ["studio", "studio64"],
            "windows_paths": [
                "%PROGRAMFILES%/Android/Android Studio/bin/studio64.exe",
                "%LOCALAPPDATA%/Programs/Android Studio/bin/studio64.exe",
            ],
            "use_cases": ["android_project_review", "sdk_management", "manual_android_debug"],
        },
        {
            "id": "android_sdk",
            "label": "Android SDK",
            "kind": "android",
            "commands": ["adb", "sdkmanager", "avdmanager"],
            "windows_paths": [
                "%LOCALAPPDATA%/Android/Sdk/platform-tools/adb.exe",
                "%ANDROID_HOME%/platform-tools/adb.exe",
                "%ANDROID_SDK_ROOT%/platform-tools/adb.exe",
            ],
            "use_cases": ["apk_install", "phone_pairing", "android_debug"],
        },
        {
            "id": "powershell",
            "label": "PowerShell",
            "kind": "shell",
            "commands": ["powershell", "pwsh"],
            "windows_paths": [],
            "use_cases": ["windows_bootstrap", "shortcut_setup", "local_tasks"],
        },
        {
            "id": "chrome_edge",
            "label": "Browser",
            "kind": "browser",
            "commands": ["chrome", "msedge", "google-chrome"],
            "windows_paths": [
                "%PROGRAMFILES%/Google/Chrome/Application/chrome.exe",
                "%PROGRAMFILES(X86)%/Google/Chrome/Application/chrome.exe",
                "%PROGRAMFILES%/Microsoft/Edge/Application/msedge.exe",
                "%PROGRAMFILES(X86)%/Microsoft/Edge/Application/msedge.exe",
            ],
            "use_cases": ["provider_web_sessions", "manual_login", "docs_review"],
        },
        {
            "id": "codex_cli",
            "label": "Codex CLI",
            "kind": "ai_cli",
            "commands": ["codex"],
            "windows_paths": [],
            "use_cases": ["local_code_assistance", "repo_patch_suggestions"],
        },
        {
            "id": "claude_cli",
            "label": "Claude CLI",
            "kind": "ai_cli",
            "commands": ["claude"],
            "windows_paths": [],
            "use_cases": ["local_ai_handoff", "large_context_review"],
        },
        {
            "id": "ollama",
            "label": "Ollama / Local LLM",
            "kind": "local_ai",
            "commands": ["ollama"],
            "windows_paths": ["%LOCALAPPDATA%/Programs/Ollama/ollama.exe"],
            "use_cases": ["offline_summary", "local_private_drafts", "basic_code_help"],
        },
    ]

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def _expand_path(self, raw: str) -> str:
        return os.path.expandvars(raw.replace("/", os.sep))

    def _command_found(self, command: str) -> Optional[str]:
        found = shutil.which(command)
        return found

    def _path_found(self, raw_path: str) -> Optional[str]:
        path = self._expand_path(raw_path)
        return path if path and Path(path).exists() else None

    def _detect_tool(self, definition: Dict[str, Any]) -> Dict[str, Any]:
        command_hits = [hit for command in definition.get("commands", []) if (hit := self._command_found(command))]
        path_hits = [hit for raw in definition.get("windows_paths", []) if (hit := self._path_found(raw))]
        status = "available" if command_hits or path_hits else "not_found"
        if definition["id"] == "android_studio" and status == "available" and not self._detect_by_id("android_sdk")["available"]:
            status = "partial_or_broken"
        return {
            "tool_id": definition["id"],
            "label": definition["label"],
            "kind": definition["kind"],
            "available": status == "available",
            "status": status,
            "command_hits": command_hits,
            "path_hits": path_hits,
            "use_cases": definition.get("use_cases", []),
            "notes": self._notes_for(definition["id"], status),
        }

    def _detect_by_id(self, tool_id: str) -> Dict[str, Any]:
        definition = next((item for item in self.TOOL_DEFINITIONS if item["id"] == tool_id), None)
        if not definition:
            return {"available": False, "status": "unknown_tool"}
        command_hits = [hit for command in definition.get("commands", []) if (hit := self._command_found(command))]
        path_hits = [hit for raw in definition.get("windows_paths", []) if (hit := self._path_found(raw))]
        return {"available": bool(command_hits or path_hits), "status": "available" if command_hits or path_hits else "not_found"}

    def _notes_for(self, tool_id: str, status: str) -> List[str]:
        notes: List[str] = []
        if tool_id == "android_studio" and status == "partial_or_broken":
            notes.append("Android Studio encontrado, mas SDK/ADB parecem indisponíveis; usar apenas como referência/manual se abrir.")
        if tool_id == "ollama" and status == "available":
            notes.append("Pode ajudar em resumos e rascunhos locais; qualidade depende do modelo instalado.")
        if tool_id in {"codex_cli", "claude_cli"} and status == "available":
            notes.append("Usar como apoio local/controlado, preservando memória e aprovação antes de alterações reais.")
        return notes

    def scan(self) -> Dict[str, Any]:
        scan_id = f"local-tool-scan-{uuid4().hex[:12]}"
        tools = [self._detect_tool(definition) for definition in self.TOOL_DEFINITIONS]
        runtime = local_pc_runtime_orchestrator_service.get_runtime_state()
        plan = self._build_usage_plan(tools)
        scan = {
            "scan_id": scan_id,
            "created_at": self._now(),
            "mode": "local_tool_capability_scan",
            "platform_hint": os.name,
            "tools": tools,
            "available_count": len([tool for tool in tools if tool.get("available")]),
            "partial_count": len([tool for tool in tools if tool.get("status") == "partial_or_broken"]),
            "runtime_state": runtime,
            "usage_plan": plan,
            "read_only": True,
            "operator_next": self._operator_next(plan),
        }
        self._store_scan(scan)
        return {"ok": True, "mode": "local_tool_capability_scan_result", "scan": scan}

    def _build_usage_plan(self, tools: List[Dict[str, Any]]) -> Dict[str, Any]:
        by_id = {tool["tool_id"]: tool for tool in tools}
        available = lambda tool_id: by_id.get(tool_id, {}).get("available", False)
        partial = lambda tool_id: by_id.get(tool_id, {}).get("status") == "partial_or_broken"
        lanes: List[Dict[str, Any]] = []
        lanes.append({
            "lane_id": "memory_lane",
            "label": "Memória e contexto",
            "status": "ready" if available("obsidian") else "file_memory_only",
            "tools": ["obsidian"] if available("obsidian") else ["andreos_files"],
            "strategy": "Usar AndreOS/Obsidian quando disponível; caso contrário manter ficheiros markdown locais.",
        })
        lanes.append({
            "lane_id": "local_code_lane",
            "label": "Edição e preparação local de código",
            "status": "ready" if available("vscode") and available("git") and available("python") else "partial",
            "tools": [tool for tool in ["vscode", "git", "python", "node"] if available(tool)],
            "strategy": "Preparar patches, diffs e validações localmente antes de upload/PR.",
        })
        lanes.append({
            "lane_id": "android_lane",
            "label": "Android/APK",
            "status": "ready" if available("android_sdk") else ("manual_only" if partial("android_studio") or available("android_studio") else "github_actions_preferred"),
            "tools": [tool for tool in ["android_studio", "android_sdk"] if by_id.get(tool, {}).get("status") != "not_found"],
            "strategy": "Usar SDK/ADB local se disponível; se Android Studio estiver quebrado, preferir GitHub Actions para builds.",
        })
        lanes.append({
            "lane_id": "provider_lane",
            "label": "Providers e IA local",
            "status": "ready" if any(available(tool) for tool in ["codex_cli", "claude_cli", "ollama", "chrome_edge"]) else "browser_or_cloud_only",
            "tools": [tool for tool in ["codex_cli", "claude_cli", "ollama", "chrome_edge"] if available(tool)],
            "strategy": "Usar ferramentas locais como apoio quando existirem; manter ChatGPT como principal e preservar contexto AndreOS.",
        })
        lanes.append({
            "lane_id": "windows_lane",
            "label": "Automação Windows",
            "status": "ready" if available("powershell") else "limited",
            "tools": ["powershell"] if available("powershell") else [],
            "strategy": "Usar scripts Windows para atalhos, arranque local e tarefas aprovadas.",
        })
        return {
            "lanes": lanes,
            "recommended_default": self._recommended_default(lanes),
            "do_not_force_broken_tools": True,
            "prefer_local_when_reliable": True,
            "fallback_to_github_actions_for_builds": True,
        }

    def _recommended_default(self, lanes: List[Dict[str, Any]]) -> Dict[str, Any]:
        android = next((lane for lane in lanes if lane["lane_id"] == "android_lane"), {})
        code = next((lane for lane in lanes if lane["lane_id"] == "local_code_lane"), {})
        return {
            "code_work": "local_patch_then_github_pr" if code.get("status") in {"ready", "partial"} else "github_only",
            "android_build": "local_sdk" if android.get("status") == "ready" else "github_actions",
            "memory": "obsidian_or_markdown",
            "providers": "chatgpt_primary_with_local_support_when_available",
        }

    def _operator_next(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "label": "Abrir plano de uso local",
            "endpoint": "/api/local-tool-capability/plan",
            "route": "/app/home",
            "priority": "high",
        }

    def _store_scan(self, scan: Dict[str, Any]) -> None:
        def mutate(state: Dict[str, Any]) -> Dict[str, Any]:
            state.setdefault("version", 1)
            state.setdefault("policy", "discover_local_tools_then_use_best_local_or_remote_path")
            state.setdefault("scans", [])
            state.setdefault("plans", [])
            state["scans"].append(scan)
            state["plans"].append(scan.get("usage_plan", {}))
            state["scans"] = state["scans"][-100:]
            state["plans"] = state["plans"][-100:]
            return state

        SCAN_STORE.update(mutate)

    def latest(self) -> Dict[str, Any]:
        state = SCAN_STORE.load()
        scans = state.get("scans") or []
        plans = state.get("plans") or []
        return {
            "ok": True,
            "mode": "local_tool_capability_latest",
            "latest_scan": scans[-1] if scans else None,
            "latest_plan": plans[-1] if plans else None,
            "scan_count": len(scans),
        }

    def plan(self) -> Dict[str, Any]:
        latest = self.latest()
        if not latest.get("latest_plan"):
            return self.scan()
        return {"ok": True, "mode": "local_tool_capability_plan", "plan": latest.get("latest_plan"), "latest_scan": latest.get("latest_scan")}

    def panel(self) -> Dict[str, Any]:
        latest = self.latest()
        scan = latest.get("latest_scan") or {}
        return {
            "ok": True,
            "mode": "local_tool_capability_panel",
            "headline": "Ferramentas locais do PC",
            "summary": {
                "available_count": scan.get("available_count", 0),
                "partial_count": scan.get("partial_count", 0),
                "scan_count": latest.get("scan_count", 0),
            },
            "latest": latest,
            "safe_buttons": [
                {"id": "scan", "label": "Fazer check-up PC", "endpoint": "/api/local-tool-capability/scan", "priority": "critical"},
                {"id": "plan", "label": "Plano local", "endpoint": "/api/local-tool-capability/plan", "priority": "critical"},
                {"id": "latest", "label": "Último scan", "endpoint": "/api/local-tool-capability/latest", "priority": "high"},
            ],
        }

    def get_status(self) -> Dict[str, Any]:
        latest = self.latest()
        scan = latest.get("latest_scan") or {}
        return {
            "ok": True,
            "mode": "local_tool_capability_status",
            "status": "scan_ready" if scan else "not_scanned_yet",
            "available_count": scan.get("available_count", 0),
            "partial_count": scan.get("partial_count", 0),
            "scan_count": latest.get("scan_count", 0),
            "read_only": True,
        }

    def get_package(self) -> Dict[str, Any]:
        return {"ok": True, "mode": "local_tool_capability_package", "package": {"status": self.get_status(), "panel": self.panel(), "plan": self.plan()}}


local_tool_capability_scan_service = LocalToolCapabilityScanService()
