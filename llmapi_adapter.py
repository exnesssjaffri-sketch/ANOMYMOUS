import os
import sys
import json
import time
from typing import Dict, Any, Optional
from transport import Transport, RealHTTPTransport, MockTransport

class LLMAPIAdapter:
    def __init__(self, provider: str, model: str, transport: Transport, timeout: int = 30):
        self.provider = provider
        self.model = model
        self.transport = transport
        self.timeout = timeout

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
            # We assume the model supports json_object if we want structured actions
            # Some models might need this in the prompt instead
            "response_format": { "type": "json_object" }
        }
        
        try:
            response_data = self.transport.send_request(payload, self.timeout)
            
            duration = time.time() - start_time
            
            # OpenAI-compatible parsing
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
            return {
                "status": "error",
                "provider": self.provider,
                "model": self.model,
                "output": None,
                "error": str(e),
                "error_type": "provider_error",
                "timed_out": False,
                "duration": time.time() - start_time,
                "request_id": None,
                "attempt": 1,
            }

