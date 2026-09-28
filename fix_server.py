import os
path = r'c:\Users\ALI HAIDER\OneDrive\Desktop\ANOMYMOUS\server.py'
with open(path, 'r') as f:
    content = f.read()

# Replace the import line
content = content.replace(
    'from transport import MockTransport',
    'from transport import MockTransport, RealHTTPTransport'
)

# Replace the mock transport block
old_block = '''# Use mock transport for testing
mock_transport = MockTransport({
    "Create a simple restaurant website with": {
        "output": json.dumps({
            "choices": [
                {
                    "message": {
                        "content": json.dumps({
                            "thought": "Creating a restaurant website.",
                            "actions": [
                                {
                                    "type": "create_file",
                                    "path": "restaurant/index.html",
                                    "content": "<html><head><title>Restaurant</title></head><body><h1>Welcome</h1></body></html>",
                                    "critical": True
                                },
                                {
                                    "type": "create_file",
                                    "path": "restaurant/style.css",
                                    "content": "body { color: red; font-family: Arial; }",
                                    "critical": True
                                },
                                {
                                    "type": "create_file",
                                    "path": "restaurant/script.js",
                                    "content": "console.log('Restaurant site loaded!');",
                                    "critical": True
                                }
                            ]
                        })
                    }
                }
            ]
        })
    }
})

orchestrator = Orchestrator(provider="mock", model="mock-model", transport=mock_transport)'''

new_block = '''# Use RealHTTPTransport by default for production
# MockTransport is only used in tests or when explicitly configured via env var
if os.getenv("ANOMYMOUS_USE_MOCK", "0") == "1":
    mock_transport = MockTransport({
        "Create a simple restaurant website with": {
            "output": json.dumps({
                "choices": [
                    {
                        "message": {
                            "content": json.dumps({
                                "thought": "Creating a restaurant website.",
                                "actions": [
                                    {
                                        "type": "create_file",
                                        "path": "restaurant/index.html",
                                        "content": "<html><head><title>Restaurant</title></head><body><h1>Welcome</h1></body></html>",
                                        "critical": True
                                    },
                                    {
                                        "type": "create_file",
                                        "path": "restaurant/style.css",
                                        "content": "body { color: red; font-family: Arial; }",
                                        "critical": True
                                    },
                                    {
                                        "type": "create_file",
                                        "path": "restaurant/script.js",
                                        "content": "console.log('Restaurant site loaded!');",
                                        "critical": True
                                    }
                                ]
                            })
                        }
                    }
                ]
            })
        }
    })
    transport = mock_transport
else:
    transport = RealHTTPTransport(
        REAL_TRANSPORT_CONFIG["endpoint"],
        REAL_TRANSPORT_CONFIG["api_key"]
    )

orchestrator = Orchestrator(provider="groq", model="llama-3.1-8b-instant", transport=transport)'''

if old_block in content:
    content = content.replace(old_block, new_block)
    # Add import for config
    content = content.replace(
        'from providers.analytics import analytics',
        'from providers.analytics import analytics\nfrom config import REAL_TRANSPORT_CONFIG'
    )
    with open(path, 'w') as f:
        f.write(content)
    print('File updated successfully')
else:
    print('Old block not found in file')
    # Try to find what's different
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if 'mock_transport' in line or 'Use mock' in line:
            print(f'Line {i}: {repr(line)}')