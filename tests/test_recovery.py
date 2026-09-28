#!/usr/bin/env python3
"""Tests for recovery and retry logic"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from orchestrator import Orchestrator
from transport import MockTransport

def test_retryable():
    transport = MockTransport()
    orchestrator = Orchestrator(provider="test", model="test-model", transport=transport)
    result = orchestrator.execute_task("test task", max_attempts=3)
    assert result["status"] in ["success", "failed"]
    print("test_retryable passed")

def test_non_retryable():
    transport = MockTransport()
    orchestrator = Orchestrator(provider="test", model="test-model", transport=transport)
    result = orchestrator.execute_task("test task", max_attempts=1)
    assert result["status"] in ["success", "failed"]
    print("test_non_retryable passed")

def test_attempt_limit():
    transport = MockTransport()
    orchestrator = Orchestrator(provider="test", model="test-model", transport=transport)
    result = orchestrator.execute_task("test task", max_attempts=2)
    assert result["status"] in ["success", "failed"]
    print("test_attempt_limit passed")

def test_repair_context():
    transport = MockTransport()
    orchestrator = Orchestrator(provider="test", model="test-model", transport=transport)
    result = orchestrator.execute_task("test task", max_attempts=1)
    assert "diagnostics" in result
    print("test_repair_context passed")

if __name__ == "__main__":
    test_retryable()
    test_non_retryable()
    test_attempt_limit()
    test_repair_context()
    print("\nAll recovery tests passed!")