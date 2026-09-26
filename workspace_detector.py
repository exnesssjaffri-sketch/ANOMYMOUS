#!/usr/bin/env python3
from pathlib import Path
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
}

def is_git_repo(path):
    try:
        subprocess.run(["git", "rev-parse", "--is-inside-work-tree"], cwd=Path(path), check=True, capture_output=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def detect_project_type(path):
    path = Path(path)
    files = list(path.iterdir())
    project_type = "Generic Project"
    
    if is_git_repo(path):
        project_type = "Git Repository"
    
    for project, indicators in PROJECT_INDICATORS.items():
        if project == "Git Repository":
            continue
        if any(indicator in str(file) for indicator in indicators if file.is_file()):
            project_type = project
            break
    
    if any(str(file).endswith(('.html', '.htm')) for file in files):
        if project_type == "Generic Project":
            project_type = "Static Website"
    
    return project_type

def get_package_manager(path):
    path = Path(path)
    files = list(path.iterdir())
    if any(str(file).endswith("package.json") for file in files):
        return "npm"
    elif any(str(file).endswith("yarn.lock") for file in files):
        return "yarn"
    elif any(str(file).endswith("pnpm-lock.yaml") for file in files):
        return "pnpm"
    else:
        return "None"

def detect_workspace(path=None):
    if path is None:
        path = Path.cwd()
    return {
        "workspace_path": str(path),
        "project_type": detect_project_type(path),
        "is_git_repo": is_git_repo(path),
        "package_manager": get_package_manager(path),
    }