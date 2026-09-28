#!/usr/bin/env python3
"""
Token estimation utilities for pre-dispatch budget checks.

Uses lightweight heuristics to estimate token counts without consuming API quotas.
"""

import re
from typing import Dict, Any, List


def estimate_tokens(text: str) -> int:
    """
    Estimate the number of tokens in a text string.
    
    Uses a heuristic based on character count and common word patterns.
    Average English token ≈ 4 characters (including spaces/punctuation).
    This is conservative enough for budget checks.
    
    Args:
        text: The text string to estimate
        
    Returns:
        Estimated token count (int)
    """
    if not text:
        return 0
    
    # Count characters
    char_count = len(text)
    
    # Count words (split on whitespace)
    words = text.split()
    word_count = len(words)
    
    # Heuristic: tokens ≈ (characters / 4) + (words * 0.5) for safety margin
    # This accounts for punctuation, special tokens, and overhead
    estimated = int(char_count / 4) + int(word_count * 0.5)
    
    # Add a small buffer (10%) for JSON overhead and special tokens
    estimated = int(estimated * 1.1)
    
    return max(estimated, 1)


def estimate_message_tokens(message: Dict[str, Any]) -> int:
    """
    Estimate tokens for a single message dict.
    Includes role and content tokens.
    """
    tokens = 0
    if "role" in message:
        tokens += estimate_tokens(message["role"])
    if "content" in message:
        tokens += estimate_tokens(message["content"])
    # Add overhead for JSON structure (~4 tokens per message for keys/quotes)
    tokens += 4
    return tokens


def estimate_payload_tokens(payload: Dict[str, Any]) -> int:
    """
    Estimate total tokens for a full request payload.
    Includes model name, messages, and other fields.
    """
    tokens = 0
    
    # Model name
    if "model" in payload:
        tokens += estimate_tokens(payload["model"])
    
    # Messages
    messages = payload.get("messages", [])
    for msg in messages:
        tokens += estimate_message_tokens(msg)
    
    # Other fields that add tokens
    if "temperature" in payload:
        tokens += 2
    if "response_format" in payload:
        tokens += estimate_tokens(str(payload["response_format"]))
    if "max_tokens" in payload:
        tokens += 4
    
    # Add overhead for JSON structure and request framing
    tokens += 10
    
    return tokens


def reduce_payload_tokens(payload: Dict[str, Any], target_tokens: int) -> Dict[str, Any]:
    """
    Attempt to reduce the payload to fit within target_tokens.
    
    Strategy (in order, least destructive first):
    1. Remove system prompt if present
    2. Truncate user message content (keep beginning, add ellipsis)
    3. If still too large, truncate more aggressively
    
    Args:
        payload: The original payload
        target_tokens: Maximum allowed tokens
        
    Returns:
        Reduced payload dict, or original if already within limit
    """
    current_tokens = estimate_payload_tokens(payload)
    if current_tokens <= target_tokens:
        return payload
    
    # Create a mutable copy
    reduced = dict(payload)
    messages = reduced.get("messages", [])
    
    # Strategy 1: Remove system prompt (if present and there's a user message)
    if len(messages) > 1 and messages[0].get("role") == "system":
        # Save system prompt content for potential later use
        system_content = messages[0].get("content", "")
        # Remove system message
        reduced["messages"] = messages[1:]
        new_tokens = estimate_payload_tokens(reduced)
        if new_tokens <= target_tokens:
            return reduced
        messages = reduced["messages"]
    
    # Strategy 2: Truncate the last (user) message content
    if messages:
        last_msg = messages[-1]
        if last_msg.get("role") == "user" and "content" in last_msg:
            original_content = last_msg["content"]
            # Calculate how many tokens we need to remove
            tokens_to_remove = estimate_payload_tokens(reduced) - target_tokens
            # Estimate characters to remove (approx 4 chars per token)
            chars_to_remove = max(tokens_to_remove * 4, 50)
            
            if len(original_content) > chars_to_remove + 20:
                # Keep first part, add truncation marker
                truncated = original_content[:len(original_content) - chars_to_remove]
                # Try to cut at a word boundary
                truncated = truncated.rsplit(' ', 1)[0] if ' ' in truncated else truncated
                truncated += "... [truncated]"
                reduced["messages"] = messages[:-1] + [{"role": "user", "content": truncated}]
                new_tokens = estimate_payload_tokens(reduced)
                if new_tokens <= target_tokens:
                    return reduced
    
    # Strategy 3: More aggressive truncation - keep only first 500 chars of user message
    if messages:
        last_msg = messages[-1]
        if last_msg.get("role") == "user" and "content" in last_msg:
            original_content = last_msg["content"]
            if len(original_content) > 500:
                truncated = original_content[:500] + "... [truncated]"
                reduced["messages"] = messages[:-1] + [{"role": "user", "content": truncated}]
                new_tokens = estimate_payload_tokens(reduced)
                if new_tokens <= target_tokens:
                    return reduced
    
    # If still too large, return the most reduced version we have
    return reduced


def can_fit_in_budget(payload: Dict[str, Any], max_tokens: int) -> bool:
    """
    Check if a payload can fit within the token budget.
    """
    return estimate_payload_tokens(payload) <= max_tokens