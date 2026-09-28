"""Model capability definitions for providers."""

from providers.base import ModelInfo, ProviderCapability

# Common capabilities
COMMON_CAPABILITIES = [
    ProviderCapability.CHAT,
    ProviderCapability.JSON_MODE,
]

POWER_CAPABILITIES = [
    ProviderCapability.CHAT,
    ProviderCapability.JSON_MODE,
    ProviderCapability.FUNCTION_CALLING,
    ProviderCapability.STREAMING,
]

EXTENDED_CAPABILITIES = [
    ProviderCapability.CHAT,
    ProviderCapability.JSON_MODE,
    ProviderCapability.FUNCTION_CALLING,
    ProviderCapability.STREAMING,
    ProviderCapability.CONTEXT_EXTENSION,
]
# Groq models
groq_models = [
    ModelInfo(
        id="llama-3.1-70b-versatile",
        name="Llama 3.1 70B Versatile",
        context_window=8192,
        max_output_tokens=4096,
        supports=POWER_CAPABILITIES,
        tpm_limit=100000,
        rpm_limit=60,
        tier="premium",
    ),
    ModelInfo(
        id="llama-3.1-8b-instant",
        name="Llama 3.1 8B Instant",
        context_window=8192,
        max_output_tokens=4096,
        supports=COMMON_CAPABILITIES,
        tpm_limit=100000,
        rpm_limit=60,
        tier="standard",
    ),
    ModelInfo(
        id="mixtral-8x7b-32768",
        name="Mixtral 8x7B",
        context_window=32768,
        max_output_tokens=4096,
        supports=POWER_CAPABILITIES,
        tpm_limit=100000,
        rpm_limit=60,
        tier="premium",
    ),
    ModelInfo(
        id="gemma-7b-it",
        name="Gemma 7B IT",
        context_window=8192,
        max_output_tokens=4096,
        supports=COMMON_CAPABILITIES,
        tpm_limit=50000,
        rpm_limit=60,
        tier="standard",
    ),
]
# Cerebras models
cerebras_models = [
    ModelInfo(
        id="llama-3.1-70b",
        name="Llama 3.1 70B",
        context_window=8192,
        max_output_tokens=4096,
        supports=POWER_CAPABILITIES,
        tpm_limit=100000,
        rpm_limit=60,
        tier="premium",
    ),
    ModelInfo(
        id="llama-3.1-8b",
        name="Llama 3.1 8B",
        context_window=8192,
        max_output_tokens=4096,
        supports=COMMON_CAPABILITIES,
        tpm_limit=100000,
        rpm_limit=60,
        tier="standard",
    ),
]

# Mistral models
mistral_models = [
    ModelInfo(
        id="mistral-large-latest",
        name="Mistral Large Latest",
        context_window=32768,
        max_output_tokens=4096,
        supports=POWER_CAPABILITIES,
        tpm_limit=100000,
        rpm_limit=60,
        tier="premium",
    ),
    ModelInfo(
        id="mistral-small-latest",
        name="Mistral Small Latest",
        context_window=8192,
        max_output_tokens=4096,
        supports=COMMON_CAPABILITIES,
        tpm_limit=100000,
        rpm_limit=60,
        tier="standard",
    ),
    ModelInfo(
        id="open-mistral-7b",
        name="Open Mistral 7B",
        context_window=8192,
        max_output_tokens=4096,
        supports=COMMON_CAPABILITIES,
        tpm_limit=50000,
        rpm_limit=60,
        tier="basic",
    ),
]

# OpenRouter models
openrouter_models = [
    ModelInfo(
        id="anthropic/claude-3-opus-20240229",
        name="Claude 3 Opus",
        context_window=200000,
        max_output_tokens=4096,
        supports=EXTENDED_CAPABILITIES,
        tpm_limit=100000,
        rpm_limit=60,
        tier="premium",
    ),
    ModelInfo(
        id="anthropic/claude-3-sonnet-20240229",
        name="Claude 3 Sonnet",
        context_window=200000,
        max_output_tokens=4096,
        supports=EXTENDED_CAPABILITIES,
        tpm_limit=100000,
        rpm_limit=60,
        tier="premium",
    ),
    ModelInfo(
        id="openai/gpt-4-turbo",
        name="GPT-4 Turbo",
        context_window=128000,
        max_output_tokens=4096,
        supports=EXTENDED_CAPABILITIES,
        tpm_limit=100000,
        rpm_limit=60,
        tier="premium",
    ),
    ModelInfo(
        id="google/gemini-pro",
        name="Gemini Pro",
        context_window=32768,
        max_output_tokens=4096,
        supports=POWER_CAPABILITIES,
        tpm_limit=100000,
        rpm_limit=60,
        tier="premium",
    ),
    ModelInfo(
        id="mistralai/mistral-large-latest",
        name="Mistral Large",
        context_window=32768,
        max_output_tokens=4096,
        supports=POWER_CAPABILITIES,
        tpm_limit=100000,
        rpm_limit=60,
        tier="standard",
    ),
]

# Cloudflare models
cloudflare_models = [
    ModelInfo(
        id="@cf/meta-llama-3.1-70b",
        name="Llama 3.1 70B Cloudflare",
        context_window=8192,
        max_output_tokens=4096,
        supports=POWER_CAPABILITIES,
        tpm_limit=100000,
        rpm_limit=60,
        tier="standard",
    ),
    ModelInfo(
        id="@cf/meta-llama-3.1-8b",
        name="Llama 3.1 8B Cloudflare",
        context_window=8192,
        max_output_tokens=4096,
        supports=COMMON_CAPABILITIES,
        tpm_limit=100000,
        rpm_limit=60,
        tier="basic",
    ),
]

# Kilo models
kilo_models = [
    ModelInfo(
        id="kilo/distil-gpt2-medium",
        name="Distil GPT-2 Medium",
        context_window=1024,
        max_output_tokens=512,
        supports=COMMON_CAPABILITIES,
        tpm_limit=10000,
        rpm_limit=20,
        tier="basic",
    ),
]

# LLM7 models
llm7_models = [
    ModelInfo(
        id="llm7/tiny-llama-1b",
        name="Tiny Llama 1B",
        context_window=2048,
        max_output_tokens=512,
        supports=COMMON_CAPABILITIES,
        tpm_limit=5000,
        rpm_limit=10,
        tier="basic",
    ),
    ModelInfo(
        id="llm7/micro-llama-3b",
        name="Micro Llama 3B",
        context_window=4096,
        max_output_tokens=1024,
        supports=POWER_CAPABILITIES,
        tpm_limit=10000,
        rpm_limit=20,
        tier="standard",
    ),
]

# Google AI Studio models
google_models = [
    ModelInfo(
        id="gemini-2.0-flash",
        name="Gemini 2.0 Flash",
        context_window=1048576,
        max_output_tokens=8192,
        supports=EXTENDED_CAPABILITIES,
        tpm_limit=1000000,
        rpm_limit=2000,
        tier="premium",
    ),
    ModelInfo(
        id="gemini-1.5-pro",
        name="Gemini 1.5 Pro",
        context_window=2097152,
        max_output_tokens=8192,
        supports=EXTENDED_CAPABILITIES,
        tpm_limit=1000000,
        rpm_limit=2000,
        tier="premium",
    ),
    ModelInfo(
        id="gemini-1.5-flash",
        name="Gemini 1.5 Flash",
        context_window=1048576,
        max_output_tokens=8192,
        supports=EXTENDED_CAPABILITIES,
        tpm_limit=1000000,
        rpm_limit=2000,
        tier="standard",
    ),
]

# HuggingFace models
huggingface_models = [
    ModelInfo(
        id="google/flan-t5-small",
        name="FLAN T5 Small",
        context_window=512,
        max_output_tokens=256,
        supports=COMMON_CAPABILITIES,
        tpm_limit=1000,
        rpm_limit=5,
        tier="basic",
    ),
    ModelInfo(
        id="microsoft/DialoGPT-medium",
        name="DialoGPT Medium",
        context_window=1024,
        max_output_tokens=512,
        supports=POWER_CAPABILITIES,
        tpm_limit=5000,
        rpm_limit=10,
        tier="standard",
    ),
]

# OpenAI models
openai_models = [
    ModelInfo(
        id="gpt-4o",
        name="GPT-4o",
        context_window=128000,
        max_output_tokens=4096,
        supports=EXTENDED_CAPABILITIES,
        tpm_limit=100000,
        rpm_limit=60,
        tier="premium",
    ),
    ModelInfo(
        id="gpt-4-turbo",
        name="GPT-4 Turbo",
        context_window=128000,
        max_output_tokens=4096,
        supports=EXTENDED_CAPABILITIES,
        tpm_limit=100000,
        rpm_limit=60,
        tier="premium",
    ),
    ModelInfo(
        id="gpt-3.5-turbo",
        name="GPT-3.5 Turbo",
        context_window=16385,
        max_output_tokens=4096,
        supports=POWER_CAPABILITIES,
        tpm_limit=100000,
        rpm_limit=60,
        tier="standard",
    ),
]

# Provider model registry
_provider_model_registry = {
    "google": google_models,
    "groq": groq_models,
    "cerebras": cerebras_models,
    "mistral": mistral_models,
    "openrouter": openrouter_models,
    "cloudflare": cloudflare_models,
    "kilo": kilo_models,
    "llm7": llm7_models,
    "huggingface": huggingface_models,
}


def get_provider_models(provider_name):
    """Get all models for a provider."""
    return _provider_model_registry.get(provider_name, [])


def get_model_capability_info(model_id):
    """Get capability information for a specific model."""
    for provider_name, models in _provider_model_registry.items():
        for model in models:
            if model.id == model_id:
                return {
                    "model_id": model.id,
                    "name": model.name,
                    "context_window": model.context_window,
                    "max_output_tokens": model.max_output_tokens,
                    "capabilities": [c.value for c in model.supports],
                    "tpm_limit": model.tpm_limit,
                    "rpm_limit": model.rpm_limit,
                    "tier": model.tier,
                }
    return None


def get_provider_capabilities(provider_name):
    """Get capabilities supported by a provider."""
    models = get_provider_models(provider_name)
    if not models:
        return []

    all_capabilities = set()
    for model in models:
        for capability in model.supports:
            all_capabilities.add(capability.value)

    return list(all_capabilities)