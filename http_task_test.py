import json
import requests
import os
import time

# Server details
server_url = "http://127.0.0.1:8000"

# Task to submit
task_text = """Create a simple restaurant website with:
- index.html
- style.css
- script.js"""

# Submit task via HTTP POST
response = requests.post(f"{server_url}/task", json={"task": task_text})
print(f"Task submission response: {response.status_code} - {response.json()}")

# Wait for task to complete (or check status periodically)
task_id = None
while task_id is None:
    time.sleep(1)
    status_response = requests.get(f"{server_url}/status")
    print(f"Current status: {status_response.json()}")
    if "status" in status_response.json() and status_response.json()["status"] == "accepted":
        task_id = status_response.json()["task_id"]

# Verify files are created in the workspace
workspace_dir = "workspace"
if os.path.exists(workspace_dir):
    files = os.listdir(workspace_dir)
    print(f"Files in workspace: {files}")
    
    # Check for expected files
    expected_files = ["restaurant/index.html", "restaurant/style.css", "restaurant/script.js"]
    for file_path in expected_files:
        if file_path in files:
            print(f"File {file_path} found!")
        else:
            print(f"File {file_path} NOT found!")
else:
    print(f"Workspace directory {workspace_dir} does not exist!")

# Verify the result
result_response = requests.get(f"{server_url}/status")
print(f"Final result: {result_response.json()}")