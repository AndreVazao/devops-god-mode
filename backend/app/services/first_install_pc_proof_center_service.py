from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List

from app.services.download_install_center_v2_service import download_install_center_v2_service
from app.services.first_release_artifact_center_service import first_release_artifact_center_service
from app.services.god_mode_reality_audit_service import god_mode_reality_audit_service
from app.services.module_registry_snapshot_service import module_registry_snapshot_service
from app.services.pc_provider_conversation_proof_service import pc_provider_conversation_proof_service
from app.services.project_tree_autorefresh_service import project_tree_autorefresh_service

REPO_URL = "https://github.com/AndreVazao/devops-god-mode"
ACTIONS_URL = f"{REPO_URL}/actions"
WINDOWS_WORKFLOW_URL = f"{REPO_URL}/actions/workflows/windows-exe-real-build.yml"
ANDROID_WORKFLOW_URL = f"{REPO_URL}/actions/workflows/android-real-build-progressive.yml"


class FirstInstallPcProofCenterService:
    """Mobile/PC cockpit package for the first real installation.

    This is not another artifact builder. It aggregates existing real services
    into one operator-facing checklist for the first PC proof run.
    """

    SERVICE_ID = "first_install_pc_proof_center"
    VERSION = "phase_181_v1"

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def status(self) -> Dict[str, Any]:
        package = self.package(include_verbose=False)
        checklist = package["checklist"]
        done = sum(1 for item in checklist if item["status"] == "ready")
        total = len(checklist)
        return {
            "ok": True,
            "service": self.SERVICE_ID,
            "version": self.VERSION,
            "generated_at": self._now(),
            "ready_items": done,
            "total_items": total,
            "readiness_percent": round(done * 100 / max(total, 1)),
            "primary_route": "/api/first-install-pc-proof-center/package",
            "actions_url": ACTIONS_URL,
        }

    def artifact_links(self) -> Dict[str, Any]:
        artifact_report = first_release_artifact_center_service.build_artifact_report()
        return {
            "ok": True,
            "mode": "first_install_artifact_links",
            "actions_url": ACTIONS_URL,
            "windows_workflow_url": WINDOWS_WORKFLOW_URL,
            "android_workflow_url": ANDROID_WORKFLOW_URL,
            "artifact_center": artifact_report,
            "operator_download_steps": [
                {
                    "id": "windows_exe",
                    "label": "Descarregar God Mode Windows EXE",
                    "url": WINDOWS_WORKFLOW_URL,
                    "instruction": "Abrir o último run verde → Artifacts → descarregar godmode-windows-exe.",
                    "expected_artifact": "godmode-windows-exe",
                },
                {
                    "id": "android_apk",
                    "label": "Descarregar God Mode Android APK",
                    "url": ANDROID_WORKFLOW_URL,
                    "instruction": "Abrir o último run verde → Artifacts → descarregar godmode-android-webview-apk.",
                    "expected_artifact": "godmode-android-webview-apk",
                },
            ],
        }

    def pc_proof_commands(self) -> Dict[str, Any]:
        providers = ["chatgpt", "gemini", "claude", "perplexity"]
        commands = [pc_provider_conversation_proof_service.provider_proof_command(provider=provider, wait_login_seconds=90) for provider in providers]
        return {
            "ok": True,
            "mode": "first_install_pc_proof_commands",
            "commands": commands,
            "install_plan": pc_provider_conversation_proof_service.install_plan(),
            "proofs": pc_provider_conversation_proof_service.list_proofs(limit=20),
            "proof_package": pc_provider_conversation_proof_service.first_pc_proof_package(),
        }

    def checklist(self) -> List[Dict[str, Any]]:
        reality = god_mode_reality_audit_service.status()
        tree = project_tree_autorefresh_service.get_status()
        registry = module_registry_snapshot_service.status()
        proof_status = pc_provider_conversation_proof_service.status()
        download_status = download_install_center_v2_service.get_status()
        checks = [
            self._check(
                "backend_builds_validated",
                "Builds e backend validados em CI",
                "ready" if reality.get("ok") else "needs_attention",
                "Universal/Android/Windows já passam no pipeline GitHub.",
                endpoint="/api/god-mode-reality-audit/status",
            ),
            self._check(
                "download_artifacts",
                "Descarregar EXE/APK dos artifacts",
                "ready",
                "Usar links de workflows no painel para baixar os últimos runs verdes.",
                endpoint="/api/first-install-pc-proof-center/artifacts",
            ),
            self._check(
                "open_pc_home",
                "Abrir /app/home no PC",
                "operator_action_required",
                "Depois do EXE iniciar, abrir http://127.0.0.1:8000/app/home ou IP LAN do PC.",
                endpoint="/app/home",
            ),
            self._check(
                "phone_cockpit_lan",
                "Abrir cockpit no telemóvel via IP LAN do PC",
                "operator_action_required",
                "No telemóvel, abrir o IP do PC na mesma rede ou túnel privado quando existir.",
                endpoint="/api/cockpit-runtime-ux/package",
            ),
            self._check(
                "tree_official",
                "Confirmar GOD_MODE_TREE.md",
                "ready" if tree.get("ok") else "needs_attention",
                "Tree oficial é docs/project-tree/GOD_MODE_TREE.md; manual fica só fallback.",
                endpoint="/api/project-tree-autorefresh/package",
            ),
            self._check(
                "module_registry",
                "Confirmar registry de módulos",
                "ready" if registry.get("ok") else "needs_attention",
                f"Routes: {registry.get('route_module_count')}; services: {registry.get('service_module_count')}.",
                endpoint="/api/module-registry-snapshot/package",
            ),
            self._check(
                "playwright_install",
                "Instalar/validar Playwright no PC se quiser browser real",
                "operator_action_required" if proof_status.get("browser_worker_status") == "playwright_not_installed" else "ready",
                "Comando: python -m pip install playwright && python -m playwright install chromium.",
                endpoint="/api/pc-provider-conversation-proof/install-plan",
            ),
            self._check(
                "provider_manual_login",
                "Fazer login manual nos providers escolhidos",
                "operator_action_required",
                "Abrir provider pelo probe, fazer login manual e nunca colar credenciais nos logs/chat.",
                endpoint="/api/pc-provider-conversation-proof/command",
            ),
            self._check(
                "import_provider_proof",
                "Importar proof JSON para inventário multi-IA",
                "ready" if proof_status.get("proof_count", 0) > 0 else "operator_action_required",
                "Depois do probe gerar JSON em data/provider_proofs, importar latest proof.",
                endpoint="/api/pc-provider-conversation-proof/import-latest",
            ),
            self._check(
                "first_low_risk_action",
                "Executar primeira ação low-risk aprovada",
                "operator_action_required",
                "Só depois de cockpit + tree + proof/inventário estarem OK.",
                endpoint="/api/github-approved-actions/package",
            ),
        ]
        if download_status.get("ok") is not True:
            checks.append(self._check("download_center_attention", "Download center precisa atenção", "needs_attention", "DownloadInstallCenterV2 não respondeu OK.", endpoint="/api/download-install-center-v2/package"))
        return checks

    def operator_cards(self) -> List[Dict[str, Any]]:
        return [
            {
                "id": "download_windows",
                "title": "1. Baixar EXE Windows",
                "kind": "external_link",
                "url": WINDOWS_WORKFLOW_URL,
                "priority": "critical",
                "description": "Último run verde → artifact godmode-windows-exe.",
            },
            {
                "id": "download_android",
                "title": "2. Baixar APK Android",
                "kind": "external_link",
                "url": ANDROID_WORKFLOW_URL,
                "priority": "high",
                "description": "Último run verde → artifact godmode-android-webview-apk.",
            },
            {
                "id": "open_home",
                "title": "3. Abrir cockpit PC",
                "kind": "route",
                "route": "/app/home",
                "priority": "critical",
                "description": "Rota visual canónica do God Mode.",
            },
            {
                "id": "pc_provider_proof",
                "title": "4. Provar conversas IA no PC",
                "kind": "endpoint",
                "endpoint": "/api/pc-provider-conversation-proof/package",
                "priority": "critical",
                "description": "Gera comandos por provider e importa proof JSON para o inventário.",
            },
            {
                "id": "reality_audit",
                "title": "5. Ver poder real vs parcial",
                "kind": "endpoint",
                "endpoint": "/api/god-mode-reality-audit/package",
                "priority": "high",
                "description": "Mostra o que é real, parcial, planeado ou bloqueado.",
            },
        ]

    def package(self, include_verbose: bool = True) -> Dict[str, Any]:
        result = {
            "ok": True,
            "service": self.SERVICE_ID,
            "version": self.VERSION,
            "generated_at": self._now(),
            "mission": {
                "id": "first_real_install_pc_provider_proof",
                "title": "Primeira instalação real no PC + prova de conversas IA",
                "goal": "Instalar, abrir cockpit, validar tree/registry, provar provider browser real e importar primeira conversa/proof.",
                "tomorrow_success_definition": [
                    "PC abre /app/home",
                    "telemóvel consegue ver cockpit via PC/LAN ou browser local",
                    "GOD_MODE_TREE.md e module registry respondem",
                    "pelo menos um provider abre com login manual",
                    "proof JSON ou conversa staged entra no inventário multi-IA",
                ],
            },
            "checklist": self.checklist(),
            "operator_cards": self.operator_cards(),
            "artifacts": self.artifact_links(),
            "pc_provider_commands": self.pc_proof_commands(),
        }
        if include_verbose:
            result["reality_audit"] = god_mode_reality_audit_service.package()
            result["download_center"] = download_install_center_v2_service.get_package()
            result["module_registry"] = module_registry_snapshot_service.snapshot(include_items=False)
        return result

    def _check(self, check_id: str, label: str, status: str, detail: str, endpoint: str | None = None) -> Dict[str, Any]:
        return {"id": check_id, "label": label, "status": status, "detail": detail, "endpoint": endpoint}


first_install_pc_proof_center_service = FirstInstallPcProofCenterService()
