# Simple verification logic test
import os
import shutil
from task_classifier import TaskClassifier
from verification import TaskVerifier

# Create a test workspace
workspace_name = "workspace_test"
if os.path.exists(workspace_name):
    shutil.rmtree(workspace_name)
os.makedirs(workspace_name)

# Task classifier and verifier
classifier = TaskClassifier()
verifier = TaskVerifier(workspace_name)

# Example tasks
website_task = "Create a simple restaurant website with HTML, CSS, and JavaScript."
api_task = "Build a Python API with Flask"
web_app_task = "Build a full-stack inventory dashboard"
debug_task = "Fix a Python import error"

# Classify and verify website task
print("=== Website Task ===")
classification = classifier.classify(website_task)
print(f"Classification: {classification}")

# Simulate workspace changes for website
os.makedirs(os.path.join(workspace_name, "restaurant"), exist_ok=True)
with open(os.path.join(workspace_name, "restaurant", "index.html"), "w") as f:
    f.write("<html><head><title>Test</title></head><body><h1>Test Page</h1></body></html>")

verification_result = verifier.verify(classification, website_task)
print(f"Website Verification Result: {verification_result}")

# Classify and verify API task
print("\n=== API Task ===")
classification = classifier.classify(api_task)
print(f"Classification: {classification}")

# Simulate workspace changes for API
os.makedirs(os.path.join(workspace_name, "api"), exist_ok=True)
with open(os.path.join(workspace_name, "api", "app.py"), "w") as f:
    f.write("""
from flask import Flask
app = Flask(__name__)
@app.route('/')
def home():
    return 'Hello, World!'
""")

verification_result = verifier.verify(classification, api_task)
print(f"API Verification Result: {verification_result}")

# Classify and verify debugging task
print("\n=== Debugging Task ===")
classification = classifier.classify(debug_task)
print(f"Classification: {classification}")

# Simulate workspace changes for debugging
with open(os.path.join(workspace_name, "fix_import.py"), "w") as f:
    f.write("import sys\nimport logging\nlogging.basicConfig(level=logging.INFO)")

verification_result = verifier.verify(classification, debug_task)
print(f"Debugging Verification Result: {verification_result}")

# Classify and verify web_app task
print("\n=== Web App Task ===")
classification = classifier.classify(web_app_task)
print(f"Classification: {classification}")

# Simulate workspace changes for web_app
os.makedirs(os.path.join(workspace_name, "app"), exist_ok=True)
os.makedirs(os.path.join(workspace_name, "restaurant"), exist_ok=True)
with open(os.path.join(workspace_name, "restaurant", "index.html"), "w") as f:
    f.write("<html><head><title>Restaurant</title></head><body><h1>Welcome</h1></body></html>")
os.makedirs(os.path.join(workspace_name, "api"), exist_ok=True)
os.makedirs(os.path.join(workspace_name, "api", "static"), exist_ok=True)
with open(os.path.join(workspace_name, "api", "app.py"), "w") as f:
    f.write("""
from flask import Flask
app = Flask(__name__)
@app.route('/')
def home():
    return 'Hello, World!'
""")

# Directly call the verifier for web_app task
web_app_verification_result = verifier.verify(classification, web_app_task)
print(f"Web App Verification Result: {web_app_verification_result}")

print("\nVerification tests completed.")