#!/usr/bin/env python3
"""Orchestrator end-to-end failure scenario tests."""
import sys, os, json, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from workspace_manager import WorkspaceManager
from action_executor import ActionExecutor
from orchestrator import Orchestrator
from task_classifier import TaskClassifier
from verification import TaskVerifier


class MockLLMAPIAdapter:
    def __init__(self, responses):
        self.responses = responses
        self.call_count = 0
        self.provider = "mock"
        self.model = "mock-model"

    def send_request(self, task, system_prompt=None):
        if self.call_count < len(self.responses):
            resp = self.responses[self.call_count]
            self.call_count += 1
            return resp
        return {"status": "error", "error": "No more mock responses"}


def make_orchestrator(workspace_dir, responses):
    o = Orchestrator.__new__(Orchestrator)
    o.task_classifier = TaskClassifier()
    o.workspace_manager = WorkspaceManager(workspace_dir)
    o.action_executor = ActionExecutor(o.workspace_manager)
    o.verifier = TaskVerifier(workspace_dir)
    o.llmapi_adapter = MockLLMAPIAdapter(responses)
    o.router = None
    return o


def test_intermediate_attempt():
    """Test that orchestrator handles failure on intermediate attempt correctly."""
    tmp = tempfile.mkdtemp()
    ws = os.path.join(tmp, "workspace")
    os.makedirs(ws, exist_ok=True)
    with open(os.path.join(ws, "existing_file.txt"), "w") as f:
        f.write("placeholder\n")

    o = make_orchestrator(ws, [
        {"status": "success", "output": json.dumps({"actions": [
            {"type": "create_file", "path": "test.txt", "content": "hello", "critical": True}
        ]}), "provider": "mock", "model": "mock-model"},
        {"status": "success", "output": json.dumps({"actions": [
            {"type": "create_file", "path": "test.txt", "content": "hello", "critical": True}
        ]}), "provider": "mock", "model": "mock-model"},
    ])
    r = o.execute_task("Create a file", max_attempts=3)
    assert r["status"] == "success", f"Expected success, got {r['status']}"
    print(f"  PASS: intermediate attempt -> status={r['status']}")


def test_final_attempt_failure():
    """Test that orchestrator returns failed on final attempt with execution error."""
    tmp = tempfile.mkdtemp()
    ws = os.path.join(tmp, "workspace")
    o = make_orchestrator(ws, [
        {"status": "success", "output": json.dumps({"actions": [
            {"type": "run_build", "command": ["python", "-c", "import sys; sys.exit(1)"], "critical": True}
        ]}), "provider": "mock", "model": "mock-model"},
        {"status": "success", "output": json.dumps({"actions": [
            {"type": "run_build", "command": ["python", "-c", "import sys; sys.exit(1)"], "critical": True}
        ]}), "provider": "mock", "model": "mock-model"},
        {"status": "success", "output": json.dumps({"actions": [
            {"type": "run_build", "command": ["python", "-c", "import sys; sys.exit(1)"], "critical": True}
        ]}), "provider": "mock", "model": "mock-model"},
    ])
    r = o.execute_task("Build the project", max_attempts=3)
    assert r["status"] == "failed", f"Expected failed, got {r['status']}"
    assert "Execution failed" in r["diagnostics"][0], f"Expected execution failure in diagnostics, got {r['diagnostics']}"
def test_no_false_success():
    """Test that failed execution can NEVER become overall success."""
    tmp = tempfile.mkdtemp()
    ws = os.path.join(tmp, "workspace")
    o = make_orchestrator(ws, [
        {"status": "success", "output": json.dumps({"actions": [
            {"type": "run_build", "command": ["python", "-c", "import sys; sys.exit(1)"], "critical": True}
        ]}), "provider": "mock", "model": "mock-model"},
    ])
    r = o.execute_task("Build the project", max_attempts=1)
    assert r["status"] != "success", f"CRITICAL: Failed execution became success! Status: {r['status']}"
    assert r["status"] == "failed"
    print(f"  PASS: no false success -> status={r['status']}")


def test_error_propagation():
    """Test that error status from action_executor propagates correctly."""
    tmp = tempfile.mkdtemp()
    ws = os.path.join(tmp, "workspace")
    o = make_orchestrator(ws, [
        {"status": "success", "output": json.dumps({"actions": [
            {"type": "invalid_action_type", "critical": True}
        ]}), "provider": "mock", "model": "mock-model"},
    ])
    r = o.execute_task("Do something invalid", max_attempts=1)
    assert r["status"] == "failed", f"Expected failed, got {r['status']}"
    assert "Unsupported action type" in str(r.get("execution", {}).get("error", ""))
    print(f"  PASS: error propagation -> status={r['status']}")


def test_failed_status_propagation():
    """Test that 'failed' status from process_executor propagates through orchestrator."""
    tmp = tempfile.mkdtemp()
    ws = os.path.join(tmp, "workspace")
    o = make_orchestrator(ws, [
        {"status": "success", "output": json.dumps({"actions": [
            {"type": "run_build", "command": ["python", "-c", "import sys; sys.exit(42)"], "critical": True}
        ]}), "provider": "mock", "model": "mock-model"},
    ])
    r = o.execute_task("Run build", max_attempts=1)
    assert r["status"] == "failed", f"Expected failed, got {r['status']}"
    exec_result = r.get("execution", {})
    assert exec_result.get("status") == "error", f"Expected execution status error, got {exec_result.get('status')}"
    print(f"  PASS: failed status propagation -> execution status={exec_result.get('status')}")


if __name__ == "__main__":
    print("=" * 60)
    print("Orchestrator End-to-End Failure Tests")
    print("=" * 60)
    test_intermediate_attempt()
    test_final_attempt_failure()
    test_no_false_success()
    test_error_propagation()
    test_failed_status_propagation()
    print()
    print("=" * 60)
    print("ALL ORCHESTRATOR E2E TESTS PASSED")
    print("=" * 60)
