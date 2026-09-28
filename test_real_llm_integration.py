import json
import unittest
from unittest.mock import patch
from transport import RealHTTPTransport, MockTransport
from llmapi_adapter import LLMAPIAdapter
from orchestrator import Orchestrator
from workspace_manager import WorkspaceManager
from action_executor import ActionExecutor
from verification import TaskVerifier

# Mock provider response (simplified for testing)
mock_response_id = "mock-req-123"
mock_provider_response = {
    "id": mock_response_id,
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
                        }
                    ]
                })
            }
        }
    ]
}

class TestRealLLMIntegration(unittest.TestCase):
    def setUp(self):
        # Use a mock transport with the provider response
        self.transport = MockTransport()
        self.transport.responses = {mock_response_id: mock_provider_response}
        
        # Setup workspace
        self.workspace_dir = "C:\\Users\\ALI HAIDER\\OneDrive\\Desktop\\ANOMYMOUS\\workspace"
        self.workspace_manager = WorkspaceManager(self.workspace_dir)
        self.action_executor = ActionExecutor(self.workspace_manager)
        self.verifier = TaskVerifier(self.workspace_dir)
        
        # Initialize orchestrator with a mock transport
        self.orchestrator = Orchestrator(
            provider="test_provider",
            model="test_model",
            transport=self.transport,
            endpoint="https://api.example.com/v1",
            api_key="test_api_key"
        )

    def test_real_llm_integration(self):
        task_text = "Create a simple restaurant website"
        
        # Execute task
        result = self.orchestrator.execute_task(task_text)
        
        # Verify workspace files
        self.assertTrue(self.workspace_manager.exists("restaurant"))
        
        # Check if files were created
        files = self.workspace_manager.list_files("restaurant")
        # Check for full paths
        normalized_files = [f.replace('\\', '/') for f in files]
        self.assertIn("restaurant/index.html", normalized_files)
        self.assertIn("restaurant/style.css", normalized_files)
        self.assertIn("restaurant/script.js", normalized_files)
        
        # Verify file contents
        with open(f"{self.workspace_dir}/restaurant/index.html", "r") as f:
            content = f.read()
            self.assertIn("<title>Restaurant</title>", content)
            
        with open(f"{self.workspace_dir}/restaurant/style.css", "r") as f:
            content = f.read()
            self.assertIn("color: red; font-family: Arial;", content)
            
        with open(f"{self.workspace_dir}/restaurant/script.js", "r") as f:
            content = f.read()
            self.assertIn("Restaurant site loaded!", content)
            
        # Verify result status
        self.assertEqual(result["status"], "success")
        self.assertIsNotNone(result["verification"])

if __name__ == "__main__":
    unittest.main()