import time
from app.services.mobile_approval_cockpit_v2_service import mobile_approval_cockpit_v2_service

# Shared dictionary to track pending approvals
# In a real system, this might be persisted or managed by a service
PENDING_APPROVALS = {}

def requires_approval(plan):
    """
    Determines if a plan requires manual approval based on its type or priority.
    """
    return plan.get("type") in ["backend", "critical"]

def wait_for_approval(plan):
    """
    Sends an approval request to the mobile cockpit and blocks until it's decided.
    """
    plan_id = str(hash(plan["title"] + str(time.time())))

    title = f"Evolution Approval: {plan['title']}"
    body = f"The God Mode Self-Evolution Engine proposes a new phase.\n\nType: {plan.get('type')}\nAction: {plan.get('action')}"

    card_res = mobile_approval_cockpit_v2_service.create_card(
        title=title,
        body=body,
        card_type="pr_write_approval",
        project_id="GOD_MODE",
        priority="high" if plan.get("type") == "critical" else "medium",
        requires_approval=True,
        actions=[
            {"action_id": "approve-evolution", "label": "Approve Evolution", "decision": "approved"},
            {"action_id": "reject-evolution", "label": "Reject", "decision": "rejected"}
        ],
        source_ref={"type": "self_evolution", "plan_id": plan_id},
        metadata=plan
    )

    card_id = card_res.get("card", {}).get("card_id")
    PENDING_APPROVALS[plan_id] = {"status": "pending", "card_id": card_id}

    print(f"📲 Evolution approval request sent to mobile. Card ID: {card_id}")

    # Wait loop
    while True:
        # Check if the card was decided in the mobile cockpit service
        cards = mobile_approval_cockpit_v2_service.list_cards(project_id="GOD_MODE", status="approved").get("cards", [])
        if any(c.get("card_id") == card_id for c in cards):
            print("✅ Evolution approved via mobile cockpit.")
            PENDING_APPROVALS[plan_id]["status"] = "approved"
            return True

        cards = mobile_approval_cockpit_v2_service.list_cards(project_id="GOD_MODE", status="rejected").get("cards", [])
        if any(c.get("card_id") == card_id for c in cards):
            print("❌ Evolution rejected via mobile cockpit.")
            PENDING_APPROVALS[plan_id]["status"] = "rejected"
            return False

        # Also check PENDING_APPROVALS for external manual approval (e.g. from relay_worker)
        if PENDING_APPROVALS[plan_id]["status"] == "approved":
             return True
        if PENDING_APPROVALS[plan_id]["status"] == "rejected":
             return False

        time.sleep(5)

def approve_locally(plan_id):
    """Callback for approving a plan from external signals (like relay_worker)."""
    if plan_id in PENDING_APPROVALS:
        PENDING_APPROVALS[plan_id]["status"] = "approved"
        return True
    return False
