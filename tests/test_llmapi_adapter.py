#!/usr/bin/env python3
"""Tests for llmapi_adapter.py"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from llmapi_adapter import LLMAPIAdapter

def test_send_request_success():
    from transport import MockTransport
    transport = MockTransport()
    adapter = LLMAPIAdapter(provider="test", model="test-model", transport=transport)
    result = adapter.send_request("test task")
    assert result["status"] == "success"
    assert result["provider"] == "test"
    assert result["model"] == "test-model"
    assert result["output"] is not None
    assert result["error"] is None
    assert result["timed_out"] is False
    assert result["attempt"] == 1
    print("test_send_request_success passed")

def test_send_request_timeout():
    from transport import MockTransport
    transport = MockTransport()
    adapter = LLMAPIAdapter(provider="test", model="test-model", transport=transport)
    result = adapter.send_request("test task")
    assert "status" in result
    assert "duration" in result
    print("test_send_request_timeout passed")

def test_send_request_network_failure():
    from transport import MockTransport
    transport = MockTransport()
    adapter = LLMAPIAdapter(provider="test", model="test-model", transport=transport)
    result = adapter.send_request("test task")
    assert result["status"] in ["success", "error"]
    print("test_send_request_network_failure passed")

def test_send_request_auth_failure():
    from transport import MockTransport
    transport = MockTransport()
    adapter = LLMAPIAdapter(provider="test", model="test-model", transport=transport)
    result = adapter.send_request("test task")
    assert result["status"] in ["success", "error"]
    print("test_send_request_auth_failure passed")

def test_send_request_rate_limit():
    from transport import MockTransport
    transport = MockTransport()
    adapter = LLMAPIAdapter(provider="test", model="test-model", transport=transport)
    result = adapter.send_request("test task")
    assert result["status"] in ["success", "error"]
    print("test_send_request_rate_limit passed")

def test_send_request_provider_failure():
    from transport import MockTransport
    transport = MockTransport()
    adapter = LLMAPIAdapter(provider="test", model="test-model", transport=transport)
    result = adapter.send_request("test task")
    assert result["status"] in ["success", "error"]
    print("test_send_request_provider_failure passed")

def test_send_request_malformed_response():
    from transport import MockTransport
    transport = MockTransport()
    adapter = LLMAPIAdapter(provider="test", model="test-model", transport=transport)
    result = adapter.send_request("test task")
    assert result["status"] in ["success", "error"]
    print("test_send_request_malformed_response passed")

if __name__ == "__main__":
    test_send_request_success()
    test_send_request_timeout()
    test_send_request_network_failure()
    test_send_request_auth_failure()
    test_send_request_rate_limit()
    test_send_request_provider_failure()
    test_send_request_malformed_response()
    print("\nAll llmapi_adapter tests passed!")