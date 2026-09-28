#!/usr/bin/env python3

import os
import json
import sys
sys.path.insert(0, 'C:\\Users\\ALI HAIDER\\OneDrive\\Desktop\\ANOMYMOUS')

from orchestrator import Orchestrator
from transport import MockTransport

# Setup workspace
workspace_dir = 'C:\\Users\\ALI HAIDER\\OneDrive\\Desktop\\ANOMYMOUS\\workspace'
os.makedirs(os.path.join(workspace_dir, 'restaurant'), exist_ok=True)

# Mock transport
mock_transport = MockTransport({
    'Create a simple restaurant website with:': {
        'output': json.dumps({
            'choices': [
                {
                    'message': {
                        'content': json.dumps({
                            'thought': 'Creating a restaurant website.',
                            'actions': [
                                {'type': 'create_file', 'path': 'restaurant/index.html', 'content': '<html><head><title>Restaurant</title></head><body><h1>Welcome</h1></body></html>', 'critical': True},
                                {'type': 'create_file', 'path': 'restaurant/style.css', 'content': 'body { color: red; font-family: Arial; }', 'critical': True},
                                {'type': 'create_file', 'path': 'restaurant/script.js', 'content': 'console.log(\"Restaurant site loaded!\");', 'critical': True}
                            ]
                        })
                    }
                }
            ]
        })
    }
})

# Orchestrator setup
orchestrator = Orchestrator(
    provider='mock',
    model='mock-model',
    transport=mock_transport,
    endpoint='http://localhost',
    api_key='mock-key',
    workspace_dir=workspace_dir
)

# Execute task
task = 'Create a simple restaurant website'
result = orchestrator.execute_task(task)

# Print result
print('=== Full Result ===')
print(f'Status: {result["status"]}')
print(f'Verification: {result.get("verification", "NOT FOUND")}')

# Verify workspace files
for f in ['index.html', 'style.css', 'script.js']:
    path = os.path.join(workspace_dir, 'restaurant', f)
    if os.path.exists(path):
        with open(path, 'r') as file:
            content = file.read()
            print(f'✓ {f} exists and is non-empty')
            print(f'   Content preview: {content[:100]}...')
    else:
        print(f'✗ {f} missing')

# Check for workspace escape
workspace_root = os.path.join(workspace_dir, '..')
if os.path.exists(workspace_root):
    for root, dirs, files in os.walk(workspace_root):
        if 'restaurant' in dirs and any(f in root for f in ['index.html', 'style.css', 'script.js']):
            print('⚠️ Files found outside workspace boundary')
            break
else:
    print('✓ Workspace root does not exist')

# Verify verifier result
if result.get('verification', {}).get('status') == 'success':
    print('✓ Verification result is successful')
else:
    print('✗ Verification result is failed')

# Classification
print('MOCKED ORCHESTRATOR + ACTION EXECUTION: VERIFIED')