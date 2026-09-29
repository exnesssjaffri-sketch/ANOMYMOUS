#!/usr/bin/env python3
"""Tests for error_classifier.py"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from error_classifier import ErrorClassifier

def test_classify_prompt_too_large():
    error = Exception('HTTP Error 413: {"error": {"type": "prompt_too_large", "message": "Prompt too large"}}')
    result = ErrorClassifier.classify_exception(error)
    assert result == ErrorClassifier.PROMPT_TOO_LARGE
    print("test_classify_prompt_too_large passed")

def test_classify_tpm_limit_exceeded():
    error = Exception('HTTP Error 413: {"error": {"type": "tpm_limit_exceeded", "message": "TPM limit exceeded"}}')
    result = ErrorClassifier.classify_exception(error)
    assert result == ErrorClassifier.TPM_LIMIT_EXCEEDED
    print("test_classify_tpm_limit_exceeded passed")

def test_classify_daily_quota_exhausted():
    error = Exception('HTTP Error 413: {"error": {"type": "daily_quota_exhausted", "message": "Daily quota exhausted"}}')
    result = ErrorClassifier.classify_exception(error)
    assert result == ErrorClassifier.DAILY_QUOTA_EXHAUSTED
    print("test_classify_daily_quota_exhausted passed")

def test_classify_request_too_large():
    error = Exception('HTTP Error 413: {"error": {"message": "Request too large"}}')
    result = ErrorClassifier.classify_exception(error)
    assert result == ErrorClassifier.REQUEST_TOO_LARGE
    print("test_classify_request_too_large passed")

def test_classify_rate_limit():
    error = Exception('HTTP Error 429: {"error": {"message": "Rate limit exceeded"}}')
    result = ErrorClassifier.classify_exception(error)
    assert result == ErrorClassifier.RATE_LIMIT
    print("test_classify_rate_limit passed")

def test_classify_auth_error():
    error = Exception('HTTP Error 403: {"error": {"message": "Forbidden"}}')
    result = ErrorClassifier.classify_exception(error)
    assert result == ErrorClassifier.AUTH_ERROR
    print("test_classify_auth_error passed")

def test_classify_unavailable():
    error = Exception('HTTP Error 503: {"error": {"message": "Service unavailable"}}')
    result = ErrorClassifier.classify_exception(error)
    assert result == ErrorClassifier.UNAVAILABLE
    print("test_classify_unavailable passed")

def test_classify_timeout():
    error = Exception('Timeout: Request timed out after 30s')
    result = ErrorClassifier.classify_exception(error)
    assert result == ErrorClassifier.TIMEOUT
    print("test_classify_timeout passed")

def test_classify_network_error():
    error = Exception('Transport Error: Connection refused')
    result = ErrorClassifier.classify_exception(error)
    assert result == ErrorClassifier.NETWORK_ERROR
    print("test_classify_network_error passed")

def test_classify_all_models_rate_limited():
    error = Exception('HTTP Error 429: {"error": {"type": "all_models_rate_limited", "message": "All models rate limited"}}')
    result = ErrorClassifier.classify_exception(error)
    assert result == ErrorClassifier.ALL_MODELS_RATE_LIMITED
    print("test_classify_all_models_rate_limited passed")

def test_is_retryable():
    assert ErrorClassifier.is_retryable(ErrorClassifier.RATE_LIMIT) == True
    assert ErrorClassifier.is_retryable(ErrorClassifier.UNAVAILABLE) == True
    assert ErrorClassifier.is_retryable(ErrorClassifier.NETWORK_ERROR) == True
    assert ErrorClassifier.is_retryable(ErrorClassifier.TIMEOUT) == True
    assert ErrorClassifier.is_retryable(ErrorClassifier.TPM_LIMIT_EXCEEDED) == True
    assert ErrorClassifier.is_retryable(ErrorClassifier.PROMPT_TOO_LARGE) == False
    assert ErrorClassifier.is_retryable(ErrorClassifier.AUTH_ERROR) == False
    print("test_is_retryable passed")

def test_is_reducible():
    assert ErrorClassifier.is_reducible(ErrorClassifier.PROMPT_TOO_LARGE) == True
    assert ErrorClassifier.is_reducible(ErrorClassifier.REQUEST_TOO_LARGE) == True
    assert ErrorClassifier.is_reducible(ErrorClassifier.TPM_LIMIT_EXCEEDED) == True
    assert ErrorClassifier.is_reducible(ErrorClassifier.RATE_LIMIT) == False
    print("test_is_reducible passed")

def test_should_quarantine():
    assert ErrorClassifier.should_quarantine_provider(ErrorClassifier.AUTH_ERROR) == True
    assert ErrorClassifier.should_quarantine_provider(ErrorClassifier.RATE_LIMIT) == False
    assert ErrorClassifier.should_quarantine_provider(ErrorClassifier.TIMEOUT) == False
    print("test_should_quarantine passed")

def test_should_failover():
    assert ErrorClassifier.should_failover(ErrorClassifier.RATE_LIMIT) == True
    assert ErrorClassifier.should_failover(ErrorClassifier.UNAVAILABLE) == True
    assert ErrorClassifier.should_failover(ErrorClassifier.NETWORK_ERROR) == True
    assert ErrorClassifier.should_failover(ErrorClassifier.TIMEOUT) == True
    # ALL_MODELS_RATE_LIMITED should NOT trigger failover - it means all models failed
    assert ErrorClassifier.should_failover(ErrorClassifier.ALL_MODELS_RATE_LIMITED) == False
    assert ErrorClassifier.should_failover(ErrorClassifier.AUTH_ERROR) == False
    print("test_should_failover passed")

if __name__ == "__main__":
    test_classify_prompt_too_large()
    test_classify_tpm_limit_exceeded()
    test_classify_daily_quota_exhausted()
    test_classify_request_too_large()
    test_classify_rate_limit()
    test_classify_auth_error()
    test_classify_unavailable()
    test_classify_timeout()
    test_classify_network_error()
    test_classify_all_models_rate_limited()
    test_is_retryable()
    test_is_reducible()
    test_should_quarantine()
    test_should_failover()
    print("\nAll error_classifier tests passed!")