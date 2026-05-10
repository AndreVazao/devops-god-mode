import pytest
from unittest.mock import MagicMock, patch
from app.evolution.memory_reader import read_memory
from app.evolution.planner import generate_plan
from app.evolution.executor import execute_plan
from app.evolution.approval import requires_approval

def test_memory_reader_import():
    # Basic import test
    assert read_memory is not None

def test_requires_approval():
    assert requires_approval({"type": "critical"}) is True
    assert requires_approval({"type": "standard"}) is False

@patch("app.evolution.planner.god_mode_global_state_service")
@patch("app.evolution.planner.self_state_analyzer_service")
@patch("app.evolution.planner.gap_detector_service")
@patch("app.evolution.planner.roadmap_generator_service")
@patch("app.evolution.planner.phase_planner_service")
def test_generate_plan_no_roadmap(mock_phase, mock_roadmap, mock_gap, mock_analyzer, mock_state):
    mock_roadmap.generate_roadmap.return_value = []
    plan = generate_plan({"some": "memory"})
    assert plan is None

@patch("app.evolution.executor.run_task")
def test_execute_plan(mock_run_task):
    mock_run_task.return_value = {"status": "completed"}
    result = execute_plan({"action": "dev_loop", "title": "Test Plan"})
    assert result["status"] == "completed"
    mock_run_task.assert_called_once()
