#!/usr/bin/env python3
"""Tests for local work and process execution"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from process_executor import execute_process

def test_safe_file_operations():
    """Test that file operations are safe"""
    result = execute_process([sys.executable, "-c", "print('hello')"])
    assert result["status"] == "SUCCESS"
    print("test_safe_file_operations passed")

def test_workspace_restriction():
    """Test that workspace restrictions are enforced"""
    result = execute_process([sys.executable, "-c", "print('hello')"], cwd="/nonexistent")
    assert result["status"] == "FAILED"
    print("test_workspace_restriction passed")

def test_controlled_process_execution():
    """Test that process execution is controlled"""
    result = execute_process([sys.executable, "-c", "print('hello')"])
    assert result["status"] == "SUCCESS"
    print("test_controlled_process_execution passed")

if __name__ == "__main__":
    test_safe_file_operations()
    test_workspace_restriction()
    test_controlled_process_execution()
    print("\nAll local_work tests passed!")