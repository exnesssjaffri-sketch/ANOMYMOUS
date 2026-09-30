#!/usr/bin/env python3
"""Deterministic failure scenario tests for orchestrator → action_executor → process_executor chain."""
import sys, os, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from workspace_manager import WorkspaceManager
from action_executor import ActionExecutor
from process_executor import execute_process

def test_action_executor_failed_status_propagation():
    """Test that action_executor properly propagates 'failed' status from process_executor."""
    tmp = tempfile.mkdtemp()
    wm = WorkspaceManager(tmp)
    ae = ActionExecutor(wm)
    
    # Test 1: run_build with command that fails (non-zero exit)
    result = ae.execute_action({
        'type': 'run_build',
        'command': ['python', '-c', 'import sys; sys.exit(1)'],
        'critical': True
    })
    
    print(f"Test 1 - Failed command result: {result}")
    assert result["status"] == "failed", f"Expected 'failed', got '{result['status']}'"
    assert result["returncode"] == 1, f"Expected returncode 1, got {result['returncode']}"
    print("PASS: Failed command returns 'failed' status")
    
    # Test 2: run_build with command that succeeds
    result = ae.execute_action({
        'type': 'run_build',
        'command': ['python', '-c', 'print("hello")'],
        'critical': True
    })
    
    print(f"Test 2 - Success command result: {result}")
    assert result["status"] == "success", f"Expected 'success', got '{result['status']}'"
    assert result["returncode"] == 0
    print("PASS: Successful command returns 'success' status")
    
    # Test 3: execute_actions with critical failed action stops execution
    result = ae.execute_actions([
        {'type': 'create_file', 'path': 'test1.txt', 'content': 'hello', 'critical': True},
        {'type': 'run_build', 'command': ['python', '-c', 'import sys; sys.exit(1)'], 'critical': True},
        {'type': 'create_file', 'path': 'test2.txt', 'content': 'world', 'critical': True},
    ])
    
    print(f"Test 3 - execute_actions with critical failure: {result}")
    assert result["status"] == "error", f"Expected 'error', got '{result['status']}'"
    assert len(result["results"]) == 2, f"Expected 2 results (stopped at failure), got {len(result['results'])}"
    assert result["results"][0]["status"] == "success"
    assert result["results"][1]["status"] == "failed"
    print("PASS: execute_actions stops at critical failure")
    
    # Test 4: execute_actions with non-critical failed action continues
    result = ae.execute_actions([
        {'type': 'create_file', 'path': 'test1.txt', 'content': 'hello', 'critical': True},
        {'type': 'run_build', 'command': ['python', '-c', 'import sys; sys.exit(1)'], 'critical': False},
        {'type': 'create_file', 'path': 'test2.txt', 'content': 'world', 'critical': True},
    ])
    
    print(f"Test 4 - execute_actions with non-critical failure: {result}")
    assert result["status"] == "success", f"Expected 'success', got '{result['status']}'"
    assert len(result["results"]) == 3, f"Expected 3 results, got {len(result['results'])}"
    print("PASS: execute_actions continues past non-critical failure")
    
    # Test 5: execute_actions with critical error action (not failed)
    result = ae.execute_actions([
        {'type': 'create_file', 'path': 'test1.txt', 'content': 'hello', 'critical': True},
        {'type': 'invalid_type', 'critical': True},
    ])
    
    print(f"Test 5 - execute_actions with error status: {result}")
    assert result["status"] == "error", f"Expected 'error', got '{result['status']}'"
    assert len(result["results"]) == 2
    print("PASS: execute_actions stops at error status")
    
    return True

def test_process_executor_statuses():
    """Test process_executor returns correct status values."""
    # Test SUCCESS
    result = execute_process(['python', '-c', 'print("ok")'])
    assert result["status"] == "SUCCESS", f"Expected SUCCESS, got {result['status']}"
    print(f"PASS: process_executor SUCCESS: {result['status']}")
    
    # Test FAILED
    result = execute_process(['python', '-c', 'import sys; sys.exit(42)'])
    assert result["status"] == "FAILED", f"Expected FAILED, got {result['status']}"
    assert result["returncode"] == 42
    print(f"PASS: process_executor FAILED: {result['status']} with returncode {result['returncode']}")
    
    # Test COMMAND_NOT_FOUND
    result = execute_process(['nonexistent_command_xyz_123'])
    assert result["status"] == "COMMAND_NOT_FOUND", f"Expected COMMAND_NOT_FOUND, got {result['status']}"
    print(f"PASS: process_executor COMMAND_NOT_FOUND: {result['status']}")
    
    return True

if __name__ == "__main__":
    print("=" * 60)
    print("Testing process_executor statuses")
    print("=" * 60)
    test_process_executor_statuses()
    
    print("\n" + "=" * 60)
    print("Testing ActionExecutor failure propagation")
    print("=" * 60)
    test_action_executor_failed_status_propagation()
    
    print("\n" + "=" * 60)
    print("ALL TESTS PASSED")
    print("=" * 60)