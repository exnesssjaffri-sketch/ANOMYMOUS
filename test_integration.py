#!/usr/bin/env python3
import os
import sys
import json
import subprocess
import time
import urllib.request
import urllib.error

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

test_results = {
    "health": None,
    "status": None,
    "static": None,
    "traversal": None,
    "workspace_files": None
}

def start_server():
    server_process = subprocess.Popen(
        [sys.executable, "server.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=os.getcwd()
    )
    return server_process

def wait_for_server(port=8000, timeout=10):
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            urllib.request.urlopen("http://127.0.0.1:{}/health".format(port), timeout=2)
            return True
        except urllib.error.URLError:
            time.sleep(0.5)
    return False

def test_health_endpoint():
    try:
        response = urllib.request.urlopen("http://127.0.0.1:8000/health")
        data = json.loads(response.read().decode())
        test_results["health"] = {"status": response.getcode(), "body": data}
        print("Health endpoint test passed.")
    except Exception as e:
        test_results["health"] = {"error": str(e)}
        print(f"Health endpoint test failed: {e}")

def test_status_endpoint():
    try:
        response = urllib.request.urlopen("http://127.0.0.1:8000/status")
        data = json.loads(response.read().decode())
        test_results["status"] = {"status": response.getcode(), "body": data}
        print("Status endpoint test passed.")
    except Exception as e:
        test_results["status"] = {"error": str(e)}
        print(f"Status endpoint test failed: {e}")

def test_static_endpoint():
    try:
        response = urllib.request.urlopen("http://127.0.0.1:8000/static/index.html")
        data = response.read().decode()
        test_results["static"] = {"status": response.getcode(), "body": data[:100]}
        print("Static endpoint test passed.")
    except Exception as e:
        test_results["static"] = {"error": str(e)}
        print(f"Static endpoint test failed: {e}")

def test_traversal_attempt():
    try:
        req = urllib.request.Request("http://127.0.0.1:8000/static/../server.py")
        response = urllib.request.urlopen(req)
        print("Traversal test failed: Expected 403 Forbidden.")
    except urllib.error.HTTPError as e:
        if e.code == 403:
            test_results["traversal"] = {"status": e.code, "body": "Forbidden"}
            print("Traversal test passed.")
        else:
            print(f"Traversal test failed: {e}")
    except Exception as e:
        print(f"Traversal test failed: {e}")

def main():
    print("Starting ANOMYMOUS server...")
    server_process = start_server()
    try:
        if not wait_for_server():
            print("Failed to start server.")
            return
        test_health_endpoint()
        test_status_endpoint()
        test_static_endpoint()
        test_traversal_attempt()
    finally:
        server_process.terminate()
    print("\n=== Test Results ===")
    print(test_results)

if __name__ == '__main__':
    main()
