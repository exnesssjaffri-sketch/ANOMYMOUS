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
    
    required_files = ["index.html"]
    missing = [f for f in required_files if not os.path.exists(os.path.join(workspace_path, f))]
    
    if missing:
        print(f"Missing files: {', '.join(missing)}")
        return {
            "status": "failed",
            "verified": False,
            "diagnostics": [f"Missing files: {', '.join(missing)}"]
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