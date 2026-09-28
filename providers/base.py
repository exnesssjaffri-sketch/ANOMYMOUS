"""Base provider classes and definitions."""

from dataclasses import dataclass
from typing import Dict, Any, List, Optional
from enum import Enum


class AuthType(Enum):
    """Authentication types for providers."""
    REQUIRED = "required"  # API key required
    OPTIONAL = "optional"  # Works without key (limited) or with key (full)
    NONE = "none"  # No authentication


class ProviderCapability(Enum):
    """Provider capabilities."""
    CHAT = "chat"
    COMPLETION = "completion"
    STREAMING = "streaming"
    JSON_MODE = "json_mode"
    VISION = "vision"
    FUNCTION_CALLING = "function_calling"
    CONTEXT_EXTENSION = "context_extension"


@dataclass
class ModelInfo:
    """Information about a model."""
    id: str
    name: str
    context_window: int
    max_output_tokens: int
    supports: List[ProviderCapability]
    tpm_limit: Optional[int] = None
    rpm_limit: Optional[int] = None
    tier: str = "standard"


@dataclass
class ProviderConfig:
    """Configuration for a provider."""
    name: str
    display_name: str
    endpoint: str
    auth_type: AuthType
    auth_env_var: str  # Environment variable name for API key
    default_models: List[ModelInfo]
    all_models: List[ModelInfo]
    supports: List[ProviderCapability]
    requires_auth: bool = True
    anonymous_access: Optional[str] = None  # What works without auth (or None if not supported)
    rate_limit_info: Optional[str] = None  # Human-readable rate limits