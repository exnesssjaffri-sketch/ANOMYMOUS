import requests

# Test Vercel production endpoints
base_url = "https://anomymous-omega.vercel.app"

endpoints = [
    "/health",
    "/providers",
    "/analytics",
    "/capabilities",
    "/status"
]

print("=== GET Endpoints ===")
for ep in endpoints:
    try:
        resp = requests.get(f"{base_url}{ep}", timeout=10)
        print(f"GET {ep}: {resp.status_code}")
        print(resp.json())
    except Exception as e:
        print(f"GET {ep}: ERROR - {e}")

print("\n=== POST /task ===")
try:
    resp = requests.post(f"{base_url}/task", json={"task": "Create a simple website"}, timeout=30)
    print(f"POST /task: {resp.status_code}")
    print(resp.json())
except Exception as e:
    print(f"POST /task: ERROR - {e}")

print("\n=== POST /task (malformed) ===")
try:
    resp = requests.post(f"{base_url}/task", json={}, timeout=10)
    print(f"POST /task (malformed): {resp.status_code}")
    print(resp.json())
except Exception as e:
    print(f"POST /task (malformed): ERROR - {e}")