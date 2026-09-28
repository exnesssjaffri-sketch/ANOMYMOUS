#!/usr/bin/env python3
"""
Error classifier for LLM API responses.

Classifies HTTP errors and exceptions into structured failure categories
for routing, retry, and failover decisions.

Failure taxonomy:
    - prompt_too_large: 413 with prompt_too_large type
    - tpm_limit_exceeded: 413 with tpm_limit_exceeded type
    - daily_quota_exhausted: 413 with daily_quota_exhausted type
    - request_too_large: 413 with no specific type
    - rate_limit: 429
    - auth_error: 401/403
    - unavailable: 503
    - network_error: transport-level failures
    - timeout: request timeout
    - malformed_response: invalid JSON or missing fields
    - unknown: unclassified errors
"""

import re
from typing import Dict, Any, Optional, Tuple


class ErrorClassifier:
    """Classify LLM API errors into structured categories."""

    # Error categories
    PROMPT_TOO_LARGE = "prompt_too_large"
    TPM_LIMIT_EXCEEDED = "tpm_limit_exceeded"
    DAILY_QUOTA_EXHAUSTED = "daily_quota_exhausted"
    REQUEST_TOO_LARGE = "request_too_large"
    RATE_LIMIT = "rate_limit"
    AUTH_ERROR = "auth_error"
    UNAVAILABLE = "unavailable"
    NETWORK_ERROR = "network_error"
    TIMEOUT = "timeout"
    MALFORMED_RESPONSE = "malformed_response"
    ALL_MODELS_RATE_LIMITED = "all_models_rate_limited"
    UNKNOWN = "unknown"

    # Retryable categories (can retry with backoff)
    RETRYABLE = {
        "rate_limit",
        "unavailable",
        "network_error",
        "timeout",
        "tpm_limit_exceeded",
    }

    # Categories that should trigger payload reduction
    REDUCIBLE = {
        "prompt_too_large",
        "request_too_large",
        "tpm_limit_exceeded",
    }

    @classmethod
    def classify_exception(cls, error: Exception) -> str:
        """Classify an exception into an error category."""
        error_str = str(error)
        return cls.classify_error_string(error_str)

    @classmethod
    def classify_error_string(cls, error_str: str) -> str:
        """Classify an error string into a category.

        Provider error text and provider-provided limits are authoritative.
        We check for specific error type patterns BEFORE generic HTTP status codes.
        """
        error_lower = error_str.lower()

        # Check for specific error types FIRST (before generic HTTP status codes)
        if "all_models_rate_limited" in error_lower or "all models rate limited" in error_lower:
            return cls.ALL_MODELS_RATE_LIMITED

        if "prompt_too_large" in error_lower:
            return cls.PROMPT_TOO_LARGE

        if "tpm_limit_exceeded" in error_lower:
            return cls.TPM_LIMIT_EXCEEDED

        if "daily_quota_exhausted" in error_lower:
            return cls.DAILY_QUOTA_EXHAUSTED

        # Groq-style TPM limit: "TPM Limit 8000 Requested 11401"
        # This is a 413 with TPM-specific text, must classify as tpm_limit_exceeded
        if "tpm limit" in error_lower or "tpm_limit" in error_lower:
            if "413" in error_str:
                return cls.TPM_LIMIT_EXCEEDED

        # Groq-style rate limit: "Rate limit exceeded" or "RPM limit"
        if "rate limit" in error_lower or "rpm limit" in error_lower:
            if "429" in error_str:
                return cls.RATE_LIMIT

        # Check for HTTP status codes
        if "413" in error_str or "http error 413" in error_lower:
            return cls.REQUEST_TOO_LARGE

        if "429" in error_str or "http error 429" in error_lower:
            return cls.RATE_LIMIT

        if "401" in error_str or "403" in error_str or "http error 401" in error_lower or "http error 403" in error_lower:
            return cls.AUTH_ERROR

        if "503" in error_str or "http error 503" in error_lower or "service unavailable" in error_lower:
            return cls.UNAVAILABLE

        if "timeout" in error_lower or "timed out" in error_lower:
            return cls.TIMEOUT

        if "network" in error_lower or "connection" in error_lower or "transport error" in error_lower:
            return cls.NETWORK_ERROR

        if "malformed" in error_lower or "no choices" in error_lower or "invalid json" in error_lower:
            return cls.MALFORMED_RESPONSE

        return cls.UNKNOWN

    @classmethod
    def is_retryable(cls, category: str) -> bool:
        """Check if an error category is retryable."""
        return category in cls.RETRYABLE

    @classmethod
    def is_reducible(cls, category: str) -> bool:
        """Check if an error category indicates the request can be reduced."""
        return category in cls.REDUCIBLE

    @classmethod
    def get_http_status(cls, category: str) -> Optional[int]:
        """Get the HTTP status code associated with a category."""
        status_map = {
            cls.PROMPT_TOO_LARGE: 413,
            cls.TPM_LIMIT_EXCEEDED: 413,
            cls.DAILY_QUOTA_EXHAUSTED: 413,
            cls.REQUEST_TOO_LARGE: 413,
            cls.RATE_LIMIT: 429,
            cls.AUTH_ERROR: 403,
            cls.UNAVAILABLE: 503,
        }
        return status_map.get(category)

    @classmethod
    def should_quarantine_provider(cls, category: str) -> bool:
        """Check if a provider should be quarantined for this error."""
        # Only quarantine for auth errors and permanent failures
        return category in (cls.AUTH_ERROR,)

    @classmethod
    def should_failover(cls, category: str) -> bool:
        """Check if failover to another provider/model is appropriate."""
        return category in (
            cls.RATE_LIMIT,
            cls.UNAVAILABLE,
            cls.NETWORK_ERROR,
            cls.TIMEOUT,
            cls.ALL_MODELS_RATE_LIMITED,
        )