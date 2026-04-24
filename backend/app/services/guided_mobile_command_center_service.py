from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List

from app.services.memory_core_service import memory_core_service
from app.services.mission_control_cockpit_service import mission_control_cockpit_service

PROJECTS = ["GOD_MODE", "PROVENTIL", "VERBAFORGE", "BOT_LORDS_MOBILE", "ECU_REPRO", "BUILD_CONTROL_CENTER"]

GUIDED_ACTIONS: List[Dict[str, Any]] = [
    {
        "action_id": "continue-project",
        "label": "Continuar projeto",
        "description": "Lê a última sessão, backlog e decisões, depois prepara o próximo passo seguro.",
        "template": "Continua o projeto {project}. Consulta a memória AndreOS, vê a última sessão, backlog, decisões e arquitetura. Diz-me o próximo passo seguro e cria cartão de aprovação se for preciso executar.",
        "risk": "safe_planning",
        "recommended": True,
    },
    {
        "action_id": "deep-audit",
        "label": "Auditoria profunda",
        "description": "Procura quebras, ficheiros mortos, inconsistências, workflows errados e lacunas.",
        "template": "Faz uma auditoria profunda ao projeto {project}. Verifica estrutura, ficheiros mortos, imports, rotas, workflows, PROJECT_TREE, memória AndreOS, backlog e riscos. Não faças alterações destrutivas sem aprovação.",
        "risk": "safe_read_only",
        "recommended": True,
    },
    {
        "action_id": "build-check",
        "label": "Ver builds",
        "description": "Foca nos workflows, artefactos, APK, EXE e checks do GitHub Actions.",
        "template": "Verifica o estado de build do projeto {project}. Analisa workflows, checks, artefactos, APK/EXE e diz o que bloqueia uma entrega limpa.",
        "risk": "safe_read_only",
        "recommended": True,
    },
    {
        "action_id": "fix-plan",
        "label": "Plano de correção",
        "description": "Gera plano por fases, PRs pequenas e validação sem escrever logo em zonas perigosas.",
        "template": "Cria um plano de correção para o projeto {project}, por fases pequenas, com PRs reversíveis, checks claros e sem ações destrutivas sem aprovação explícita.",
        "risk": "approval_required_before_write",
        "recommended": False,
    },
    {
        "action_id": "memory-review",
        "label": "Rever memória",
        "description": "Mostra se a memória do projeto está suficiente para continuar sem repetir tudo.",
        "template": "Revê a memória AndreOS do projeto {project}. Diz o que está completo, o que falta preencher em MEMORIA_MESTRE, DECISOES, BACKLOG, ARQUITETURA, HISTORICO e ULTIMA_SESSAO, e cria tarefas de backlog se necessário.",
        "risk": "safe_planning",
        "recommended": True,
    },
    {
        "action_id": "delivery-summary",
        "label": "Resumo de entrega",
        "description": "Gera resumo executivo do estado do projeto e próximos passos.",
        "template": "Gera um resumo de entrega do projeto {project}: estado atual, últimas decisões, riscos, próximos passos, builds e o que preciso aprovar.",
        "risk": "safe_planning",
        "recommended": False,
    },
]


class GuidedMobileCommandCenterService:
    """Guided, phone-first action surface for operators who do not want to remember commands."""

    def get_status(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "mode": "guided_mobile_command_center_status",
            "status": "guided_mobile_command_center_ready",
            "project_count": len(PROJECTS),
            "action_count": len(GUIDED_ACTIONS),
            "mission_control_enabled": True,
            "memory_core_enabled": True,
        }

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def list_actions(self) -> Dict[str, Any]:
        return {"ok": True, "mode": "guided_mobile_action_list", "projects": PROJECTS, "actions": GUIDED_ACTIONS}

    def _find_action(self, action_id: str) -> Dict[str, Any] | None:
        return next((item for item in GUIDED_ACTIONS if item["action_id"] == action_id), None)

    def build_project_brief(self, project: str) -> Dict[str, Any]:
        normalized = project.upper().replace("-", "_").replace(" ", "_")
        memory_core_service.initialize()
        memory_core_service.create_project(normalized)
        context = memory_core_service.compact_context(normalized, max_chars=2800)
        link = memory_core_service.obsidian_link(normalized, "MEMORIA_MESTRE.md")
        memory = memory_core_service.read_project(normalized)
        files = memory.get("memory", {}) if memory.get("ok") else {}
        checklist = {
            "master_memory": len(files.get("MEMORIA_MESTRE.md", "").strip()) > 100,
            "decisions": len(files.get("DECISOES.md", "").strip()) > 80,
            "backlog": "- [ ]" in files.get("BACKLOG.md", ""),
            "architecture": len(files.get("ARQUITETURA.md", "").strip()) > 80,
            "last_session": len(files.get("ULTIMA_SESSAO.md", "").strip()) > 80,
        }
        score = round(sum(1 for value in checklist.values() if value) / len(checklist) * 100)
        return {
            "ok": True,
            "mode": "guided_mobile_project_brief",
            "project": normalized,
            "memory_score": score,
            "checklist": checklist,
            "context_preview": context.get("context", "")[:1800],
            "obsidian": link,
        }

    def build_prompt(self, project: str, action_id: str, extra_instruction: str = "") -> Dict[str, Any]:
        action = self._find_action(action_id)
        if action is None:
            return {"ok": False, "error": "unknown_guided_action", "action_id": action_id}
        brief = self.build_project_brief(project)
        command_text = action["template"].format(project=brief["project"])
        if extra_instruction.strip():
            command_text += f"\n\nInstrução adicional do operador: {extra_instruction.strip()}"
        return {
            "ok": True,
            "mode": "guided_mobile_command_prompt",
            "project": brief["project"],
            "action": action,
            "command_text": command_text,
            "project_brief": brief,
        }

    def execute_guided_action(self, project: str, action_id: str, extra_instruction: str = "", tenant_id: str = "owner-andre") -> Dict[str, Any]:
        built = self.build_prompt(project, action_id, extra_instruction=extra_instruction)
        if not built.get("ok"):
            return built
        result = mission_control_cockpit_service.submit_mobile_command(
            command_text=built["command_text"],
            project_hint=built["project"],
            tenant_id=tenant_id,
        )
        memory_log = memory_core_service.write_history(
            built["project"],
            action="Guided Mobile Command Center action submitted",
            result=f"Action: {action_id} | Tenant: {tenant_id} | Created: {self._now()}",
        )
        return {
            "ok": True,
            "mode": "guided_mobile_command_execution",
            "prompt": built,
            "mission_control": result,
            "memory_log": memory_log,
        }

    def build_dashboard(self) -> Dict[str, Any]:
        briefs = [self.build_project_brief(project) for project in PROJECTS]
        return {
            "ok": True,
            "mode": "guided_mobile_command_center_dashboard",
            "created_at": self._now(),
            "projects": briefs,
            "actions": GUIDED_ACTIONS,
            "recommended_next_actions": [item for item in GUIDED_ACTIONS if item.get("recommended")],
        }

    def get_package(self) -> Dict[str, Any]:
        return {"ok": True, "mode": "guided_mobile_command_center_package", "package": {"status": self.get_status(), "dashboard": self.build_dashboard()}}


guided_mobile_command_center_service = GuidedMobileCommandCenterService()
