#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.path.abspath('.'))

# Test imports
try:
    from task_classifier import TaskClassifier
    print("TaskClassifier imported successfully")
except ImportError as e:
    print(f"Failed to import TaskClassifier: {e}")

try:
    from verification import verify_website, verify_api, verify_backend_service, verify_debugging_task, verify_testing, verify_web_app, verify_generic_task
    print("Verification functions imported successfully")
except ImportError as e:
    print(f"Failed to import verification functions: {e}")

try:
    from orchestrator import Orchestrator
    print("Orchestrator imported successfully")
except ImportError as e:
    print(f"Failed to import Orchestrator: {e}")

print("\nTest completed.")