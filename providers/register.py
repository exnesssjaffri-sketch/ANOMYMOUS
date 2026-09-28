"""Provider registration module.

Registers all provider configurations into the global registry.
"""

from providers.configs import PROVIDER_CONFIGS
from providers.registry import register_provider, list_providers, get_config


def register_all_providers():
    """Register all provider configurations into the global registry."""
    for name, config in PROVIDER_CONFIGS.items():
        register_provider(name, config)
    return list_providers()


def get_provider_config(name):
    """Get provider configuration by name."""
    return get_config(name)


def get_all_providers():
    """Get all registered provider names."""
    return list_providers()


# Auto-register on import
register_all_providers()