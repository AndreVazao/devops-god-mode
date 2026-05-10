import os
import pytest
from app.brain.operational_state import add_goal, load_state, STATE_FILE, store
from app.brain.priority_engine import prioritize
from app.brain.task_generator import generate_tasks

@pytest.fixture(autouse=True)
def setup_teardown():
    # Setup: Ensure a clean state for testing
    if os.path.exists(STATE_FILE):
        os.remove(STATE_FILE)
    # Also reset the store's internal state if it caches
    yield
    # Teardown: Clean up after tests
    if os.path.exists(STATE_FILE):
        os.remove(STATE_FILE)

def test_add_goal_and_persistence():
    goal_text = "Fix all production bugs"
    state = add_goal(goal_text)

    assert any(g["text"] == goal_text for g in state["goals"])

    # Reload and verify persistence
    reloaded_state = load_state()
    assert any(g["text"] == goal_text for g in reloaded_state["goals"])

def test_prioritization():
    add_goal("Normal improvement 123")
    add_goal("Critical fix for crash 123")
    add_goal("Deploy latest version 123")

    state = load_state()
    prioritized = prioritize(state)

    # Check that our specific goals are there and prioritized
    our_goals = [g for g in prioritized if "123" in g["text"]]
    assert len(our_goals) == 3

    assert "fix" in our_goals[0]["text"].lower()
    assert "deploy" in our_goals[1]["text"].lower()

def test_task_generation_fix():
    goal = {"text": "Fix the login bug"}
    tasks = generate_tasks(goal)

    actions = [t["action"] for t in tasks]
    assert "dev_loop" in actions
    assert any("scan" in str(t.get("code")).lower() for t in tasks if t.get("action") == "execute_code")

def test_task_generation_deploy():
    goal = {"text": "Deploy to production"}
    tasks = generate_tasks(goal)

    types = [t["type"] for t in tasks]
    assert "check_env" in types
    assert "build" in types
    assert "deploy_vercel" in types

def test_task_generation_fallback():
    goal = {"text": "Just some random thing"}
    tasks = generate_tasks(goal)

    assert len(tasks) == 1
    assert tasks[0]["action"] == "think"
