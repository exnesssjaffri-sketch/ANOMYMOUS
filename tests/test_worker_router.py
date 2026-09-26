import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from worker_router import select_best_worker, WORKER_CAPABILITIES
from worker_registry import WORKER_REGISTRY

@pytest.fixture
def mock_worker_registry(monkeypatch):
    monkeypatch.setattr("worker_registry.WORKER_REGISTRY", {
        "FCC": {"available": True, "capabilities": ["implementation", "simple coding", "website creation", "bug fixes"]},
        "Claude": {"available": True, "capabilities": ["architecture", "complex reasoning", "debugging", "code review"]},
        "OpenCode": {"available": True, "capabilities": ["implementation", "frontend", "full-stack", "refactoring"]},
    })

def test_select_best_worker(mock_worker_registry):
    task_classification = {"simple": True, "frontend": False, "debugging": False, "complex": False}
    best_worker = select_best_worker(task_classification)
    assert best_worker == "FCC", "FCC should be selected for simple tasks"

    task_classification = {"simple": False, "frontend": True, "debugging": False, "complex": False}
    best_worker = select_best_worker(task_classification)
    assert best_worker == "OpenCode", "OpenCode should be selected for frontend tasks"

    task_classification = {"simple": False, "frontend": False, "debugging": True, "complex": False}
    best_worker = select_best_worker(task_classification)
    assert best_worker == "Claude", "Claude should be selected for debugging tasks"

    task_classification = {"simple": False, "frontend": False, "debugging": False, "complex": True}
    best_worker = select_best_worker(task_classification)
    assert best_worker == "Claude", "Claude should be selected for complex tasks"