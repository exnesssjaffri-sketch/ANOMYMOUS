import pytest
import sys
import os
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from workspace_detector import detect_project_type, is_git_repo, get_package_manager

@pytest.fixture
def temp_workspace():
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir

def test_detect_project_type(temp_workspace):
    # Test for static website
    with open(os.path.join(temp_workspace, "index.html"), "w") as f:
        f.write("<html></html>")
    assert detect_project_type(temp_workspace) == "Static Website", "Static website should be detected"

    # Test for Python project
    with open(os.path.join(temp_workspace, "requirements.txt"), "w") as f:
        f.write("pytest")
    assert detect_project_type(temp_workspace) == "Python", "Python project should be detected"

    # Test for Node.js project
    with open(os.path.join(temp_workspace, "package.json"), "w") as f:
        f.write("{}")
    assert detect_project_type(temp_workspace) == "Node.js", "Node.js project should be detected"

    # Test for generic project
    assert detect_project_type(temp_workspace) == "Generic Project", "Generic project should be detected"

def test_is_git_repo(temp_workspace):
    assert not is_git_repo(temp_workspace), "Non-Git repository should be detected"

    # Simulate a Git repository
    os.makedirs(os.path.join(temp_workspace, ".git"))
    assert is_git_repo(temp_workspace), "Git repository should be detected"

def test_get_package_manager(temp_workspace):
    assert get_package_manager(temp_workspace) == "None", "No package manager should be detected"

    # Test for npm
    with open(os.path.join(temp_workspace, "package.json"), "w") as f:
        f.write("{}")
    assert get_package_manager(temp_workspace) == "npm", "npm should be detected"

    # Test for yarn
    with open(os.path.join(temp_workspace, "yarn.lock"), "w") as f:
        f.write("")
    assert get_package_manager(temp_workspace) == "yarn", "yarn should be detected"

    # Test for pnpm
    with open(os.path.join(temp_workspace, "pnpm-lock.yaml"), "w") as f:
        f.write("")
    assert get_package_manager(temp_workspace) == "pnpm", "pnpm should be detected"