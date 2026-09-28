#!/usr/bin/env python3
"""Tests for task_classifier.py"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from task_classifier import TaskClassifier

def test_classify_simple():
    classifier = TaskClassifier()
    result = classifier.classify("simple task")
    assert result["category"] == "simple"
    print("test_classify_simple passed")

def test_classify_frontend():
    classifier = TaskClassifier()
    result = classifier.classify("create a website with html and css")
    assert result["category"] == "frontend"
    print("test_classify_frontend passed")

def test_classify_backend():
    classifier = TaskClassifier()
    result = classifier.classify("build a backend API")
    assert result["category"] == "backend"
    print("test_classify_backend passed")

def test_classify_debugging():
    classifier = TaskClassifier()
    result = classifier.classify("fix this bug")
    assert result["category"] == "debugging"
    print("test_classify_debugging passed")

def test_classify_refactoring():
    classifier = TaskClassifier()
    result = classifier.classify("refactor this code")
    assert result["category"] == "refactoring"
    print("test_classify_refactoring passed")

def test_classify_testing():
    classifier = TaskClassifier()
    result = classifier.classify("write tests for this")
    assert result["category"] == "testing"
    print("test_classify_testing passed")

def test_classify_research():
    classifier = TaskClassifier()
    result = classifier.classify("research this topic")
    assert result["category"] == "research"
    print("test_classify_research passed")

def test_classify_complex():
    classifier = TaskClassifier()
    result = classifier.classify("build a complex SaaS")
    assert result["category"] == "complex"
    print("test_classify_complex passed")

def test_classify_normalization():
    classifier = TaskClassifier()
    result = classifier.classify("  BUILD A WEBSITE  ")
    assert result["normalized_task"] == "build a website"
    print("test_classify_normalization passed")

def test_classify_overlapping():
    """Test overlapping categories - should pick first match"""
    classifier = TaskClassifier()
    result = classifier.classify("test and debug")
    # "test" comes first in the if-elif chain
    assert result["category"] == "testing"
    print("test_classify_overlapping passed")

if __name__ == "__main__":
    test_classify_simple()
    test_classify_frontend()
    test_classify_backend()
    test_classify_debugging()
    test_classify_refactoring()
    test_classify_testing()
    test_classify_research()
    test_classify_complex()
    test_classify_normalization()
    test_classify_overlapping()
    print("\nAll task_classifier tests passed!")