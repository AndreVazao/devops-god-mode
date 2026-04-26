from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from app.services.first_usable_release_service import first_usable_release_service
from app.services.install_run_readiness_service import install_run_readiness_service

ROOT = Path(".")
REPO_URL = "https://github.com/AndreVazao/devops-god-mode"
ACTIONS_URL = f"{REPO_URL}/actions"


class FirstReleaseArtifactCenterService:
    """Release artifact truth center for the first usable God Mode release."""

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def _exists(self, path: str) -> bool:
        return (ROOT / path).exists()

    def _read(self, path: str) -> str:
        target = ROOT / path
        if not target.exists():
            return ""
        return target.read_text(encoding="utf-8", errors="ignore")

    def _is_placeholder_workflow(self, content: str) -> bool:
        lowered = content.lower()
        placeholder_markers = [
            '"artifact_kind": "placeholder"',
            "'artifact_kind': 'placeholder'",
            "not_a_real_apk_yet",
            "placeholder_only",
            "placeholder_pipeline_progressive",
        ]
        return any(marker in lowered for marker in placeholder_markers)

    def _workflow(self, artifact_id: str, label: str, path: str, artifact_name: str, installable: bool, truth: str) -> Dict[str, Any]:
        content = self._read(path)
        placeholder = self._is_placeholder_workflow(content)
        return {
            "artifact_id": artifact_id,
            "label": label,
            "workflow_path": path,
            "workflow_present": self._exists(path),
            "workflow_name": label,
            "workflow_url": f"{REPO_URL}/actions/workflows/{Path(path).name}",
            "actions_url": ACTIONS_URL,
            "artifact_name": artifact_name,
            "installable_now": bool(installable and not placeholder),
            "placeholder": placeholder,
            "truth": truth if not placeholder else "placeholder_not_installable_as_real_product",
            "operator_instruction": self._instruction(artifact_id, placeholder, installable),
        }

    def _instruction(self, artifact_id: str, placeholder: bool, installable: bool) -> str:
        if artifact_id == "windows_exe" and installable and not placeholder:
            return "Correr o workflow Windows EXE Build, abrir o run mais recente e descarregar o artifact godmode-windows-exe."
        if artifact_id == "android_apk" and installable and not placeholder:
            return "Correr o workflow Android APK Build, abrir o run mais recente e descarregar o artifact godmode-android-webview-apk."
        if artifact_id == "android_apk" and placeholder:
            return "Não instalar como APK real. Este workflow ainda gera placeholder; criar APK real/WebView shell."
        return "Correr workflow correspondente e verificar artifact no run mais recente."

    def build_artifact_report(self) -> Dict[str, Any]:
        artifacts = [
            self._workflow(
                artifact_id="windows_exe",
                label="Windows EXE Build",
                path=".github/workflows/windows-exe-real-build.yml",
                artifact_name="godmode-windows-exe",
                installable=True,
                truth="real_pyinstaller_exe_bundle",
            ),
            self._workflow(
                artifact_id="android_apk",
                label="Android APK Build",
                path=".github/workflows/android-real-build-progressive.yml",
                artifact_name="godmode-android-webview-apk",
                installable=True,
                truth="real_webview_shell_debug_apk",
            ),
            self._workflow(
                artifact_id="universal_test",
                label="Universal Total Test",
                path=".github/workflows/universal-total-test.yml",
                artifact_name="test_report",
                installable=False,
                truth="quality_gate",
            ),
        ]
        readiness = install_run_readiness_service.get_status()
        first_use = first_usable_release_service.get_status()
        blockers: List[Dict[str, Any]] = []
        for artifact in artifacts:
            if not artifact["workflow_present"]:
                blockers.append({"id": f"missing_workflow:{artifact['artifact_id']}", "label": artifact["label"], "detail": artifact["workflow_path"]})
        android = next(item for item in artifacts if item["artifact_id"] == "android_apk")
        if android["placeholder"]:
            blockers.append({"id": "android_apk:placeholder", "label": "APK ainda é placeholder", "detail": "Criar APK real/WebView shell antes de dizer que há APK instalável."})
        windows = next(item for item in artifacts if item["artifact_id"] == "windows_exe")
        status = "green" if windows["installable_now"] and android["installable_now"] and not blockers else "yellow"
        if not windows["workflow_present"] or not android["workflow_present"]:
            status = "red"
        return {
            "ok": True,
            "mode": "first_release_artifact_report",
            "created_at": self._now(),
            "status": status,
            "release_truth": self._release_truth(status, android["placeholder"]),
            "repo_url": REPO_URL,
            "actions_url": ACTIONS_URL,
            "artifacts": artifacts,
            "blockers": blockers,
            "readiness": readiness,
            "first_usable_release": first_use,
            "download_steps": self._download_steps(artifacts),
            "next_actions": self._next_actions(blockers),
        }

    def _release_truth(self, status: str, android_placeholder: bool) -> str:
        if android_placeholder:
            return "PC EXE path is usable, but Android APK is still placeholder. First usable release is PC-first with mobile web/APK shell pending real build."
        if status == "green":
            return "EXE and Android WebView debug APK artifact paths are ready for first controlled release."
        return "Release artifacts need blockers resolved before install/use."

    def _download_steps(self, artifacts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        return [
            {
                "step": 1,
                "title": "Abrir Actions",
                "detail": ACTIONS_URL,
            },
            {
                "step": 2,
                "title": "Descarregar EXE Windows",
                "detail": "Abrir workflow Windows EXE Build → último run verde → Artifacts → godmode-windows-exe.",
                "artifact_id": "windows_exe",
            },
            {
                "step": 3,
                "title": "Descarregar APK Android WebView",
                "detail": "Abrir workflow Android APK Build → último run verde → Artifacts → godmode-android-webview-apk → instalar GodModeMobile-debug.apk.",
                "artifact_id": "android_apk",
            },
            {
                "step": 4,
                "title": "Configurar URL do PC no APK",
                "detail": "No APK, trocar o URL base para o IP do PC, por exemplo http://192.168.1.50:8000, e abrir /app/apk-start.",
                "artifact_id": "android_apk",
            },
            {
                "step": 5,
                "title": "Validar no God Mode",
                "detail": "Abrir /app/first-use, /app/install-readiness e /app/e2e-operational-drill.",
            },
        ]

    def _next_actions(self, blockers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        actions = [
            {"priority": "critical", "label": "Executar Android APK Build", "detail": "Descarregar godmode-android-webview-apk do run verde."},
            {"priority": "high", "label": "Executar Windows EXE Build", "detail": "Descarregar godmode-windows-exe do run verde."},
            {"priority": "high", "label": "Instalar APK debug em teste controlado", "detail": "Configurar URL do PC no campo do APK."},
            {"priority": "high", "label": "Correr E2E Drill depois de instalar", "detail": "/app/e2e-operational-drill"},
        ]
        if blockers:
            actions.insert(0, {"priority": "critical", "label": "Resolver blockers de artifacts", "detail": f"{len(blockers)} blocker(s)"})
        return actions

    def get_status(self) -> Dict[str, Any]:
        report = self.build_artifact_report()
        return {
            "ok": True,
            "mode": "first_release_artifact_center_status",
            "status": report["status"],
            "blocker_count": len(report["blockers"]),
            "release_truth": report["release_truth"],
        }

    def build_dashboard(self) -> Dict[str, Any]:
        report = self.build_artifact_report()
        return {
            "ok": True,
            "mode": "first_release_artifact_center_dashboard",
            "report": report,
            "buttons": [
                {"id": "actions", "label": "GitHub Actions", "url": ACTIONS_URL, "priority": "critical"},
                {"id": "first_use", "label": "First Use", "route": "/app/first-use", "priority": "high"},
                {"id": "readiness", "label": "Readiness", "route": "/app/install-readiness", "priority": "high"},
                {"id": "drill", "label": "E2E Drill", "route": "/app/e2e-operational-drill", "priority": "medium"},
            ],
        }

    def get_package(self) -> Dict[str, Any]:
        return {"ok": True, "mode": "first_release_artifact_center_package", "package": {"status": self.get_status(), "dashboard": self.build_dashboard(), "report": self.build_artifact_report()}}


first_release_artifact_center_service = FirstReleaseArtifactCenterService()
