#!/usr/bin/env python3
import urllib.request
import json

# Trigger /task endpoint
data = json.dumps({"task": "Create a simple restaurant website"}).encode()
req = urllib.request.Request('http://127.0.0.1:8000/task', data=data, headers={'Content-Type': 'application/json'})
resp = urllib.request.urlopen(req)
print("Response:", resp.read().decode())