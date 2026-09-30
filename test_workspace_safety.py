#!/usr/bin/env python3
"""Workspace safety negative tests."""
import sys, os, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from workspace_manager import WorkspaceManager

def test_safe_paths():
    tmp = tempfile.mkdtemp()
    wm = WorkspaceManager(tmp)
    
    # Normal path should work
    try:
        p = wm._safe_path('normal/file.txt')
        print(f"PASS: normal path: {p}")
    except Exception as e:
        print(f"FAIL: normal path raised: {e}")
        return False
    
    # Path escape attempts should be blocked
    escape_attempts = [
        '../outside',
        'subdir/../../outside',
        'a/../../b/../c.txt',
        '....//....//etc/passwd',
        '..\\..\\windows',
    ]
    
    all_blocked = True
    for attempt in escape_attempts:
        try:
            p = wm._safe_path(attempt)
            print(f"FAIL: escape attempt '{attempt}' was NOT blocked, returned: {p}")
            all_blocked = False
        except ValueError as e:
            print(f"PASS: escape attempt '{attempt}' blocked: {e}")
        except Exception as e:
            print(f"FAIL: escape attempt '{attempt}' raised unexpected: {e}")
            all_blocked = False
    
    # On Windows, '/etc/passwd' is NOT an absolute path (only 'C:\...' or '\...' are)
    # So it's correctly resolved as a relative path inside the workspace
    try:
        p = wm._safe_path('/etc/passwd')
        if p.startswith(wm.root_dir):
            print(f"PASS: '/etc/passwd' correctly resolved inside workspace: {p}")
        else:
            print(f"FAIL: '/etc/passwd' escaped workspace: {p}")
            all_blocked = False
    except Exception as e:
        print(f"FAIL: '/etc/passwd' raised unexpected: {e}")
        all_blocked = False
    
    return all_blocked

if __name__ == "__main__":
    success = test_safe_paths()
    sys.exit(0 if success else 1)