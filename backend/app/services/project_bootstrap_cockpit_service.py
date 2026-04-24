from __future__ import annotations

from typing import Any, Dict, List

from app.services.godmode_diagnostics_service import godmode_diagnostics_service
from app.services.godmode_remediation_service import godmode_remediation_service
from app.services.provider_onboarding_cockpit_service import provider_onboarding_cockpit_service


class ProjectBootstrapCockpitService:
    def get_status(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "mode": "project_bootstrap_cockpit_status",
            "status": "project_bootstrap_cockpit_ready",
        }

    def build_dashboard(
        self,
        tenant_id: str = "owner-andre",
        project_name: str = "godmode-project",
        providers: List[str] | None = None,
        multirepo_mode: bool = True,
    ) -> Dict[str, Any]:
        requested_providers = providers or ["github", "vercel", "supabase", "render"]
        diagnostics = godmode_diagnostics_service.build_dashboard(tenant_id=tenant_id)
        remediation = godmode_remediation_service.build_plan(tenant_id=tenant_id)
        onboarding = provider_onboarding_cockpit_service.build_dashboard(
            tenant_id=tenant_id,
            project_name=project_name,
            providers=requested_providers,
            multirepo_mode=multirepo_mode,
        )

        blockers: List[str] = []
        blockers.extend(diagnostics.get("blockers", []))
        blockers.extend(onboarding.get("blockers", []))

        unique_blockers: List[str] = []
        seen = set()
        for blocker in blockers:
            normalized = blocker.strip().lower()
            if normalized and normalized not in seen:
                seen.add(normalized)
                unique_blockers.append(blocker)

        launch_ready = diagnostics.get("blocker_count", 0) == 0 and onboarding.get("blocker_count", 0) == 0
        readiness_score = 100
        readiness_score -= min(diagnostics.get("blocker_count", 0) * 15, 45)
        readiness_score -= min(onboarding.get("blocker_count", 0) * 15, 45)
        if diagnostics.get("secret_count", 0) == 0:
            readiness_score -= 15
        readiness_score = max(readiness_score, 0)

        launch_phases = [
            {
                "phase_id": "diagnostics",
                "label": "Diagnóstico base",
                "status": "ready" if diagnostics.get("blocker_count", 0) == 0 else "blocked",
                "summary": f"{diagnostics.get('blocker_count', 0)} blockers detetados no cockpit de diagnóstico.",
            },
            {
                "phase_id": "provider_onboarding",
                "label": "Onboarding de providers",
                "status": "ready" if onboarding.get("blocker_count", 0) == 0 else "blocked",
                "summary": f"{onboarding.get('provider_count', 0)} providers pedidos para o projeto alvo.",
            },
            {
                "phase_id": "remediation",
                "label": "Remediação imediata",
                "status": "ready" if remediation.get("action_count", 0) == 0 else "attention_required",
                "summary": f"{remediation.get('action_count', 0)} ações sugeridas para limpar bloqueios e inconsistências.",
            },
            {
                "phase_id": "project_launch",
                "label": "Lançamento do projeto",
                "status": "ready" if launch_ready else "hold",
                "summary": "Pode avançar já" if launch_ready else "Convém limpar blockers antes de lançar cadeia completa.",
            },
        ]

        return {
            "ok": True,
            "mode": "project_bootstrap_cockpit_dashboard",
            "dashboard_status": "project_bootstrap_cockpit_dashboard_ready",
            "tenant_id": tenant_id,
            "project_name": project_name,
            "providers": requested_providers,
            "multirepo_mode": multirepo_mode,
            "launch_ready": launch_ready,
            "readiness_score": readiness_score,
            "blocker_count": len(unique_blockers),
            "blockers": unique_blockers,
            "launch_phases": launch_phases,
            "diagnostics": {
                "blocker_count": diagnostics.get("blocker_count", 0),
                "provider_count": diagnostics.get("provider_count", 0),
                "secret_count": diagnostics.get("secret_count", 0),
                "tenant_count": diagnostics.get("tenant_count", 0),
            },
            "onboarding": {
                "provider_count": onboarding.get("provider_count", 0),
                "blocker_count": onboarding.get("blocker_count", 0),
                "repo_plan": onboarding.get("repo_plan", {}),
                "first_run_steps": onboarding.get("first_run_steps", []),
                "manifest_file": onboarding.get("manifest_file"),
            },
            "remediation": {
                "action_count": remediation.get("action_count", 0),
                "actions": remediation.get("actions", []),
            },
        }

    def get_package(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "mode": "project_bootstrap_cockpit_package",
            "package": {
                "status": self.get_status(),
                "package_status": "project_bootstrap_cockpit_ready",
            },
        }


project_bootstrap_cockpit_service = ProjectBootstrapCockpitService()
