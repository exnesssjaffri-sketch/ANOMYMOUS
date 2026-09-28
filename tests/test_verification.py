#!/usr/bin/env python3
"""Tests for verification.py"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from verification import verify_website

def test_missing_files():
    result = verify_website("/nonexistent/path")
    assert result["status"] == "failed"
    assert result["verified"] is False
    print("test_missing_files passed")

def test_valid_files():
    import tempfile
    import os
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create required files with valid HTML content
        with open(os.path.join(tmpdir, "index.html"), "w") as fh:
            fh.write("<html><body><h1>Test</h1></body></html>")
        with open(os.path.join(tmpdir, "style.css"), "w") as fh:
            fh.write("body { color: red; }")
        with open(os.path.join(tmpdir, "script.js"), "w") as fh:
            fh.write("console.log('test');")
        result = verify_website(tmpdir)
        assert result["status"] == "success"
        assert result["verified"] is True
        print("test_valid_files passed")

def test_build_failure():
    result = verify_website("/nonexistent/path")
    assert result["status"] == "failed"
    print("test_build_failure passed")

def test_test_failure():
    result = verify_website("/nonexistent/path")
    assert result["status"] == "failed"
    print("test_test_failure passed")

if __name__ == "__main__":
    test_missing_files()
    test_valid_files()
    test_build_failure()
    test_test_failure()
    print("\nAll verification tests passed!")