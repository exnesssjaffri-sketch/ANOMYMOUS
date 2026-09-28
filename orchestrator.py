import os
import json
from typing import Dict, Any, Optional, List, Type, Union
from transport import Transport, MockTransport, RealHTTPTransport
from llmapi_adapter import LLMAPIAdapter
from task_classifier import TaskClassifier
from process_executor import execute_process
from workspace_manager import WorkspaceManager
from action_executor import ActionExecutor
from verification import TaskVerifier

class Orchestrator:
    def __init__(self, provider: str, model: str, transport: Transport = None, endpoint: str = None, api_key: str = None, workspace_dir: Optional[str] = None):
        # Use RealHTTPTransport if endpoint and api_key are provided, else use MockTransport
        if transport is None:
            if endpoint and api_key:
                from transport import RealHTTPTransport
                transport = RealHTTPTransport(endpoint, api_key)
            else:
                from transport import MockTransport
                transport = MockTransport()
        
        self.llmapi_adapter = LLMAPIAdapter(provider, model, transport)
        self.task_classifier = TaskClassifier()
        
        # Set up safe workspace
        if workspace_dir is None:
            workspace_dir = os.path.join(os.getcwd(), "workspace")
        self.workspace_manager = WorkspaceManager(workspace_dir)
        self.action_executor = ActionExecutor(self.workspace_manager)
        self.verifier = TaskVerifier(workspace_dir)

    def execute_task(self, task_text: str, max_attempts: int = 3) -> Dict[str, Any]:
        """
        Execute a task through the complete ANOMYMOUS workflow.
        """
        task_classification = self.task_classifier.classify(task_text)
        print(f"Task classification: {task_classification}")
        
        for attempt in range(1, max_attempts + 1):
            # Get LLM response
            llm_result = self.llmapi_adapter.send_request(task_text)
            print(f"LLM Result: {llm_result}")
            
            if llm_result["status"] != "success":
                print(f"LLM API failed: {llm_result}")
                if attempt == max_attempts:
                    return self._create_final_result(
                        "failed",
                        execution=llm_result,
                        verification=None,
                        diagnostics=[f"LLMAPI failed after {max_attempts} attempts"]
                    )
                continue
            
            # Parse actions from LLM response
            try:
                parsed_content = json.loads(llm_result["output"])
                if isinstance(parsed_content, dict) and "actions" in parsed_content:
                    actions = parsed_content.get("actions", [])
                elif isinstance(parsed_content, list):
                    actions = parsed_content
                else:
                    actions = []
                print(f"Extracted actions: {actions}")
            except json.JSONDecodeError as e:
                print(f"Failed to parse LLM response: {e}")
                if attempt == max_attempts:
                    return self._create_final_result(
                        "failed",
                        execution=llm_result,
                        verification=None,
                        diagnostics=[f"Failed to parse LLM response: {str(e)}"]
                    )
                continue
            
            # Execute actions
            execution_result = self.action_executor.execute_actions(actions)
            print(f"Execution result: {execution_result}")
            
            # Verify the result
            verification_result = self.verifier.verify(task_classification, task_text)
            print(f"Verification result: {verification_result}")
            
            # Debug: Ensure verification_result is not None
            if verification_result is None:
                print("Verification result is None, using generic task verification")
                verification_result = {
                    "status": "failed",
                    "verified": False,
                    "diagnostics": ["Verification failed due to unexpected result"]
                }
            
            # Debug: Print verification_result before returning
            print(f"Verification result before return: {verification_result}")
            
            if verification_result["status"] == "success":
                print("Verification result is successful\nVerification: {verification_result}\n")
                return self._create_final_result(
                    "success",
                    execution=llm_result,
                    verification=verification_result,
                    diagnostics=["Task completed successfully"]
                )
            
            # Handle verification failure
            print("Verification result is failed\nVerification: {verification_result}\n")
            if attempt == max_attempts:
                return self._create_final_result(
                    "failed",
                    execution=llm_result,
                    verification=verification_result,
                    diagnostics=[f"Verification failed after {max_attempts} attempts"]
                )

    def _build_repair_prompt(self, original_task: str, attempt: int, failure_type: str, details: str) -> str:
        """
        Builds a compact repair prompt context without accumulating unlimited history.
        """
        return f"""Original Task: {original_task}
Attempt {attempt} failed.
Failure type: {failure_type}
Details: {details}

Please correct your actions to resolve this failure. Ensure that you return the corrected actions inside a valid JSON object following the required schema."""

    def _verify_result(self, local_work_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Verify the result of local work.
        """
        # This is a simplified verification - real implementation would check
        # for required files, build success, test results, etc.
        
        if local_work_result["status"] == "success":
            # Check if the file exists and has content
            if os.path.exists("task_output.txt") and os.path.getsize("task_output.txt") > 0:
                return {
                    "status": "success",
                    "verified": True,
                    "diagnostics": ["File exists and is not empty"]
                }
            
        return {
            "status": "failed",
            "verified": False,
            "diagnostics": ["Verification failed"]
        }

    def _create_final_result(self, status: str, execution: Dict[str, Any], verification: Optional[Dict[str, Any]], diagnostics: List[str]) -> Dict[str, Any]:
        result = {
            "status": status,
            "execution": execution,
            "verification": verification,
            "provider": self.llmapi_adapter.provider,
            "model": self.llmapi_adapter.model,
            "output": execution.get("output"),
            "diagnostics": diagnostics
        }
        
        # Ensure verification status is explicitly set
        if status == "success" and verification:
            if verification.get("verified", False) is False:
                result["status"] = "failed"
                result["diagnostics"].append("Verification failed despite execution success")
        
        return result

