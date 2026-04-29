from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import uuid4

from app.services.autonomous_install_research_code_service import autonomous_install_research_code_service
from app.services.local_cleanup_optimizer_service import local_cleanup_optimizer_service
from app.services.local_tool_capability_scan_service import local_tool_capability_scan_service
from app.services.ollama_model_benchmark_service import ollama_model_benchmark_service
from app.utils.atomic_json_store import AtomicJsonStore

DATA_DIR = Path("data")
PERFORMANCE_FILE = DATA_DIR / "local_performance_autopilot.json"
PERFORMANCE_STORE = AtomicJsonStore(
    PERFORMANCE_FILE,
    default_factory=lambda: {
        "version": 1,
        "policy": "safe_local_performance_autopilot_for_weak_and_strong_pcs",
        "plans": [],
        "runs": [],
    },
)


class LocalPerformanceAutopilotService:
    """One panel for local PC performance optimization.

    It combines:
    - local tool scan;
    - auto-install decision;
    - Ollama model benchmark;
    - cleanup plan;
    - weak/strong PC recommendations.

    It does not remove software or change Windows critical settings by default.
    Cleanup execution stays delegated to Local Cleanup Optimizer with the required
    approval phrase.
    """

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def policy(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "mode": "local_performance_autopilot_policy",
            "goal": "manter o PC rápido sem partir ferramentas, Windows ou memória do God Mode",
            "automatic_safe_steps": [
                "scan de ferramentas locais",
                "decisão de instalação/configuração",
                "listagem de modelos Ollama",
                "benchmark Ollama quando pedido",
                "plano de limpeza seguro",
                "geração de recomendações PC fraco/novo",
            ],
            "requires_approval": [
                "remoção real de modelos",
                "alterações Windows",
                "desinstalar programas completos",
                "limpezas que possam remover trabalho útil",
            ],
            "cleanup_phrase": "OPTIMIZE LOCAL PC",
            "weak_pc_strategy": "manter só ferramentas leves, poucos modelos Ollama, builds pesados em GitHub Actions",
            "strong_pc_strategy": "testar toolchain completa, manter melhores modelos locais e usar mais execução local",
        }

    def plan(
        self,
        pc_profile: str = "auto",
        run_ollama_benchmark: bool = False,
        ollama_timeout_seconds: Optional[int] = None,
        max_ollama_models: int = 20,
    ) -> Dict[str, Any]:
        tool_scan = local_tool_capability_scan_service.scan().get("scan", {})
        install_decision = autonomous_install_research_code_service.decide_auto_install(pc_profile=pc_profile).get("decision", {})
        ollama_models = ollama_model_benchmark_service.list_models().get("models", [])
        benchmark_run = None
        cleanup_plan = None
        if run_ollama_benchmark and ollama_models:
            benchmark_run = ollama_model_benchmark_service.benchmark(
                pc_profile=pc_profile,
                timeout_seconds=ollama_timeout_seconds,
                max_models=max_ollama_models,
            ).get("run")
            cleanup_plan = ollama_model_benchmark_service.cleanup_plan_from_latest().get("plan")
        else:
            cleanup_plan = local_cleanup_optimizer_service.plan(
                keep_ollama_models=local_cleanup_optimizer_service.DEFAULT_KEEP_OLLAMA_MODELS,
                broken_ollama_models=[],
                allow_auto_ollama_remove=True,
                allow_windows_tuning_script=True,
            ).get("plan")
        profile = self._profile(pc_profile, tool_scan, benchmark_run)
        plan = {
            "plan_id": f"local-performance-plan-{uuid4().hex[:12]}",
            "created_at": self._now(),
            "pc_profile_requested": pc_profile,
            "pc_profile_detected": profile,
            "tool_scan_id": tool_scan.get("scan_id"),
            "install_decision_id": install_decision.get("decision_id"),
            "ollama_model_count": len(ollama_models),
            "ollama_benchmark_id": (benchmark_run or {}).get("benchmark_id"),
            "cleanup_plan_id": (cleanup_plan or {}).get("plan_id"),
            "recommendations": self._recommendations(profile, install_decision, benchmark_run, cleanup_plan),
            "blocked_actions": [
                {
                    "id": "apply_cleanup",
                    "label": "Aplicar remoção/limpeza segura",
                    "endpoint": "/api/local-cleanup/apply-safe",
                    "requires_phrase": "OPTIMIZE LOCAL PC",
                },
                {
                    "id": "windows_tuning",
                    "label": "Alterações Windows",
                    "reason": "precisa revisão para não desativar serviços críticos",
                },
            ],
            "safe_next": self._safe_next(benchmark_run, cleanup_plan),
        }
        self._store("plans", plan)
        return {"ok": True, "mode": "local_performance_autopilot_plan", "plan": plan}

    def run_safe(
        self,
        pc_profile: str = "auto",
        run_ollama_benchmark: bool = True,
        ollama_timeout_seconds: Optional[int] = None,
        max_ollama_models: int = 20,
    ) -> Dict[str, Any]:
        plan = self.plan(
            pc_profile=pc_profile,
            run_ollama_benchmark=run_ollama_benchmark,
            ollama_timeout_seconds=ollama_timeout_seconds,
            max_ollama_models=max_ollama_models,
        ).get("plan", {})
        run = {
            "run_id": f"local-performance-run-{uuid4().hex[:12]}",
            "created_at": self._now(),
            "status": "completed_safe_steps",
            "plan_id": plan.get("plan_id"),
            "pc_profile_detected": plan.get("pc_profile_detected"),
            "summary": {
                "ollama_model_count": plan.get("ollama_model_count", 0),
                "cleanup_plan_id": plan.get("cleanup_plan_id"),
                "safe_next": plan.get("safe_next"),
            },
            "operator_stops": plan.get("blocked_actions", []),
            "note": "Não removeu modelos nem alterou Windows; apenas mediu, planeou e preparou próximos passos.",
        }
        self._store("runs", run)
        return {"ok": True, "mode": "local_performance_autopilot_run", "run": run}

    def _profile(self, requested: str, tool_scan: Dict[str, Any], benchmark_run: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        if requested in {"weak", "old", "legacy"}:
            label = "weak_pc"
        elif requested in {"strong", "new", "powerful"}:
            label = "strong_pc"
        else:
            available_count = tool_scan.get("available_count", 0) or 0
            partial_count = tool_scan.get("partial_count", 0) or 0
            if benchmark_run:
                rec = benchmark_run.get("recommendation") or {}
                keep_count = len(rec.get("keep_models") or [])
                label = "strong_pc" if keep_count >= 3 and available_count >= 5 else "weak_pc"
            else:
                label = "weak_pc" if partial_count > 0 or available_count < 5 else "balanced_pc"
        return {
            "label": label,
            "requested": requested,
            "available_tool_count": tool_scan.get("available_count", 0),
            "partial_tool_count": tool_scan.get("partial_count", 0),
        }

    def _recommendations(
        self,
        profile: Dict[str, Any],
        install_decision: Dict[str, Any],
        benchmark_run: Optional[Dict[str, Any]],
        cleanup_plan: Optional[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        recommendations: List[Dict[str, Any]] = []
        label = profile.get("label")
        if label == "weak_pc":
            recommendations.append({"priority": 1, "label": "Manter só 1-2 modelos Ollama bons", "reason": "evitar lentidão e bloqueios"})
            recommendations.append({"priority": 2, "label": "Usar GitHub Actions para builds pesados", "reason": "poupar CPU/RAM local"})
            recommendations.append({"priority": 3, "label": "Instalar apenas ferramentas leves essenciais", "reason": "PC antigo/fraco"})
        else:
            recommendations.append({"priority": 1, "label": "Testar e manter até 5 modelos Ollama úteis", "reason": "PC parece aguentar mais execução local"})
            recommendations.append({"priority": 2, "label": "Preparar toolchain local mais completa", "reason": "reduz dependência cloud"})
        if benchmark_run:
            rec = benchmark_run.get("recommendation") or {}
            recommendations.append({
                "priority": 4,
                "label": f"Melhor modelo Ollama: {rec.get('best_model') or 'nenhum'}",
                "reason": "resultado do benchmark local",
                "keep_models": rec.get("keep_models", []),
                "remove_models": rec.get("remove_models", []),
            })
        if cleanup_plan:
            recommendations.append({
                "priority": 5,
                "label": "Rever plano de limpeza antes de aplicar",
                "reason": "limpeza real exige frase de aprovação",
                "cleanup_plan_id": cleanup_plan.get("plan_id"),
                "auto_action_count": cleanup_plan.get("auto_action_count", 0),
            })
        install_missing = install_decision.get("decisions", []) if install_decision else []
        if install_missing:
            recommendations.append({
                "priority": 6,
                "label": "Instalar/configurar ferramentas em falta quando o PC aguentar",
                "reason": "decisão de auto-instalação já calculada",
                "decision_count": len(install_missing),
            })
        return recommendations

    def _safe_next(self, benchmark_run: Optional[Dict[str, Any]], cleanup_plan: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        if benchmark_run and cleanup_plan:
            return {
                "label": "Aplicar limpeza segura se aprovares",
                "endpoint": "/api/local-cleanup/apply-safe",
                "requires_phrase": "OPTIMIZE LOCAL PC",
            }
        if benchmark_run is None:
            return {
                "label": "Testar modelos Ollama",
                "endpoint": "/api/local-performance-autopilot/run-safe",
                "payload_hint": {"run_ollama_benchmark": True},
            }
        return {"label": "Rever plano de otimização", "endpoint": "/api/local-performance-autopilot/panel"}

    def _store(self, key: str, value: Dict[str, Any]) -> None:
        def mutate(state: Dict[str, Any]) -> Dict[str, Any]:
            state.setdefault(key, [])
            state[key].append(value)
            state[key] = state[key][-100:]
            return state
        PERFORMANCE_STORE.update(mutate)

    def latest(self) -> Dict[str, Any]:
        state = PERFORMANCE_STORE.load()
        return {
            "ok": True,
            "mode": "local_performance_autopilot_latest",
            "latest_plan": (state.get("plans") or [None])[-1],
            "latest_run": (state.get("runs") or [None])[-1],
            "plan_count": len(state.get("plans") or []),
            "run_count": len(state.get("runs") or []),
        }

    def panel(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "mode": "local_performance_autopilot_panel",
            "headline": "Otimizar PC e modelos locais",
            "policy": self.policy(),
            "latest": self.latest(),
            "safe_buttons": [
                {"id": "plan", "label": "Plano performance", "endpoint": "/api/local-performance-autopilot/plan", "priority": "critical"},
                {"id": "run_safe", "label": "Auto otimizar seguro", "endpoint": "/api/local-performance-autopilot/run-safe", "priority": "critical"},
                {"id": "benchmark", "label": "Testar Ollama", "endpoint": "/api/ollama-model-benchmark/run", "priority": "high"},
                {"id": "cleanup", "label": "Limpeza local", "endpoint": "/api/local-cleanup/panel", "priority": "high"},
            ],
        }

    def get_status(self) -> Dict[str, Any]:
        latest = self.latest()
        run = latest.get("latest_run") or {}
        return {
            "ok": True,
            "mode": "local_performance_autopilot_status",
            "plan_count": latest.get("plan_count", 0),
            "run_count": latest.get("run_count", 0),
            "latest_profile": run.get("pc_profile_detected"),
            "safe_only": True,
        }

    def get_package(self) -> Dict[str, Any]:
        return {"ok": True, "mode": "local_performance_autopilot_package", "package": {"status": self.get_status(), "panel": self.panel(), "latest": self.latest()}}


local_performance_autopilot_service = LocalPerformanceAutopilotService()
