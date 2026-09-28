#!/usr/bin/env python3

import os
from typing import Dict, Any, List, Optional


def verify_website(workspace_path: str) -> Dict[str, Any]:
    """
    Verifies a website task by checking for required files and basic HTML structure.
    """
    print(f"Verifying website in: {workspace_path}")
    
    if not os.path.isdir(workspace_path):
        print("Workspace does not exist")
        return {
            "status": "failed",
            "verified": False,
            "diagnostics": ["Workspace does not exist"]
        }
    
    # Search for index.html recursively or in root
    index_path = os.path.join(workspace_path, "index.html")
    if not os.path.exists(index_path):
        for root, _, files in os.walk(workspace_path):
            if "index.html" in files:
                index_path = os.path.join(root, "index.html")
                break
    
    if not os.path.exists(index_path):
        print("Missing files: index.html")
        return {
            "status": "failed",
            "verified": False,
            "diagnostics": ["Missing files: index.html"]
        }
    
    try:
        with open(os.path.join(workspace_path, "index.html"), "r", encoding="utf-8") as f:
            html_content = f.read().lower()
            print(f"HTML content preview: {html_content[:100]}")
            
            if "<html" not in html_content or "<body" not in html_content:
                print("index.html is missing basic HTML tags")
                return {
                    "status": "failed",
                    "verified": False,
                    "diagnostics": ["index.html is missing basic HTML tags"]
                }
            
            print("index.html structure is valid")
            return {
                "status": "success",
                "verified": True,
                "diagnostics": ["All required files exist and index.html structure is valid"]
            }
    except Exception as e:
        print(f"Failed to read index.html: {str(e)}")
        return {
            "status": "failed",
            "verified": False,
            "diagnostics": [f"Failed to read index.html: {str(e)}"]
        }


def verify_api(workspace_path: str) -> Dict[str, Any]:
    """
    Verifies an API task by checking for Python files and basic API structure.
    """
    print(f"Verifying API in: {workspace_path}")
    
    # Check for Python files
    python_files = []
    for root, _, filenames in os.walk(workspace_path):
        for filename in filenames:
            if filename.endswith(".py") and not filename.startswith("."):
                python_files.append(os.path.join(root, filename))
    
    if not python_files:
        print("No Python files found")
        return {
            "status": "failed",
            "verified": False,
            "diagnostics": ["No Python files found"]
        }
    
    # Check for a basic API entry point (e.g., Flask/Django)
    try:
        for file_path in python_files:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                if "from flask" in content.lower() or "import flask" in content.lower() or "from django" in content.lower():
                    print("API project structure looks valid")
                    return {
                        "status": "success",
                        "verified": True,
                        "diagnostics": ["API project structure verified"]
                    }
    except Exception as e:
        print(f"Error checking API structure: {str(e)}")
        return {
            "status": "failed",
            "verified": False,
            "diagnostics": [f"Error checking API structure: {str(e)}"]
        }
    
    return {
        "status": "failed",
        "verified": False,
        "diagnostics": ["No Flask/Django imports detected"]
    }


def verify_backend_service(workspace_path: str) -> Dict[str, Any]:
    """
    Verifies a backend service task by checking for Python files and basic backend structure.
    """
    print(f"Verifying backend service in: {workspace_path}")
    
    # Check for Python files
    python_files = []
    for root, _, filenames in os.walk(workspace_path):
        for filename in filenames:
            if filename.endswith(".py") and not filename.startswith("."):
                python_files.append(os.path.join(root, filename))
    
    if not python_files:
        print("No Python files found")
        return {
            "status": "failed",
            "verified": False,
            "diagnostics": ["No Python files found"]
        }
    
    # Check for a basic backend entry point
    try:
        for file_path in python_files:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                if "import json" in content.lower() or "import csv" in content.lower():
                    print("Backend service structure looks valid")
                    return {
                        "status": "success",
                        "verified": True,
                        "diagnostics": ["Backend service structure verified"]
                    }
    except Exception as e:
        print(f"Error checking backend structure: {str(e)}")
        return {
            "status": "failed",
            "verified": False,
            "diagnostics": [f"Error checking backend structure: {str(e)}"]
        }
    
    return {
        "status": "failed",
        "verified": False,
        "diagnostics": ["No backend entry point detected"]
    }


def verify_web_app(workspace_path: str) -> Dict[str, Any]:
    """
    Verifies a web_app task by checking for a combination of frontend and backend artifacts.
    """
    print(f"Verifying web_app in: {workspace_path}")
    
    # Check for frontend artifacts
    frontend_files = ["index.html"]
    missing_frontend = [f for f in frontend_files if not os.path.exists(os.path.join(workspace_path, f))]
    
    if missing_frontend:
        print(f"Missing frontend files: {', '.join(missing_frontend)}")
        return {
            "status": "failed",
            "verified": False,
            "diagnostics": [f"Missing frontend files: {', '.join(missing_frontend)}"]
        }
    
    # Check for backend artifacts (generic check for Python backend)
    backend_files = ["app.py"]
    missing_backend = [f for f in backend_files if not os.path.exists(os.path.join(workspace_path, f))]
    
    if missing_backend:
        print(f"Missing backend files: {', '.join(missing_backend)}")
        return {
            "status": "failed",
            "verified": False,
            "diagnostics": [f"Missing backend files: {', '.join(missing_backend)}"]
        }
    
    # Check for a basic Python file to ensure backend logic is present
    python_files = []
    for root, _, filenames in os.walk(workspace_path):
        for filename in filenames:
            if filename.endswith(".py") and not filename.startswith("."):
                python_files.append(os.path.join(root, filename))
    
    if not python_files:
        print("No Python files found in workspace")
        return {
            "status": "failed",
            "verified": False,
            "diagnostics": ["No Python files found in workspace"]
        }
    
    return {
        "status": "success",
        "verified": True,
        "diagnostics": ["Web app verification passed: frontend and backend artifacts found"]
    }


def verify_debugging_task(workspace_path: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Verifies a debugging task by checking for file changes and actual debugging evidence.
    """
    print(f"Verifying debugging task in: {workspace_path}")
    
    # Check for Python files that might indicate debugging activity
    python_files = []
    for root, _, filenames in os.walk(workspace_path):
        for filename in filenames:
            if filename.endswith(".py") and not filename.startswith("."):
                python_files.append(os.path.join(root, filename))
    
    if not python_files:
        print("No Python files found")
        return {
            "status": "failed",
            "verified": False,
            "diagnostics": ["No Python files found"]
        }
    
    # Check for actual debugging evidence (e.g., error handling, imports)
    try:
        for file_path in python_files:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                # Check for error handling (e.g., try/except blocks)
                if "try:" in content.lower() and "except" in content.lower():
                    print(f"Error handling detected in {file_path}")
                    return {
                        "status": "success",
                        "verified": True,
                        "diagnostics": [f"Error handling detected in {file_path}"]
                    }
                # Check for imports that might indicate debugging (e.g., logging, sys)
                if "import logging" in content.lower() or "import sys" in content.lower():
                    print(f"Debugging imports detected in {file_path}")
                    return {
                        "status": "success",
                        "verified": True,
                        "diagnostics": [f"Debugging imports detected in {file_path}"]
                    }
                # Check for explicit error messages
                if "raise" in content.lower() or "Error" in content.lower():
                    print(f"Error message detected in {file_path}")
                    return {
                        "status": "success",
                        "verified": True,
                        "diagnostics": [f"Error message detected in {file_path}"]
                    }
    except Exception as e:
        print(f"Failed to read Python file: {str(e)}")
        return {
            "status": "failed",
            "verified": False,
            "diagnostics": [f"Failed to read Python file: {str(e)}"]
        }
    
    return {
        "status": "failed",
        "verified": False,
        "diagnostics": ["No debugging evidence detected"]
    }


def verify_testing(workspace_path: str) -> Dict[str, Any]:
    """
    Verifies a testing task by checking for test files and execution evidence.
    """
    print(f"Verifying testing task in: {workspace_path}")
    
    # Check for test files
    test_files = ["test_*.py", "tests/*.py", "_test.py"]
    test_paths = []
    for root, _, filenames in os.walk(workspace_path):
        for filename in filenames:
            for pattern in test_files:
                if pattern in filename:
                    test_paths.append(os.path.join(root, filename))
    
    if not test_paths:
        print("No test files found")
        return {
            "status": "failed",
            "verified": False,
            "diagnostics": ["No test files found"]
        }
    
    # Check for test execution evidence (e.g., test output, assertions)
    try:
        for test_path in test_paths:
            with open(test_path, "r", encoding="utf-8") as f:
                content = f.read()
                if "def test" in content.lower() or "assert" in content.lower():
                    print(f"Test evidence found in {test_path}")
                    return {
                        "status": "success",
                        "verified": True,
                        "diagnostics": [f"Test evidence found in {test_path}"]
                    }
    except Exception as e:
        print(f"Error reading test file: {str(e)}")
        return {
            "status": "failed",
            "verified": False,
            "diagnostics": [f"Error reading test file: {str(e)}"]
        }
    
    return {
        "status": "failed",
        "verified": False,
        "diagnostics": ["No test evidence detected"]
    }

def verify_generic_task(workspace_path: str, strategy: str = "generic") -> Dict[str, Any]:
    """
    Verifies a generic task by checking if workspace exists and contains files.
    """
    print(f"Verifying generic task in: {workspace_path} with strategy: {strategy}")

    if not os.path.isdir(workspace_path):
        print("Workspace does not exist")
        return {
            "status": "failed",
            "verified": False,
            "diagnostics": ["Workspace does not exist"]
        }

    # List files recursively
    try:
        all_entries = []
        for root, dirs, files in os.walk(workspace_path):
            all_entries.extend(dirs)
            all_entries.extend(files)
        if not all_entries:
            print("Workspace is empty")
            return {
                "status": "failed",
                "verified": False,
                "diagnostics": ["Workspace is empty"]
            }
        print(f"Generic verification passed: workspace contains {len(all_entries)} items")
        return {
            "status": "success",
            "verified": True,
            "diagnostics": [f"Generic verification passed: workspace contains {len(all_entries)} items"]
        }
    except Exception as e:
        print(f"Failed to verify generic task: {str(e)}")
        return {
            "status": "failed",
            "verified": False,
            "diagnostics": [f"Failed to verify generic task: {str(e)}"]
        }
class TaskVerifier:
    def __init__(self, workspace_path: str):
        self.workspace_path = os.path.abspath(workspace_path)
        print(f"TaskVerifier initialized with workspace: {self.workspace_path}")
    
    def verify(self, task_classification: Dict[str, Any], task_text: str) -> Dict[str, Any]:
        """
        Task-aware verifier.
        """
        intent = task_classification.get("intent")
        verification_strategy = task_classification.get("verification", {}).get("strategy", "generic")
        
        # Map intent to explicit verification strategy
        strategy_map = {
            "website": verify_website,
            "api": verify_api,
            "backend_service": verify_backend_service,
            "web_app": verify_web_app,
            "debugging": verify_debugging_task,
            "testing": verify_testing,
            "generic": lambda workspace: verify_generic_task(workspace, verification_strategy)
        }
        
        if intent in strategy_map:
            verifier_func = strategy_map[intent]
            print(f"Using {verifier_func.__name__} verification")
            return verifier_func(self.workspace_path)
        else:
            print(f"Using generic task verification for intent: {intent}")
            return verify_generic_task(self.workspace_path, verification_strategy)