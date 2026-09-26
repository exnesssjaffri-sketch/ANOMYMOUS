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
}

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
        if any(indicator in files for indicator in indicators):
            project_type = project
            break
    
    # Check for static website
    if "index.html" in files or "index.htm" in files:
        if project_type == "Generic Project":
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
def detect_workspace(path):
    workspace_info = {
        "workspace_path": path,
        "project_type": detect_project_type(path),
        "is_git_repo": is_git_repo(path),
        "package_manager": get_package_manager(path),
    }
    return workspace_info