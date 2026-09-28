#!/usr/bin/env python3
"""
Integration test for ANOMYMOUS server.
This script tests the actual server implementation by:
1. Starting the server as a child process.
2. Sending HTTP requests to the server.
3. Validating responses.
"""

import os
import sys
# Add the project root to the path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Global variables to store server process and test results
test_results = {
    "health": None,
    "status": None,
    "static": None,
    "traversal": None,
    "workspace_files": None
}
def start_server():
    """Start the ANOMYMOUS server as a child process."""
    server_process = subprocess.Popen(
        ["python", "server.py"],
        stdout=subprocess.PIPE,
def wait_for_server(port=8000, timeout=10):
    """Wait for the server to be ready."""
    start_time = time.time()
    while time.time() - start_time < timeout:
    while time.time() - start_time < timeout:
        try:
            urllib.request.urlopen("http://127.0.0.1:{}/health".format(port), timeout=2)
            return True
        except urllib.error.URLError:
def test_health_endpoint():
    """Test the /health endpoint."""
    try:
        response = urllib.request.urlopen("http://127.0.0.1:8000/health")
        data = json.loads(response.read().decode())
        test_results["health"] = {
            "status": response.getcode(),
            "body": data
def test_status_endpoint():
    """Test the /status endpoint."""
    try:
        response = urllib.request.urlopen("http://127.0.0.1:8000/status")
        data = json.loads(response.read().decode())
        test_results["status"] = {
            "status": response.getcode(),
            "body": data
def test_static_endpoint():
    """Test the /static endpoint."""
    try:
        response = urllib.request.urlopen("http://127.0.0.1:8000/static/index.html")
        data = response.read().decode()
        test_results["static"] = {
            "status": response.getcode(),
            "body": data[:200] + "..."
def test_traversal_attempt():
    """Test traversal attempt on /static endpoint."""
    try:
        response = urllib.request.urlopen("http://127.0.0.1:8000/static/../server.py")
        data = response.read().decode()
        test_results["traversal"] = {
            "status": response.getcode(),
            "body": data
        }
        print("Traversal test failed: Expected 403 Forbidden.")
    except urllib.error.HTTPError as e:
        if e.code == 403:
            test_results["traversal"] = {
def test_task_submission():
    """Test submitting a task to /task."""
    task_text = "Create a simple restaurant website with:\n- index.html\n- style.css\n- script.js"
    
    try:
        data = json.dumps({"task": task_text}).encode()
        req = urllib.request.Request("http://127.0.0.1:8000/task",
                                    data=data,
                                    method='POST')
        req.add_header('Content-Type', 'application/json')
        
        response = urllib.request.urlopen(req)
        data = json.loads(response.read().decode())
def verify_workspace_files():
    """Verify that workspace files were created."""
    workspace_files = [
        "workspace/restaurant/index.html",
        "workspace/restaurant/style.css",
        "workspace/restaurant/script.js"
    ]
    
def cleanup_server(server_process):
    """Terminate the server process."""
    server_process.terminate()
def main():
    """Run integration tests."""
    print("Starting ANOMYMOUS server...")
    server_process = start_server()
    
    if not wait_for_server():
        print("Failed to start server.")
        return
    
    print("Server started. Running tests...")
    
    # Run tests
    test_health_endpoint()
    test_status_endpoint()
    test_static_endpoint()
    test_traversal_attempt()
    test_task_submission()
    verify_workspace_files()
    
    # Cleanup
    cleanup_server(server_process)
    
    # Print results
    print("\n=== Test Results ===")
    for test_name, result in test_results.items():
        print(f"{test_name}: {result}")

if __name__ == "__main__":
    main()
    server_process.wait()
    print("Server process terminated.")
    file_status = {}
    for file_path in workspace_files:
        if os.path.exists(file_path):
            file_status[file_path] = "exists"
        else:
            file_status[file_path] = "missing"
    
    test_results["workspace_files"] = file_status
    print(f"Workspace files verification: {file_status}")
        
        test_results["task_submission"] = {
            "status": response.getcode(),
            "body": data
        }
        print("Task submission test passed.")
    except Exception as e:
        test_results["task_submission"] = {
            "error": str(e)
        }
        print(f"Task submission test failed: {e}")
                "status": e.code,
                "body": "Forbidden: Traversal attempt detected"
            }
            print("Traversal test passed.")
        else:
            test_results["traversal"] = {
                "error": f"Unexpected error: {e}"
            }
            print(f"Traversal test failed: {e}")
    except Exception as e:
        test_results["traversal"] = {
            "error": str(e)
        }
        print(f"Traversal test failed: {e}")
        }
        print("Static endpoint test passed.")
    except Exception as e:
        test_results["static"] = {
            "error": str(e)
        }
        print(f"Static endpoint test failed: {e}")
        }
        print("Status endpoint test passed.")
    except Exception as e:
        test_results["status"] = {
            "error": str(e)
        }
        print(f"Status endpoint test failed: {e}")
        }
        print("Health endpoint test passed.")
    except Exception as e:
        test_results["health"] = {
            "error": str(e)
        }
        print(f"Health endpoint test failed: {e}")
            time.sleep(0.5)
    return False
        stderr=subprocess.PIPE,
        cwd=os.getcwd()
    )
    return server_process


import json
import subprocess
import time
import urllib.request
import urllib.error
