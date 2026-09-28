#!/usr/bin/env python3
"""
Manual test for verification architecture.
Validates task classification and structured intent.
"""

from task_classifier import TaskClassifier
from verification import TaskVerifier
import os


def test_task_classification_and_verification():
    classifier = TaskClassifier()
    verifier = TaskVerifier("workspace")

    test_cases = [
        ("Create a restaurant website", "frontend", "website"),
        ("Build a static site", "frontend", "website"),
        ("Build a Python API", "backend", "api"),
        ("Build a CSV processing backend service", "backend", "backend_service"),
        ("Build a full-stack inventory dashboard", "full_stack", "web_app"),
        ("Fix a Python import error", "debugging", "debugging"),
        ("Add authentication tests", "testing", "testing"),
    ]

    for task_text, expected_category, expected_intent in test_cases:
        print(f"\n--- Task: {task_text} ---")
        classification = classifier.classify(task_text)
        print(f"Classification: {classification}")
        print(f"Expected Category: {expected_category}, Got: {classification['category']}")
        print(f"Expected Intent: {expected_intent}, Got: {classification['intent']}")
        
        # Simulate workspace creation for testing
        os.makedirs(os.path.join(classification['workspace_dir'] or 'workspace', 'test'), exist_ok=True)
        verification_result = verifier.verify(classification, task_text)
        print(f"Verification Result: {verification_result}")

if __name__ == "__main__":
    test_task_classification_and_verification()