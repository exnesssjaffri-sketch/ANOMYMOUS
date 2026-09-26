import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from task_classifier import classify_task

@pytest.mark.parametrize("task_description, expected_flags", [
    ("Build a simple website", {"simple": True, "frontend": True, "medium": True}),
    ("Fix a broken import", {"simple": True, "debugging": True, "medium": True}),
    ("Debug login error", {"debugging": True, "medium": True}),
    ("Build a complex SaaS dashboard", {"complex": True, "full-stack": True}),
])
def test_task_classification(task_description, expected_flags):
    classification = classify_task(task_description)
    for flag, expected_value in expected_flags.items():
        assert classification[flag] == expected_value, f"Flag {flag} does not match for task: {task_description}"