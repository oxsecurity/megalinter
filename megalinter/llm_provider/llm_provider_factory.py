#!/usr/bin/env python3
"""
LLM Provider Factory for MegaLinter
"""

import logging
from typing import Dict, Any, Optional
from .llm_provider import LLMProvider
from .llm_provider_openai import OpenAIProvider
from .llm_provider_anthropic import AnthropicProvider
from .llm_provider_google import GoogleProvider
from .llm_provider_ollama import OllamaProvider
from .llm_provider_huggingface import HuggingFaceProvider
from .llm_provider_mistral import MistralProvider
from .llm_provider_deepseek import DeepSeekProvider
from .llm_provider_grok import GrokProvider


class LLMProviderFactory:
    """Factory for creating LLM providers"""
    
    SUPPORTED_PROVIDERS = {
        "openai": OpenAIProvider,
        "anthropic": AnthropicProvider,
        "google": GoogleProvider,
        "ollama": OllamaProvider,
        "huggingface": HuggingFaceProvider,
        "mistral": MistralProvider,
        "deepseek": DeepSeekProvider,
        "grok": GrokProvider
    }
    
    @classmethod
    def create_provider(cls, provider_name: str, request_id: str = None) -> Optional[LLMProvider]:
        """
        Create an LLM provider instance
        
        Args:
            provider_name: Name of the provider (e.g., 'openai', 'anthropic')
            request_id: Request ID for configuration context
            
        Returns:
            LLMProvider instance or None if creation failed
        """
        provider_name = provider_name.lower()
        
        if provider_name not in cls.SUPPORTED_PROVIDERS:
            logging.error(f"Unsupported LLM provider: {provider_name}")
            return None
            
        try:
            provider_class = cls.SUPPORTED_PROVIDERS[provider_name]
            provider = provider_class()
            
            # Load configuration using the provider's own method
            config = provider.load_config(request_id)
            provider.config = config
            
            if provider.initialize():
                return provider
            else:
                logging.error(f"Failed to initialize {provider_name} provider")
                return None
                
        except Exception as e:
            logging.error(f"Error creating {provider_name} provider: {str(e)}")
            return None
    
    @classmethod
    def get_supported_providers(cls) -> Dict[str, str]:
        """
        Get list of supported providers
        
        Returns:
            Dictionary mapping provider names to descriptions
        """
        return {
            "openai": "OpenAI GPT models",
            "anthropic": "Anthropic Claude models",
            "google": "Google Gemini models",
            "ollama": "Local Ollama models",
            "huggingface": "Hugging Face models",
            "mistral": "Mistral AI models",
            "deepseek": "DeepSeek models",
            "grok": "Grok (xAI) models"
        }
