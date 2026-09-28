#!/usr/bin/env python3
"""
Test verification routing for structured task intents.
"""

from task_classifier import TaskClassifier
from verification import TaskVerifier


def test_verification_routing():
    classifier = TaskClassifier()
    verifier = TaskVerifier("workspace")

    test_cases = [
        ("Create a restaurant website", "website"),
        ("Build a static site", "website"),
        ("Build a Python API", "api"),
        ("Build a CSV processing backend service", "backend_service"),
        ("Build a full-stack inventory dashboard", "web_app"),
        ("Fix a Python import error", "debugging"),
        ("Add authentication tests", "testing"),
    ]

    for task_text, expected_intent in test_cases:
        print(f"\n--- Task: {task_text} ---")
        classification = classifier.classify(task_text)
        print(f"Classification: {classification}")
        
        # Extract intent from classification
        intent = classification.get("intent", "unknown")
        print(f"Extracted Intent: {intent}")
        
        # Simulate workspace creation for testing
        verification_result = verifier.verify(classification, task_text)
        print(f"Verification Result: {verification_result}")

if __name__ == "__main__":
    test_verification_routing()