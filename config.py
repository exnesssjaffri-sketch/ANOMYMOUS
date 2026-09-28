import os

# Configuration for Real HTTP Transport
# Defaults to no endpoint - must be explicitly configured via env vars
REAL_TRANSPORT_CONFIG = {
    "endpoint": os.getenv("LLM_API_ENDPOINT"),
    "api_key": os.getenv("LLM_API_KEY"),
    "timeout": 30
}

# Mock Transport for testing
MOCK_TRANSPORT_CONFIG = {
    "responses": {}
}