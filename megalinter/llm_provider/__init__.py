#!/usr/bin/env python3
"""
LLM Provider package for MegaLinter
"""

# Provider classes are resolved lazily (PEP 562): each one imports a heavy LLM SDK
# (langchain_openai, langchain_anthropic, google.genai, ...) that would add several
# seconds to EVERY MegaLinter startup, even when LLM Advisor is disabled.
# pylint: disable=undefined-all-variable
from importlib import import_module

from .llm_provider import LLMProvider
from .llm_provider_factory import LLMProviderFactory

_LAZY_PROVIDER_MODULES = {
    "OpenAIProvider": "llm_provider_openai",
    "AnthropicProvider": "llm_provider_anthropic",
    "GoogleProvider": "llm_provider_google",
    "OllamaProvider": "llm_provider_ollama",
    "HuggingFaceProvider": "llm_provider_huggingface",
    "MistralProvider": "llm_provider_mistral",
    "DeepSeekProvider": "llm_provider_deepseek",
    "GrokProvider": "llm_provider_grok",
    "OrcaRouterProvider": "llm_provider_orcarouter",
}

__all__ = [
    "LLMProvider",
    "LLMProviderFactory",
    *_LAZY_PROVIDER_MODULES.keys(),
]


def __getattr__(name):
    if name in _LAZY_PROVIDER_MODULES:
        module = import_module(f".{_LAZY_PROVIDER_MODULES[name]}", __name__)
        return getattr(module, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
