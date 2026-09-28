import os
import sys
import json
import time
from typing import Dict, Any, Optional, Tuple
from transport import Transport, RealHTTPTransport, MockTransport
from token_estimator import estimate_payload_tokens, reduce_payload_tokens, can_fit_in_budget
from error_classifier import ErrorClassifier


class LLMAPIAdapter:
    def __init__(self, provider: str, model: str, transport: Transport, timeout: int = 30, max_tokens: int = 7000):
        self.provider = provider
        self.model = model
        self.transport = transport
        self.timeout = timeout
        self.max_tokens = max_tokens  # Pre-dispatch budget limit (tokens)
        self._reduced_request_used = False  # Track if we already tried reduction

    def send_request(self, task: str, system_prompt: Optional[str] = None) -> Dict[str, Any]:
        """
        Sends a task to the configured LLMAPI.
        Normalizes responses to the standard internal result contract.
        """
        start_time = time.time()
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": task})
        
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0,
            "response_format": {"type": "json_object"}
        }
        
        # PRE-DISPATCH BUDGET CHECK
        estimated_tokens = estimate_payload_tokens(payload)
        if estimated_tokens > self.max_tokens:
            reduced_payload = reduce_payload_tokens(payload, self.max_tokens)
            reduced_tokens = estimate_payload_tokens(reduced_payload)
            if reduced_tokens > self.max_tokens:
                return {
                    "status": "error",
                    "provider": self.provider,
                    "model": self.model,
                    "output": None,
                    "error": f"Request too large: estimated {estimated_tokens} tokens, max {self.max_tokens}. Reduction attempt resulted in {reduced_tokens} tokens, still exceeds limit.",
                    "error_type": "request_too_large",
                    "timed_out": False,
                    "duration": time.time() - start_time,
                    "request_id": None,
                    "attempt": 1,
                }
            payload = reduced_payload
            self._reduced_request_used = True
        
        try:
            response_data = self.transport.send_request(payload, self.timeout)
            duration = time.time() - start_time
            choices = response_data.get("choices", [])
            if not choices:
                raise Exception(f"No choices in LLM response: {json.dumps(response_data)}")
            content = choices[0].get("message", {}).get("content")
            request_id = response_data.get("id")
            return {
                "status": "success",
                "provider": self.provider,
                "model": self.model,
                "output": content,
                "error": None,
                "error_type": None,
                "timed_out": False,
                "duration": duration,
                "request_id": request_id,
                "attempt": 1,
            }
        except Exception as e:
            # Use ErrorClassifier for structured error classification
            error_class = ErrorClassifier.classify_exception(e)
            error_str = str(e)
            
            # Determine if we should retry/reduce based on error classification
            is_413 = error_class in (
                ErrorClassifier.PROMPT_TOO_LARGE,
                ErrorClassifier.TPM_LIMIT_EXCEEDED,
                ErrorClassifier.DAILY_QUOTA_EXHAUSTED,
                ErrorClassifier.REQUEST_TOO_LARGE,
            )
            
            # Set error_type based on classification
            error_type = error_class
            
            if is_413 and not self._reduced_request_used:
                reduced_payload = reduce_payload_tokens(payload, self.max_tokens)
                reduced_tokens = estimate_payload_tokens(reduced_payload)
                original_tokens = estimate_payload_tokens(payload)
                
                # Check if original payload fits in budget (not oversized)
                fits_in_budget = original_tokens <= self.max_tokens
                
                # Retry if:
                # 1. Reduction actually reduces tokens, OR
                # 2. Original payload fits in budget (transient 413 like TPM limit)
                # Don't retry if payload is oversized AND reduction doesn't help
                should_retry = (reduced_tokens < original_tokens) or fits_in_budget
                
                if should_retry:
                    self._reduced_request_used = True
                    try:
                        response_data = self.transport.send_request(reduced_payload, self.timeout)
                        duration = time.time() - start_time
                        choices = response_data.get("choices", [])
                        if not choices:
                            raise Exception(f"No choices in LLM response: {json.dumps(response_data)}")
                        content = choices[0].get("message", {}).get("content")
                        request_id = response_data.get("id")
                        return {
                            "status": "success",
                            "provider": self.provider,
                            "model": self.model,
                            "output": content,
                            "error": None,
                            "error_type": None,
                            "timed_out": False,
                            "duration": duration,
                            "request_id": request_id,
                            "attempt": 2,
                        }
                    except Exception as retry_error:
                        return {
                            "status": "error",
                            "provider": self.provider,
                            "model": self.model,
                            "output": None,
                            "error": f"413 retry failed: {str(retry_error)}",
                            "error_type": error_type,
                            "timed_out": False,
                            "duration": time.time() - start_time,
                            "request_id": None,
                            "attempt": 2,
                        }
            
            return {
                "status": "error",
                "provider": self.provider,
                "model": self.model,
                "output": None,
                "error": error_str,
                "error_type": error_type,
                "timed_out": False,
                "duration": time.time() - start_time,
                "request_id": None,
                "attempt": 1,
            }

