#!/usr/bin/env python3

import os
import json
import sys
from orchestrator import Orchestrator
from transport import MockTransport

def test_restaurant_website_task():
    """Test creating a restaurant website with index.html, style.css, and script.js."""
    
    # Setup workspace
    workspace_dir = os.path.join(os.getcwd(), "restaurant")
    os.makedirs(workspace_dir, exist_ok=True)
    
    # Mock transport with structured response
    mock_transport = MockTransport({
        "Create a simple restaurant website with:": {
            "output": json.dumps({
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
                ]
            })
        }
    })
    
    # Orchestrator setup
    orchestrator = Orchestrator(
        provider="mock",
        model="mock-model",
        transport=mock_transport,
        endpoint="http://localhost:8000",
        api_key="mock-key",
        workspace_dir=workspace_dir
    )
    
    # Execute task
    task = "Create a simple restaurant website"
    result = orchestrator.execute_task(task)
    
    # Debug: Print the full result structure
    print("=== Full Result ===")
    print(f"Status: {result['status']}")
    print(f"Verification: {result.get('verification', 'NOT FOUND')}")
    
    # Check if files exist and are non-empty
    for f in ["index.html", "style.css", "script.js"]:
        path = os.path.join(workspace_dir, f)
        if os.path.exists(path) and os.path.getsize(path) > 0:
            print(f"✓ {f} exists and is non-empty")
        else:
            print(f"X {f} issue")
    
    # Exit with error if verification is not captured
    if result.get('verification') is None:
        print("❌ Verification result is None!")
        sys.exit(1)

if __name__ == "__main__":
    test_restaurant_website_task()