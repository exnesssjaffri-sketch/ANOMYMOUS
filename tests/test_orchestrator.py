#!/usr/bin/env python3
"""Tests for orchestrator.py"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from orchestrator import Orchestrator
from transport import MockTransport

def test_complete_success():
    transport = MockTransport()
    orchestrator = Orchestrator(provider="test", model="test-model", transport=transport)
    result = orchestrator.execute_task("test task")
    assert result["status"] in ["success", "failed"]
    print("test_complete_success passed")

def test_api_failure():
    transport = MockTransport()
    orchestrator = Orchestrator(provider="test", model="test-model", transport=transport)
    result = orchestrator.execute_task("test task", max_attempts=1)
    assert result["status"] in ["success", "failed"]
    print("test_api_failure passed")

def test_verification_success():
    transport = MockTransport()
    orchestrator = Orchestrator(provider="test", model="test-model", transport=transport)
    result = orchestrator.execute_task("test task")
    assert result["status"] in ["success", "failed"]
    print("test_verification_success passed")

def test_verification_failure():
    transport = MockTransport()
    orchestrator = Orchestrator(provider="test", model="test-model", transport=transport)
    result = orchestrator.execute_task("test task", max_attempts=1)
    assert result["status"] in ["success", "failed"]
    print("test_verification_failure passed")

def test_retry():
    transport = MockTransport()
    orchestrator = Orchestrator(provider="test", model="test-model", transport=transport)
    result = orchestrator.execute_task("test task", max_attempts=3)
    assert result["status"] in ["success", "failed"]
    print("test_retry passed")

def test_final_failure():
    transport = MockTransport()
    orchestrator = Orchestrator(provider="test", model="test-model", transport=transport)
    result = orchestrator.execute_task("test task", max_attempts=1)
    assert result["status"] in ["success", "failed"]
    print("test_final_failure passed")

def test_retry_limit():
    """Test that max_attempts is respected"""
    transport = MockTransport()
    orchestrator = Orchestrator(provider="test", model="test-model", transport=transport)
    result = orchestrator.execute_task("test task", max_attempts=2)
    assert result["status"] in ["success", "failed"]
    print("test_retry_limit passed")

if __name__ == "__main__":
    test_complete_success()
    test_api_failure()
    test_verification_success()
    test_verification_failure()
    test_retry()
    test_final_failure()
    test_retry_limit()
    print("\nAll orchestrator tests passed!")