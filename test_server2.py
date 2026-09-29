import subprocess
import time
import requests
import sys

# Start server
server_process = subprocess.Popen([
    r"C:\Users\ALI HAIDER\AppData\Local\Programs\Python\Python313\python.exe",
    r"C:\Users\ALI HAIDER\OneDrive\Desktop\ANOMYMOUS\server.py"
], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

print("Server started, waiting for startup...")
time.sleep(3)

# Test endpoints
endpoints = ["/health", "/providers", "/analytics", "/status"]
for ep in endpoints:
    try:
        resp = requests.get(f"http://127.0.0.1:8000{ep}", timeout=5)
        print(f"GET {ep}: {resp.status_code}")
        print(resp.json())
    except Exception as e:
        print(f"GET {ep}: ERROR - {e}")

# Test POST /task
try:
    resp = requests.post("http://127.0.0.1:8000/task", json={"task": "Create a simple website"}, timeout=10)
    print(f"POST /task: {resp.status_code}")
    print(resp.json())
except Exception as e:
    print(f"POST /task: ERROR - {e}")

# Wait for background task to complete
print("Waiting for background task...")
time.sleep(5)

# Check status
try:
    resp = requests.get("http://127.0.0.1:8000/status", timeout=5)
    print(f"GET /status (after task): {resp.status_code}")
    print(resp.json())
except Exception as e:
    print(f"GET /status (after task): ERROR - {e}")

# Test malformed /task
try:
    resp = requests.post("http://127.0.0.1:8000/task", json={}, timeout=5)
    print(f"POST /task (malformed): {resp.status_code}")
    print(resp.json())
except Exception as e:
    print(f"POST /task (malformed): ERROR - {e}")

# Shutdown
server_process.terminate()
server_process.wait(timeout=5)
print("Server stopped")

# Print any stdout/stderr
stdout, stderr = server_process.communicate()
if stdout:
    print("STDOUT:", stdout.decode())
if stderr:
    print("STDERR:", stderr.decode())