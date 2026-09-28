# Simple verification logic test
import os
import shutil
from task_classifier import TaskClassifier
from verification import verify_website, verify_api, verify_web_app, verify_debugging_task

# Create a test workspace
workspace_name = "workspace_test"
if os.path.exists(workspace_name):
    shutil.rmtree(workspace_name)
os.makedirs(workspace_name)

# Test website verification
print("Testing website verification...")
website_path = os.path.join(workspace_name, "restaurant")
os.makedirs(website_path, exist_ok=True)
with open(os.path.join(website_path, "index.html"), "w") as f:
    f.write("<html><head><title>Test</title></head><body><h1>Test Page</h1></body></html>")

website_verification = verify_website(website_path)
print(f"Website Verification: {website_verification}")

# Test API verification
print("\nTesting API verification...")
api_path = workspace_name
os.makedirs(api_path, exist_ok=True)
with open(os.path.join(api_path, "app.py"), "w") as f:
    f.write("""
from flask import Flask
app = Flask(__name__)
@app.route('/')
def home():
    return 'Hello, World!'
""")

api_verification = verify_api(api_path)
print(f"API Verification: {api_verification}")

# Test web_app verification
print("\nTesting web_app verification...")
web_app_path = workspace_name
os.makedirs(os.path.join(web_app_path, "restaurant"), exist_ok=True)
os.makedirs(os.path.join(web_app_path, "api"), exist_ok=True)
with open(os.path.join(web_app_path, "restaurant", "index.html"), "w") as f:
    f.write("<html><head><title>Restaurant</title></head><body><h1>Welcome</h1></body></html>")
os.makedirs(os.path.join(web_app_path, "api", "static"), exist_ok=True)
with open(os.path.join(web_app_path, "api", "app.py"), "w") as f:
    f.write("""
from flask import Flask
app = Flask(__name__)
@app.route('/')
def home():
    return 'Hello, World!'
""")

web_app_verification = verify_web_app(web_app_path)
print(f"Web App Verification: {web_app_verification}")

# Test debugging verification
print("\nTesting debugging verification...")
debug_path = workspace_name
with open(os.path.join(debug_path, "fix.py"), "w") as f:
    f.write("import sys\nimport logging\nlogging.basicConfig(level=logging.INFO)")

debug_verification = verify_debugging_task(debug_path)
print(f"Debugging Verification: {debug_verification}")

print("\nVerification tests completed.")