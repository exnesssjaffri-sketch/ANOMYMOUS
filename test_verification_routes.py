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
        
        # Verify category and intent
        assert classification["category"] == expected_category, \
            f"Expected category {expected_category}, got {classification['category']}"
        assert classification["intent"] == expected_intent, \
            f"Expected intent {expected_intent}, got {classification['intent']}"
        
        # Verify verification strategy
        verification_strategy = classification.get("verification", {}).get("strategy")
        assert verification_strategy == expected_intent, \
            f"Expected verification strategy {expected_intent}, got {verification_strategy}"
        
        # Simulate workspace creation for testing
        verification_result = verifier.verify(classification, task_text)
        print(f"Verification Result: {verification_result}")

if __name__ == "__main__":
    test_verification_routing()