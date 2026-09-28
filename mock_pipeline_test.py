# Mock task execution and verification
import os
import shutil
from task_classifier import TaskClassifier
from verification import TaskVerifier

workspace_name = "workspace_test"
if os.path.exists(workspace_name):
    shutil.rmtree(workspace_name)
os.makedirs(workspace_name)

classifier = TaskClassifier()
verifier = TaskVerifier(workspace_name)

website_task = "Create a simple restaurant website with HTML, CSS, and JavaScript."
api_task = "Build a Python API with Flask"

print("=== Website Task ===")
classification = classifier.classify(website_task)
os.makedirs(os.path.join(workspace_name, "restaurant"), exist_ok=True)
with open(os.path.join(workspace_name, "restaurant", "index.html"), "w") as f:
    f.write("<html><head><title>Restaurant</title></head><body><h1>Welcome</h1></body></html>")
verification_result = verifier.verify(classification, website_task)
print(f"Verification Result: {verification_result}")

print("\n=== API Task ===")
classification = classifier.classify(api_task)
with open(os.path.join(workspace_name, "api_app.py"), "w") as f:
    f.write('from flask import Flask\napp = Flask(__name__)\n@app.route("/")\ndef home():\n    return "Hello, World!"\nif __name__ == "__main__":\n    app.run()\n')
verification_result = verifier.verify(classification, api_task)
print(f"Verification Result: {verification_result}")

print("\nMock pipeline test completed.")
