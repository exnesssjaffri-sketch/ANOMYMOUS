import os

# Configuration for Real HTTP Transport
REAL_TRANSPORT_CONFIG = {
    "endpoint": os.getenv("LLM_API_ENDPOINT", "https://api.example.com/v1"),
    "api_key": os.getenv("LLM_API_KEY", "your_default_api_key_here"),
    "timeout": 30
}

# Mock Transport for testing
MOCK_TRANSPORT_CONFIG = {
    "responses": {}
}