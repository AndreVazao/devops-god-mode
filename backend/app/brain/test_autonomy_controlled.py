import os
import time
import pytest
from app.brain.policy_engine import requires_approval
from app.brain.budget_manager import check_budget, STATE_FILE as BUDGET_FILE
from app.brain.learner import record, get_learning_data, STATE_FILE as LEARNING_FILE
from app.brain.skill_registry import get_skill
from app.brain.safe_executor import run_action

@pytest.fixture(autouse=True)
def cleanup():
    if os.path.exists(BUDGET_FILE):
        os.remove(BUDGET_FILE)
    if os.path.exists(LEARNING_FILE):
        os.remove(LEARNING_FILE)
    yield
    if os.path.exists(BUDGET_FILE):
        os.remove(BUDGET_FILE)
    if os.path.exists(LEARNING_FILE):
        os.remove(LEARNING_FILE)

def test_policy_engine():
    assert requires_approval("deploy_vercel") is True
    assert requires_approval("scan_errors") is False

def test_budget_manager():
    # Initial check should pass
    assert check_budget() is True

    # Manually modify state to reach limit
    from app.brain.budget_manager import store
    state = store.load()
    state["cycle_count"] = 60
    store.save(state)

    assert check_budget() is False

def test_skill_registry():
    assert get_skill("scan_errors") == "scripts/scan_errors.py"
    assert get_skill("non_existent") is None

def test_learner():
    record("test_action", True)
    data = get_learning_data()
    assert data["test_action"]["ok"] == 1

    record("test_action", False)
    data = get_learning_data()
    assert data["test_action"]["fail"] == 1

def test_safe_executor_skill(capsys):
    # scan_errors does not require approval and is a skill
    result = run_action("scan_errors")
    assert result["status"] == "success"
    assert "Scanning" in result["stdout"]

def test_safe_executor_orchestrator():
    # 'think' is not a skill and not critical, should go to orchestrator
    result = run_action("think", {"goal": "test goal"})
    # Result from god_brain.think contains 'plan' or 'error'
    assert "plan" in result or "error" in result
