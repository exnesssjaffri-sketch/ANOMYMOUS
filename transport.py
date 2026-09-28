import abc
import json
import time
import requests
from typing import Dict, Any, Optional

class Transport(abc.ABC):
    @abc.abstractmethod
    def send_request(self, payload: Dict[str, Any], timeout: int) -> Dict[str, Any]:
        pass

class MockTransport(Transport):
    def __init__(self, responses: Optional[Dict[str, Any]] = None):
        self.responses = responses or {}

    def send_request(self, payload: Dict[str, Any], timeout: int) -> Dict[str, Any]:
        # Simple mock response based on task if available, or generic
        task = payload.get("messages", [{}])[-1].get("content", "")
        
        # Look for a specific mock response if provided
        if task in self.responses:
            return self.responses[task]
            
        # Return a structured response with choices
        return {
            "choices": [
                {
                    "message": {
                        "content": json.dumps({
                            "thought": "Creating a restaurant website.",
                            "actions": [
                                {
                                    "type": "create_file",
                                    "path": "restaurant/index.html",
                                    "content": "<html><head><title>Restaurant</title></head><body><h1>Welcome</h1></body></html>",
                                    "critical": True
                                },
                                {
                                    "type": "create_file",
                                    "path": "restaurant/style.css",
                                    "content": "body { color: red; font-family: Arial; }",
                                    "critical": True
                                },
                                {
                                    "type": "create_file",
                                    "path": "restaurant/script.js",
                                    "content": "console.log('Restaurant site loaded!');",
                                    "critical": True
                                }
                            ]
                        })
                    }
                }
            ],
            "id": "mock-req-123"
        }

class RealHTTPTransport(Transport):
    def __init__(self, endpoint: str, api_key: str):
        self.endpoint = endpoint
        self.api_key = api_key

    def send_request(self, payload: Dict[str, Any], timeout: int) -> Dict[str, Any]:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        try:
            response = requests.post(
                self.endpoint,
                json=payload,
                headers=headers,
                timeout=timeout
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            error_body = ""
            if e.response:
                try:
                    error_body = e.response.json()
                except Exception:
                    error_body = e.response.text
            # Preserve error details in exception for 413 handling
            raise Exception(f"HTTP Error {e.response.status_code}: {json.dumps(error_body)}")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Transport Error: {str(e)}")
