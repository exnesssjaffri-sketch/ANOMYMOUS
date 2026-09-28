#!/usr/bin/env python3

import os
import json
from llmapi_adapter import LLMAPIAdapter
from transport import MockTransport
from orchestrator import Orchestrator

def test_mock_workflow():
    """
    Test the complete workflow using mock transport.
    """
    print("=== Testing Mock Workflow ===")
    
    # Setup mock transport
    from transport import MockTransport
    
    # Create a mock transport with predefined responses
    mock_transport = MockTransport({
        "Create a simple restaurant website with:": {
                "content": "{\"thought\": \"Creating a simple restaurant website.\", \"actions\": [{\"type\": \"create_file\", \"path\": \"restaurant/index.html\", \"content\": \"<html><body><h1>Welcome</h1></body></html>\", \"critical\": true}, {\"type\": \"create_file\", \"path\": \"restaurant/style.css\", \"content\": \"body { color: red; }\", \"critical\": true}]}"
            "choices": [
                {
                    "message": {
                        "content": "{\"thought\": \"Creating a simple restaurant website.\", \"actions\": [{\"type\": \"create_file\", \"path\": \"restaurant/index.html\", \"content\": \"<html><body><h1>Welcome</h1></body></html>\", \"critical\": true}, {\"type\": \"create_file\", \"path\": \"restaurant/style.css\", \"content\": \"body { color: red; }\", \"critical\": true}]}"
                    }
                }
            )
    })
    
    # Override the orchestrator's transport
    orchestrator = Orchestrator(
        provider="mock",
        model="mock-model",
        transport=mock_transport,  # Use the mock transport
        endpoint="http://mock-endpoint",
        api_key="dummy",
        workspace_dir=None
    )
    
    orchestrator = Orchestrator(
        provider="mock",
        model="mock-model",
        endpoint="http://mock-endpoint",
        api_key="dummy",
        workspace_dir=None
    )
    
    # Execute task
    task = "Create a simple restaurant website with:
            - index.html with title and basic content
            - style.css with simple styling"
    
    result = orchestrator.execute_task(task)
    
    print("\n--- Result ---")
    print(f"Status: {result['status']}")
    print(f"Verification Status: {result['verification']['status']}")
    
    # Check workspace
    workspace_path = os.path.join(os.getcwd(), "workspace", "restaurant")
    if os.path.exists(workspace_path):
        files = os.listdir(workspace_path)
        print(f"Files created in workspace: {files}")
        
        # Verify files
        if os.path.exists(os.path.join(workspace_path, "index.html")):
            with open(os.path.join(workspace_path, "index.html"), "r") as f:
                content = f.read()
                print(f"index.html content preview: {content[:100]}...")
        
        if os.path.exists(os.path.join(workspace_path, "style.css")):
            with open(os.path.join(workspace_path, "style.css"), "r") as f:
                content = f.read()
                print(f"style.css content preview: {content[:100]}...")
    else:
        print("Workspace directory not found!")
    
    return result

if __name__ == "__main__":
    test_mock_workflow()