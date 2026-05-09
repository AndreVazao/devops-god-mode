from typing import Dict, Any
from app.services.mobile_approval_cockpit_v2_service import mobile_approval_cockpit_v2_service

class SelfEvolutionGateService:
    def require_approval(self, phase_plan: Dict[str, Any]) -> Dict[str, Any]:
        # Integration with Mobile Approval Cockpit
        title = "Nova evolução proposta"
        body = f"God Mode propõe a fase: {phase_plan['meta']['phase']}\nPrioridade: {phase_plan['meta']['priority']}"

        card_res = mobile_approval_cockpit_v2_service.create_card(
            title=title,
            body=body,
            card_type="pr_write_approval", # Using existing type or progress_update
            project_id="GOD_MODE",
            priority="high" if phase_plan['meta']['priority'] == 1 else "medium",
            requires_approval=True,
            actions=[
                {"action_id": "approve-evolution", "label": "Aprovar Evolução", "decision": "approved"},
                {"action_id": "reject-evolution", "label": "Rejeitar", "decision": "rejected"}
            ],
            source_ref={"type": "self_evolution", "phase_plan": phase_plan},
            metadata=phase_plan
        )

        return {
            "type": "approval_request",
            "title": title,
            "description": phase_plan["initial_message"],
            "payload": phase_plan,
            "card_res": card_res
        }

self_evolution_gate_service = SelfEvolutionGateService()
