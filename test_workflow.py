#!/usr/bin/env python3
import os
import json
import sys
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from transport import MockTransport
from orchestrator import Orchestrator

def test_mock_workflow():
    print("=== Testing Mock Workflow ===")
    mock_responses = {
        "Create a simple restaurant website with:": {
            "choices": [{
                "message": {
                    "content": json.dumps({
                        "thought": "Creating a simple restaurant website.",
                        "actions": [
                            {"type": "create_file", "path": "restaurant/index.html", "content": "<html><body><h1>Welcome</h1></body></html>", "critical": True},
                            {"type": "create_file", "path": "restaurant/style.css", "content": "body { color: red; }", "critical": True}
                        ]
                    })
                }
            }],
            "id": "mock-req-123"
        }
    }
    mock_transport = MockTransport(mock_responses)
    orchestrator = Orchestrator(
        provider="mock",
        model="mock-model",
        transport=mock_transport,
        endpoint="http://mock-endpoint",
        api_key="dummy",
        workspace_dir=os.path.join(os.getcwd(), "workspace")
    )
    task = "Create a simple restaurant website with:"
    result = orchestrator.execute_task(task)
    print(f"\n--- Result ---")
    print(f"Status: {result['status']}")
    print(f"Verification: {result.get('verification', {}).get('status')}")
    return result

if __name__ == "__main__":
    test_mock_workflow()
