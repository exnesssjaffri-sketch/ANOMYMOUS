import pytest
import sys
import os
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from failure_recovery import recover_from_failure

@pytest.fixture
def temp_output_dir():
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir

def test_recover_from_failure(temp_output_dir):
    error_message = "Module \"./Navbar\" not found."
    task_description = "Build a restaurant website"
    repair_task = recover_from_failure(error_message, task_description, temp_output_dir)
    
    assert "Fix the following error" in repair_task, "Repair task should contain the error message"
    assert task_description in repair_task, "Repair task should contain the task description"
    
    repair_file_path = os.path.join(temp_output_dir, "repair_task.txt")
    assert os.path.exists(repair_file_path), "Repair task file should be created"
    
    with open(repair_file_path, "r") as file:
        content = file.read()
    assert error_message in content, "Repair task file should contain the error message"
    assert task_description in content, "Repair task file should contain the task description"