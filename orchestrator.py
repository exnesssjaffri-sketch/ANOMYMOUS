import os
import json
from typing import Dict, Any, Optional, List, Type, Union
from transport import Transport, MockTransport, RealHTTPTransport
from llmapi_adapter import LLMAPIAdapter
from llmapi_router import LLMAPIRouter
from task_classifier import TaskClassifier
from process_executor import execute_process
from workspace_manager import WorkspaceManager
from action_executor import ActionExecutor
from verification import TaskVerifier

class Orchestrator:
    def __init__(self, provider: str, model: str, transport: Transport = None, endpoint: str = None, api_key: str = None, workspace_dir: Optional[str] = None, max_tokens: int = 7000, router: LLMAPIRouter = None):
        self.router = router
        if router:
            self.llmapi_adapter = None
        else:
            if transport is None:
                if endpoint and api_key:
                    transport = RealHTTPTransport(endpoint, api_key)
                else:
                    # Production MUST NOT silently fall back to MockTransport
                    raise ValueError(
                        "No transport provided and no endpoint/api_key for RealHTTPTransport. "
                        "Transport is required for production use."
                    )
            self.llmapi_adapter = LLMAPIAdapter(provider, model, transport, max_tokens=max_tokens)
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
            if self.router:
                llm_result = self.router.send_request(task_text)
            else:
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
            
            # Check if execution failed - if so, don't proceed to verification
            if execution_result.get("status") == "error":
                print(f"Execution failed: {execution_result.get('error')}")
                if attempt == max_attempts:
                    return self._create_final_result(
                        "failed",
                        execution=execution_result,
                        verification=None,
                        diagnostics=[f"Execution failed: {execution_result.get('error')}"]
                    )
                continue
            
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
                print(f"Verification result is successful\nVerification: {verification_result}\n")
                return self._create_final_result(
                    "success",
                    execution=execution_result,
                    verification=verification_result,
                    diagnostics=["Task completed successfully"]
                )
            
            # Handle verification failure
            print(f"Verification result is failed\nVerification: {verification_result}\n")
            if attempt == max_attempts:
                return self._create_final_result(
                    "failed",
                    execution=execution_result,
                    verification=verification_result,
                    diagnostics=[f"Verification failed after {max_attempts} attempts"]
                )
            
            # Continue to next attempt
            continue
        
        # If we exhaust all attempts without returning, return a failure
        return self._create_final_result(
            "failed",
            execution=llm_result,
            verification=None,
            diagnostics=["All attempts failed"]
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

    def _verify_result(self, local_work_result: Dict[str, Any], task_classification: Dict[str, Any], task_text: str) -> Dict[str, Any]:
        """
        Verify the result of local work using the task verifier.
        """
        if local_work_result["status"] != "success":
            return {
                "status": "failed",
                "verified": False,
                "diagnostics": [f"Local work failed: {local_work_result.get('error', 'unknown')}"]
            }
        
        # Use the actual task verifier
        return self.verifier.verify(task_classification, task_text)

    def _create_final_result(self, status: str, execution: Dict[str, Any], verification: Optional[Dict[str, Any]], diagnostics: List[str]) -> Dict[str, Any]:
        if self.router:
            provider = execution.get("provider")
            model = execution.get("model")
        else:
            provider = self.llmapi_adapter.provider
            model = self.llmapi_adapter.model
        result = {
            "status": status,
            "execution": execution,
            "verification": verification,
            "provider": provider,
            "model": model,
            "output": execution.get("output"),
            "diagnostics": diagnostics
        }
        
        # Ensure verification status is explicitly set
        if status == "success" and verification:
            if verification.get("verified", False) is False:
                result["status"] = "failed"
                result["diagnostics"].append("Verification failed despite execution success")
        
        return result

