#!/usr/bin/env python3

import os
import subprocess

# Common project indicators
PROJECT_INDICATORS = {
    "Node.js": ["package.json", "pnpm-lock.yaml", "yarn.lock", "package-lock.json"],
    "Python": ["requirements.txt", "pyproject.toml", "setup.py"],
    "Rust": ["Cargo.toml"],
    "Go": ["go.mod"],
    "PHP": ["composer.json"],
    "Ruby": ["Gemfile"],
    "Java": ["pom.xml", "build.gradle"],
    "Static Website": ["index.html", "index.htm"],
    "Git Repository": [".git"],
}

# Current working directory
CURRENT_DIR = os.getcwd()

# Detect workspace
workspace_path = os.path.abspath(CURRENT_DIR)

# Check if the directory is a Git repository
def is_git_repo(path):
    try:
        subprocess.run(["git", "rev-parse", "--is-inside-work-tree"], 
                       cwd=path, check=True, capture_output=True)
        return True
    except subprocess.CalledProcessError:
        return False

def detect_project_type(path):
    files = os.listdir(path)
    project_type = "Generic Project"
    
    # Check for Git repository
    if is_git_repo(path):
        project_type = "Git Repository"
    
    # Check for project-specific files
    for project, indicators in PROJECT_INDICATORS.items():
        if project == "Git Repository":
            continue  # Already checked
        if any(indicator in files for indicator in indicators):
            project_type = project
            break
    
    # Check for static website
    if "index.html" in files or "index.htm" in files:
        if project_type == "Generic Project":
            project_type = "Static Website"
    
    # Ensure non-Git repositories are handled correctly
    if project_type == "Generic Project" and not is_git_repo(path):
        # Check for static website again if not a Git repo
        if "index.html" in files or "index.htm" in files:
            project_type = "Static Website"
    
    return project_type

def get_package_manager(path):
    files = os.listdir(path)
    if "package.json" in files:
        return "npm"
    elif "yarn.lock" in files:
        return "yarn"
    elif "pnpm-lock.yaml" in files:
        return "pnpm"
    else:
        return "None"

# Main detection logic
def detect_workspace():
    workspace_info = {
        "workspace_path": workspace_path,
        "project_type": detect_project_type(workspace_path),
        "is_git_repo": is_git_repo(workspace_path),
        "package_manager": get_package_manager(workspace_path),
    }
    return workspace_info

if __name__ == "__main__":
    workspace_info = detect_workspace()
    print(f"Workspace: {workspace_info['workspace_path']}")
    print(f"Project Type: {workspace_info['project_type']}")
    print(f"Git: {'available' if workspace_info['is_git_repo'] else 'unavailable'}")
    print(f"Package Manager: {workspace_info['package_manager']}")
# Import necessary modules
import sys
sys.path.insert(0, os.path.abspath("c:\Users\ALI HAIDER\OneDrive\Desktop\ANOMYMOUS"))

from task_classifier import classify_task

# Orchestration logic
def orchestrate_task(task_description, workspace_info):
    try:
        # Classify the task
        task_classification = classify_task(task_description)
        print(f"Task Classification: {task_classification}")
        
        # Detect and manage workers
        from worker_registry import detect_workers
        detect_workers()
        
        # Select the best worker
        from worker_router import select_best_worker
        best_worker = select_best_worker(task_classification)
        print(f"Best Worker: {best_worker}")
        
        # Simulate verification
        from verification import verify_website
        verification_results = verify_website(workspace_info['workspace_path'])
        print(f"Verification Results: {verification_results}")
        
        if all(verification_results.values()):
            return "STATUS: VERIFIED"
        else:
            return "STATUS: NOT VERIFIED"
    except ValueError as e:
        print(f"Error: {e}")
        return "STATUS: FAILED"

if __name__ == "__main__":
    workspace_info = detect_workspace()
    print(f"Workspace: {workspace_info['workspace_path']}")
    print(f"Project Type: {workspace_info['project_type']}")
    print(f"Git: {'available' if workspace_info['is_git_repo'] else 'unavailable'}")
    print(f"Package Manager: {workspace_info['package_manager']}")
    
    # Example task
    task_description = "Build a simple website"
    status = orchestrate_task(task_description, workspace_info)
    print(f"Status: {status}")
# Real website verification logic
def verify_website(path):
    files = os.listdir(path)
    verification_results = {
        "files_exist": False,
        "valid_html": False,
        "valid_js": False,
        "valid_css": False,
        "imports_exist": False,
        "build_success": False,
        "browser_verification": False
    }
    
    # Check if requested files exist
    required_files = ["index.html", "style.css", "script.js"]
    if all(file in files for file in required_files):
        verification_results["files_exist"] = True
    
    # Check for valid HTML, JS, and CSS files
    if "index.html" in files:
        with open(os.path.join(path, "index.html"), "r") as file:
            content = file.read()
            if "<!DOCTYPE html>" in content:
                verification_results["valid_html"] = True
    
    if "script.js" in files:
        with open(os.path.join(path, "script.js"), "r") as file:
            content = file.read()
            if "function" in content or "const" in content:
                verification_results["valid_js"] = True
    
    if "style.css" in files:
        with open(os.path.join(path, "style.css"), "r") as file:
            content = file.read()
            if "body" in content or "div" in content:
                verification_results["valid_css"] = True
    
    # Check for important imports
    if "index.html" in files:
        with open(os.path.join(path, "index.html"), "r") as file:
            content = file.read()
            if "<link rel=\"stylesheet\" href=\"style.css\">" in content and \
               "<script src=\"script.js\"></script>" in content:
                verification_results["imports_exist"] = True
    
    # Check build success if a build system exists
    if "package.json" in files:
        try:
            subprocess.run(["npm", "run", "build"], cwd=path, check=True, capture_output=True)
            verification_results["build_success"] = True
        except subprocess.CalledProcessError:
            pass
    
    # Browser automation verification (simplified)
    try:
        subprocess.run(["npm", "install", "puppeteer"], cwd=path, check=True, capture_output=True)
        subprocess.run(["node", "-e", "require('puppeteer').launch().then(browser => browser.close())"], cwd=path, check=True, capture_output=True)
        verification_results["browser_verification"] = True
    except subprocess.CalledProcessError:
        pass
    
    return verification_results

# Example usage for website verification
if __name__ == "__main__":
    workspace_info = detect_workspace()
    print(f"Workspace: {workspace_info['workspace_path']}")
    print(f"Project Type: {workspace_info['project_type']}")
    print(f"Git: {'available' if workspace_info['is_git_repo'] else 'unavailable'}")
    print(f"Package Manager: {workspace_info['package_manager']}")
    
    # Print worker registry
    print("\nWorker Registry:")
    for worker, info in WORKER_REGISTRY.items():
        print(f"{worker}: Available = {info['available']}, Command = {info['command']}, Version = {info['version']}")
    
    # Example task classification
    task_description = "Build a simple website with a button"
    task_classification = classify_task(task_description)
    print(f"\nTask Classification: {task_classification}")
    
    # Select best worker
    try:
        best_worker = select_best_worker(task_classification)
        print(f"Best Worker: {best_worker}")
    except ValueError as e:
        print(f"Error: {e}")
    
    # Example website verification
    verification_results = verify_website(workspace_info['workspace_path'])
    print("\nWebsite Verification Results:")
    for key, value in verification_results.items():
        print(f"{key}: {'Passed' if value else 'Failed'}")
    
    # Example result inspection
    original_task = "Build a simple website with a button"
    output_dir = workspace_info['workspace_path']
    file_matches = inspect_results(original_task, output_dir)
    
# Failure recovery logic
def recover_from_failure(error_message, task_description, output_dir):
    repair_task = f"Fix the following error: {error_message}\n\nTask: {task_description}\n\nDo not modify unrelated files.\n\nAfter fixing, run the build again."
    
    # Write repair task to a file
    with open(os.path.join(output_dir, "repair_task.txt"), "w") as file:
        file.write(repair_task)
    
    return repair_task

# Example usage for failure recovery
if __name__ == "__main__":
    workspace_info = detect_workspace()
    print(f"Workspace: {workspace_info['workspace_path']}")
    print(f"Project Type: {workspace_info['project_type']}")
    print(f"Git: {'available' if workspace_info['is_git_repo'] else 'unavailable'}")
    print(f"Package Manager: {workspace_info['package_manager']}")
    
    # Print worker registry
    print("\nWorker Registry:")
    for worker, info in WORKER_REGISTRY.items():
        print(f"{worker}: Available = {info['available']}, Command = {info['command']}, Version = {info['version']}")
    
    # Example task classification
    task_description = "Build a simple website with a button"
    task_classification = classify_task(task_description)
    print(f"\nTask Classification: {task_classification}")
    
    # Select best worker
    try:
        best_worker = select_best_worker(task_classification)
        print(f"Best Worker: {best_worker}")
    except ValueError as e:
        print(f"Error: {e}")
    
    # Example website verification
    verification_results = verify_website(workspace_info['workspace_path'])
    print("\nWebsite Verification Results:")
    for key, value in verification_results.items():
        print(f"{key}: {'Passed' if value else 'Failed'}")
    
    # Example result inspection
    original_task = "Build a simple website with a button"
    output_dir = workspace_info['workspace_path']
    file_matches = inspect_results(original_task, output_dir)
    
    # Example failure recovery
    error_message = "Module \"./Navbar\" not found."
    repair_task = recover_from_failure(error_message, original_task, output_dir)
    print(f"\nRepair Task:\n{repair_task}")
    
# Multi-worker mode logic
def multi_worker_mode(task_classification, output_dir):
    workers_used = []
    current_worker = select_best_worker(task_classification)
    workers_used.append(current_worker)
    
    # Simulate worker execution and verification
    verification_results = verify_website(output_dir)
    
    if not all(verification_results.values()):
        # Escalate to another worker if verification fails
        next_worker = escalate_worker(task_classification, current_worker)
        workers_used.append(next_worker)
        
        # Simulate the next worker's execution
        verification_results = verify_website(output_dir)
    
    return workers_used, verification_results

# Example usage for multi-worker mode
if __name__ == "__main__":
    workspace_info = detect_workspace()
    print(f"Workspace: {workspace_info['workspace_path']}")
    print(f"Project Type: {workspace_info['project_type']}")
    print(f"Git: {'available' if workspace_info['is_git_repo'] else 'unavailable'}")
    print(f"Package Manager: {workspace_info['package_manager']}")
    
    # Print worker registry
    print("\nWorker Registry:")
    for worker, info in WORKER_REGISTRY.items():
        print(f"{worker}: Available = {info['available']}, Command = {info['command']}, Version = {info['version']}")
    
    # Example task classification
    task_description = "Build a complex SaaS dashboard"
    task_classification = classify_task(task_description)
    print(f"\nTask Classification: {task_classification}")
    
    # Example multi-worker mode
    workers_used, verification_results = multi_worker_mode(task_classification, workspace_info['workspace_path'])
    print(f"\nWorkers Used: {workers_used}")
    print("\nVerification Results:")
    for key, value in verification_results.items():
        print(f"{key}: {'Passed' if value else 'Failed'}")
    
    # Example website verification
    verification_results = verify_website(workspace_info['workspace_path'])
    print("\nWebsite Verification Results:")
    for key, value in verification_results.items():
        print(f"{key}: {'Passed' if value else 'Failed'}")
    
    # Example result inspection
    original_task = "Build a simple website with a button"
    output_dir = workspace_info['workspace_path']
    file_matches = inspect_results(original_task, output_dir)
    
    # Example failure recovery
    error_message = "Module \"./Navbar\" not found."
    repair_task = recover_from_failure(error_message, original_task, output_dir)
    print(f"\nRepair Task:\n{repair_task}")
    
    # Example worker escalation
    task_description = "Build a complex SaaS dashboard"
    task_classification = classify_task(task_description)
    print(f"\nTask Classification: {task_classification}")
    
    # Simulate failure and escalate
    try:
        best_worker = select_best_worker(task_classification)
        print(f"Best Worker: {best_worker}")
        
        if best_worker == "FCC":
            print("\nSimulating failure with FCC...")
            next_worker = escalate_worker(task_classification, best_worker)
            print(f"Escalated to Worker: {next_worker}")
    except ValueError as e:
        print(f"Error: {e}")
    # Select best worker
    try:
        best_worker = select_best_worker(task_classification)
        print(f"Best Worker: {best_worker}")
    except ValueError as e:
        print(f"Error: {e}")
# Worker registry structure
WORKER_REGISTRY = {
    "FCC": {
        "available": False,
        "command": "fcc",
        "version": None,
        "capabilities": ["implementation", "simple coding", "website creation", "bug fixes"],
    },
    "Claude": {
        "available": False,
        "command": "claude",
        "version": None,
        "capabilities": ["architecture", "complex reasoning", "debugging", "code review"],
    },
    "OpenCode": {
        "available": False,
        "command": "opencode",
        "version": None,
        "capabilities": ["implementation", "frontend", "full-stack", "refactoring"],
    }
}

# Detect if a worker is available by checking its command
def is_worker_available(command):
    try:
        subprocess.run([command, "--version"], check=True, capture_output=True, text=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

# Detect worker availability and update registry
def detect_workers():
    global WORKER_REGISTRY
    for worker_name, worker_info in WORKER_REGISTRY.items():
        worker_info["available"] = is_worker_available(worker_info["command"])
        if worker_info["available"]:
            try:
                version_output = subprocess.run(
                    [worker_info["command"], "--version"],
                    capture_output=True,
                    text=True
                )
                worker_info["version"] = version_output.stdout.strip()
            except subprocess.CalledProcessError:
                worker_info["version"] = None
    return WORKER_REGISTRY

# Detect workers and update registry
detect_workers()

# Main detection logic for ANOMYMOUS
workspace_info = detect_workspace()

# Capability routing logic
WORKER_CAPABILITIES = {
    "FCC": ["implementation", "simple coding", "website creation", "bug fixes"],
    "Claude": ["architecture", "complex reasoning", "debugging", "code review"],
    "OpenCode": ["implementation", "frontend", "full-stack", "refactoring"],
}

def classify_task(task_description):
    task_classification = {
        "simple": False,
        "medium": False,
        "complex": False,
        "frontend": False,
        "backend": False,
        "full-stack": False,
        "debugging": False,
        "refactoring": False,
        "research": False,
        "testing": False
    }
    
    # Simple tasks (e.g., small coding tasks)
    if "change" in task_description.lower() or "fix" in task_description.lower():
        task_classification["simple"] = True
    
    # Medium tasks (e.g., frontend development)
    if "website" in task_description.lower() or "button" in task_description.lower():
        task_classification["frontend"] = True
        task_classification["medium"] = True
    
    # Complex tasks (e.g., full-stack development)
    if "dashboard" in task_description.lower() or "SaaS" in task_description.lower():
        task_classification["complex"] = True
        task_classification["full-stack"] = True
    
    # Debugging tasks
    if "debug" in task_description.lower() or "error" in task_description.lower():
        task_classification["debugging"] = True
        task_classification["medium"] = True
    
    # Refactoring tasks
    if "refactor" in task_description.lower():
        task_classification["refactoring"] = True
        task_classification["medium"] = True
    
    # Research tasks
    if "research" in task_description.lower():
        task_classification["research"] = True
    
    # Testing tasks
    if "test" in task_description.lower():
        task_classification["testing"] = True
    
    return task_classification

def select_best_worker(task_classification):
    available_workers = [worker for worker in WORKER_REGISTRY if WORKER_REGISTRY[worker]["available"]]
    if not available_workers:
        raise ValueError("No available workers.")
    
    # Select the worker with the least overlap in capabilities
    best_worker = None
    min_overlap = float('inf')
    
    for worker in available_workers:
        worker_capabilities = WORKER_CAPABILITIES[worker]
        overlap = sum(1 for capability in task_classification if capability in worker_capabilities)
        
        if overlap < min_overlap:
            min_overlap = overlap
            best_worker = worker
    
    return best_worker

if __name__ == "__main__":
    workspace_info = detect_workspace()
    print(f"Workspace: {workspace_info['workspace_path']}")
    print(f"Project Type: {workspace_info['project_type']}")
    print(f"Git: {'available' if workspace_info['is_git_repo'] else 'unavailable'}")
    print(f"Package Manager: {workspace_info['package_manager']}")
    
    # Print worker registry
    print("\nWorker Registry:")
    for worker, info in WORKER_REGISTRY.items():
        print(f"{worker}: Available = {info['available']}, Command = {info['command']}, Version = {info['version']}")
    
    # Example task classification
    task_description = "Build a simple website with a button"
    task_classification = classify_task(task_description)
    print(f"\nTask Classification: {task_classification}")
    
    # Select best worker
    best_worker = select_best_worker(task_classification)
    print(f"Best Worker: {best_worker}")