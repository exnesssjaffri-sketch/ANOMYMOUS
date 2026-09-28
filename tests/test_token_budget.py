#!/usr/bin/env python3
"""
Tests for token budget and 413 handling.
"""

import sys
import os
import json
import unittest
from unittest.mock import patch, MagicMock
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from token_estimator import estimate_tokens, estimate_payload_tokens, reduce_payload_tokens, can_fit_in_budget
from llmapi_adapter import LLMAPIAdapter
from transport import MockTransport, RealHTTPTransport
from orchestrator import Orchestrator


class TestTokenEstimation(unittest.TestCase):
    """Test token estimation functions."""
    
    def test_estimate_tokens_empty(self):
        self.assertEqual(estimate_tokens(""), 0)
    
    def test_estimate_tokens_short(self):
        tokens = estimate_tokens("Hello world")
        self.assertGreater(tokens, 0)
        self.assertLess(tokens, 20)
    
    def test_estimate_tokens_long(self):
        long_text = "x" * 10000
        tokens = estimate_tokens(long_text)
        self.assertGreater(tokens, 2000)
    
    def test_estimate_message_tokens(self):
        msg = {"role": "user", "content": "Hello world"}
        tokens = estimate_payload_tokens({"messages": [msg]})
        self.assertGreater(tokens, 0)
    
    def test_estimate_payload_tokens(self):
        payload = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {"role": "system", "content": "You are a helpful assistant"},
                {"role": "user", "content": "Hello, how are you?"}
            ],
            "temperature": 0,
            "response_format": {"type": "json_object"}
        }
        tokens = estimate_payload_tokens(payload)
        self.assertGreater(tokens, 0)
    
    def test_can_fit_in_budget(self):
        payload = {
            "model": "gpt-3.5-turbo",
            "messages": [{"role": "user", "content": "Hello"}]
        }
        self.assertTrue(can_fit_in_budget(payload, 7000))
        self.assertFalse(can_fit_in_budget(payload, 1))


class TestPayloadReduction(unittest.TestCase):
    """Test payload reduction strategies."""
    
    def test_reduce_removes_system_prompt(self):
        payload = {
            "model": "test-model",
            "messages": [
                {"role": "system", "content": "x" * 5000},
                {"role": "user", "content": "Short task"}
            ]
        }
        reduced = reduce_payload_tokens(payload, 100)
        self.assertEqual(len(reduced["messages"]), 1)
        self.assertEqual(reduced["messages"][0]["role"], "user")
    
    def test_reduce_truncates_user_message(self):
        payload = {
            "model": "test-model",
            "messages": [
                {"role": "user", "content": "x" * 10000}
            ]
        }
        reduced = reduce_payload_tokens(payload, 500)
        self.assertLess(len(reduced["messages"][0]["content"]), 10000)
        self.assertIn("[truncated]", reduced["messages"][0]["content"])
    
    def test_reduce_keeps_within_limit(self):
        payload = {
            "model": "test-model",
            "messages": [
                {"role": "user", "content": "x" * 50000}
            ]
        }
        reduced = reduce_payload_tokens(payload, 1000)
        tokens = estimate_payload_tokens(reduced)
        self.assertLessEqual(tokens, 1000)


class Test413Handling(unittest.TestCase):
    """Test 413 error handling and retry logic."""
    
    def test_413_detection_prompt_too_large(self):
        class FailingTransport(MockTransport):
            def __init__(self):
                super().__init__()
                self.call_count = 0
            
            def send_request(self, payload, timeout):
                self.call_count += 1
                if self.call_count == 1:
                    raise Exception('HTTP Error 413: {"error": {"type": "prompt_too_large", "message": "Prompt too large"}}')
                return {"choices": [{"message": {"content": '{"actions": []}'}}], "id": "test-123"}
        
        failing_transport = FailingTransport()
        adapter = LLMAPIAdapter("test", "test-model", failing_transport, max_tokens=100)
        result = adapter.send_request("Short task")
        
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["attempt"], 2)
        self.assertEqual(failing_transport.call_count, 2)