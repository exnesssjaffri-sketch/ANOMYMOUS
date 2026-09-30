#!/usr/bin/env python3

from typing import Dict, Any

class TaskClassifier:
    """
    Analyzes and classifies the task for downstream consumption.
    Does NOT select workers or perform orchestration.
    """

    CATEGORIES = [
        "simple",
        "frontend",
        "backend",
        "full_stack",
        "debugging",
        "refactoring",
        "testing",
        "research",
        "complex"
    ]

    def classify(self, task_text: str) -> Dict[str, Any]:
        """
        Normalizes and classifies the task with structured intent.
        """
        normalized_text = task_text.strip().lower()
        
        # Simple heuristic classification with intent/verification metadata
        category = "simple"
        intent = "generic"
        verification = {
            "strategy": "generic",
            "expected_artifacts": []
        }
        
        if "test" in normalized_text:
            category = "testing"
            intent = "testing"
            verification = {
                "strategy": "testing",
                "expected_artifacts": []
            }
        elif "bug" in normalized_text or "fix" in normalized_text:
            category = "debugging"
            intent = "debugging"
            verification = {
                "strategy": "debugging",
                "expected_artifacts": []
            }
        elif "frontend" in normalized_text or "html" in normalized_text or "css" in normalized_text:
            category = "frontend"
            intent = "website"
            verification = {
                "strategy": "website",
                "expected_artifacts": ["index.html", "style.css", "script.js"]
            }
        elif "backend" in normalized_text or "api" in normalized_text:
            category = "backend"
            if "api" in normalized_text:
                intent = "api"
                verification = {
                    "strategy": "api",
                    "expected_artifacts": []
                }
            else:
                intent = "backend_service"
                verification = {
                    "strategy": "backend_service",
                    "expected_artifacts": []
                }
        elif "full_stack" in normalized_text or "dashboard" in normalized_text:
            category = "full_stack"
            intent = "web_app"
            verification = {
                "strategy": "web_app",
                "expected_artifacts": []
            }
        elif "refactor" in normalized_text:
            category = "refactoring"
            intent = "refactoring"
            verification = {
                "strategy": "refactoring",
                "expected_artifacts": []
            }
        elif "research" in normalized_text:
            category = "research"
            intent = "research"
            verification = {
                "strategy": "research",
                "expected_artifacts": []
            }
        elif "complex" in normalized_text:
            category = "complex"
            intent = "complex"
            verification = {
                "strategy": "complex",
                "expected_artifacts": []
            }
        elif "restaurant" in normalized_text or "website" in normalized_text or "static site" in normalized_text or ("static" in normalized_text and "site" in normalized_text):
            category = "frontend"
            intent = "website"
            verification = {
                "strategy": "website",
                "expected_artifacts": ["index.html", "style.css", "script.js"]
            }
        
        return {
            "category": category,
            "intent": intent,
            "original_task": task_text,
            "normalized_task": normalized_text,
            "verification": verification
        }

    def get_all_capabilities(self) -> list:
        """Return list of all available capabilities (categories + intents)."""
        return [
            {"category": "simple", "intent": "generic", "description": "Simple text-based task"},
            {"category": "testing", "intent": "testing", "description": "Testing tasks"},
            {"category": "debugging", "intent": "debugging", "description": "Debugging tasks"},
            {"category": "frontend", "intent": "website", "description": "Frontend/website tasks"},
            {"category": "frontend", "intent": "generic", "description": "General frontend tasks"},
            {"category": "backend", "intent": "api", "description": "Backend API tasks"},
            {"category": "backend", "intent": "backend_service", "description": "Backend service tasks"},
            {"category": "full_stack", "intent": "web_app", "description": "Full-stack web applications"},
            {"category": "refactoring", "intent": "refactoring", "description": "Code refactoring tasks"},
            {"category": "research", "intent": "research", "description": "Research tasks"},
            {"category": "complex", "intent": "complex", "description": "Complex multi-step tasks"}
        ]
