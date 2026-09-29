"""Provider Registry - Central registry for LLM provider configurations and transports."""
import os
import json
from typing import Dict, Any, List, Optional

from providers.base import (
    AuthType,
    ModelInfo,
    ProviderConfig,
    ProviderCapability,
)

_provider_configs: Dict[str, Any] = {}
_transport_factories: Dict[str, Any] = {}


def register_provider(name, config, transport_factory=None):
    _provider_configs[name] = config
    if transport_factory:
        _transport_factories[name] = transport_factory


def get_config(name):
    return _provider_configs.get(name)


def list_providers():
    return list(_provider_configs.keys())
"""Create a transport instance for the given provider."""
def create_transport(provider_name, api_key=None, endpoint=None):
    """Create a transport instance for the given provider.

    Args:
        provider_name: Registered provider name
        api_key: API key (if None, reads from auth_env_var)
        endpoint: Optional endpoint override

    Returns:
        Transport instance

    Raises:
        ValueError: If provider is not registered
    """
    config = _provider_configs.get(provider_name)
    if not config:
        raise ValueError(f"Provider '{provider_name}' is not registered")

    # Use provided key or read from env var
    key = api_key
    if not key:
        key = os.getenv(config.auth_env_var)

    # Use provided endpoint or config endpoint
    url = endpoint or config.endpoint

    # Determine transport type based on auth requirements
    if config.requires_auth and not key:
        if config.anonymous_access:
            # Use anonymous access mode (limited)
            # Production MUST NOT silently fall back to MockTransport
            raise ValueError(
                f"Provider '{provider_name}' requires authentication but no API key is available. "
                f"Please set {config.auth_env_var} environment variable or configure authentication."
            )
        else:
            # Provider requires auth but no key available - fail explicitly
            raise ValueError(
                f"Provider '{provider_name}' requires authentication but no API key is available. "
                f"Please set {config.auth_env_var} environment variable."
            )

    # Create standard transport
    # Production MUST NOT silently fall back to MockTransport or real transports
    if provider_name in ["kilo", "llm7"] and not key:
        # Providers that support anonymous access must still get a real transport
        # (not MockTransport) for production
        raise ValueError(
            f"Provider '{provider_name}' requires an API key for production use. "
            f"Please set {config.auth_env_var} environment variable."
        )
    else:
        from transport import RealHTTPTransport
        return RealHTTPTransport(url, key or "")


def create_anonymous_transport(provider_name, config):
    """Create a transport that allows anonymous/limited access."""
    from transport import MockTransport
    # Return mock transport that simulates limited anonymous access
    return MockTransport({})


def create_routes(provider_name, transport=None, max_candidates=3):
    """Create ProviderRoute instances for a registered provider.

    Args:
        provider_name: Registered provider name
        transport: Optional transport instance (creates one if None)
        max_candidates: Maximum number of routes to create

    Returns:
        List of ProviderRoute instances
    """
    from llmapi_router import ProviderRoute, LLMAPIRouter
    from llmapi_adapter import LLMAPIAdapter
    from transport import Transport

    config = _provider_configs.get(provider_name)
    if not config:
        raise ValueError(f"Provider '{provider_name}' is not registered")

    # Create routes for default models
    routes = []
    models_to_use = config.default_models[:max_candidates]

    # Also include all_models if default_models is empty
    models = models_to_use if models_to_use else config.all_models[:max_candidates]

    for model_info in models:
        # For HuggingFace, create a transport specific to this model
        if provider_name == "huggingface":
            route_transport = create_huggingface_transport_for_model(config, model_info.id)
        elif transport is None:
            route_transport = create_transport(provider_name)
        else:
            route_transport = transport
        
        route = ProviderRoute(
            provider=provider_name,
            model=model_info.id,
            transport=route_transport,
            max_tokens=model_info.context_window,
            priority=model_info.tier_weight if hasattr(model_info, 'tier_weight') else 1,
            weight=model_info.weight if hasattr(model_info, 'weight') else 1.0,
        )
        routes.append(route)

    return routes


def create_huggingface_transport_for_model(config, model_id):
    """Create a transport for a specific HuggingFace model using the router API."""
    from transport import RealHTTPTransport
    
    # For HuggingFace Router, the model ID should be passed in the URL path
    # The endpoint is the OpenAI-compatible chat completions endpoint
    endpoint = f"{config.endpoint}?model={model_id}"
    
    # Use provided key or read from env var
    api_key_env_var = config.auth_env_var
    api_key = os.getenv(api_key_env_var)
    
    if not api_key:
        raise ValueError(f"No API key available for HuggingFace model '{model_id}'. "
                        f"Please set {api_key_env_var} environment variable.")
    
    # Create the transport
    transport = RealHTTPTransport(endpoint, api_key)
    
    # Monkey-patch the transport to convert payloads to HuggingFace router format
    original_send_request = transport.send_request
    
    def send_request_with_conversion(payload, timeout):
        # Convert OpenAI format to HuggingFace router format
        messages = payload.get("messages", [])
        if not messages:
            return original_send_request(payload, timeout)
        
        # For chat models, use the messages directly as they already match OpenAI format
        # The router expects OpenAI-compatible chat completions format
        # So we can pass the payload directly through
        return original_send_request(payload, timeout)
    
    transport.send_request = send_request_with_conversion
    return transport


def get_provider_info(provider_name):
    """Get human-readable info about a provider."""
    config = _provider_configs.get(provider_name)
    if not config:
        return None

    models_info = []
    for model in config.all_models:
        models_info.append({
            "id": model.id,
            "name": model.name,
            "context_window": model.context_window,
            "supports": [c.value for c in model.supports],
        })

    return {
        "name": config.display_name,
        "endpoint": config.endpoint,
        "auth_type": config.auth_type.value,
        "requires_auth": config.requires_auth,
        "anonymous_access": config.anonymous_access,
        "rate_limit_info": config.rate_limit_info,
        "default_models": [
            {"id": m.id, "name": m.name, "context_window": m.context_window}
            for m in config.default_models
        ],
        "all_models": models_info,
    }