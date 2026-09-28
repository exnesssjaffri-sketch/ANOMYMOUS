"""ANOMYMOUS Provider Layer

Provides real LLM provider implementations with:
- Provider registry and configuration
- Real transport implementations
- Model capability discovery
- Health state persistence
- Analytics tracking

Usage:
  from providers.registry import ProviderRegistry
  
  config = ProviderRegistry.get_config("groq")
  transport = ProviderRegistry.create_transport("groq")
  routes = ProviderRegistry.create_routes(config, transport)
"""

# Auto-register all providers on import
from providers.register import register_all_providers, get_all_providers
from providers.registry import (
    register_provider,
    get_config,
    list_providers,
    create_transport,
    create_routes,
    get_provider_info,
)
from providers.health import HealthStatePersistence, RouteHealthState
from providers.model_capabilities import (
    get_provider_models,
    get_model_capability_info,
    get_provider_capabilities,
)

# Auto-register
_registered_providers = register_all_providers()

__all__ = [
    "register_all_providers",
    "get_all_providers",
    "register_provider",
    "get_config",
    "list_providers",
    "create_transport",
    "create_routes",
    "get_provider_info",
    "HealthStatePersistence",
    "RouteHealthState",
    "get_provider_models",
    "get_model_capability_info",
    "get_provider_capabilities",
]
