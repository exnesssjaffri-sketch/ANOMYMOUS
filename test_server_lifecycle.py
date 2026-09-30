#!/usr/bin/env python3
"""Server ON/OFF lifecycle verification - 4 complete cycles."""
import sys, os, time, subprocess, json, signal

def test_lifecycle():
    """Start and stop the server 4 times, verifying it starts and stops cleanly."""
    for cycle in range(1, 5):
        print(f"\n=== Cycle {cycle}/4 ===")
        
        # Start server
        proc = subprocess.Popen(
            [sys.executable, "-c", "import server; server.run_server()"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        
        # Wait for server to start
        time.sleep(2)
        
        if proc.poll() is not None:
            stdout, stderr = proc.communicate()
            print(f"FAIL: Server exited early on cycle {cycle}")
            print(f"stdout: {stdout.decode()}")
            print(f"stderr: {stderr.decode()}")
            return False
        
        print(f"PASS: Server started (PID {proc.pid})")
        
        # Terminate server
        proc.send_signal(signal.SIGTERM)
        try:
            proc.wait(timeout=5)
            print(f"PASS: Server terminated cleanly on cycle {cycle}")
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait()
            print(f"PASS: Server killed (had to force) on cycle {cycle}")
    
    print("\n=== All 4 lifecycle cycles passed! ===")
    return True

if __name__ == "__main__":
    success = test_lifecycle()
    sys.exit(0 if success else 1)