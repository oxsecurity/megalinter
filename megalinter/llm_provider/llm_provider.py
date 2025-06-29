#!/usr/bin/env python3
"""
Base LLM Provider class for MegaLinter
"""

import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from langchain_core.messages import HumanMessage, SystemMessage


class LLMProvider(ABC):
    """Base class for all LLM providers"""
    
    # Centralized default configuration values
    DEFAULT_CONFIG = {
        "temperature": 0.1,
        "max_tokens": 1000,
        "timeout": 30,
        "retry_attempts": 3
    }
    
    def __init__(self):
        """Initialize the provider"""
        self.llm = None
        self.provider_name = self.__class__.__name__.replace("Provider", "").lower()
        self.config = {}
        
    @abstractmethod
    def initialize(self) -> bool:
        """
        Initialize the LLM provider
        
        Returns:
            bool: True if initialization successful, False otherwise
        """
        pass
    
    @abstractmethod
    def get_default_model(self) -> str:
        """
        Get the default model name for this provider
        
        Returns:
            str: Default model name
        """
        pass
    
    @abstractmethod
    def load_config(self, request_id: str = None) -> Dict[str, Any]:
        """
        Load provider-specific configuration
        
        Args:
            request_id: MegaLinter request ID for configuration access
            
        Returns:
            Dict containing provider configuration
        """
        pass
    
    def get_default_config_value(self, key: str) -> Any:
        """
        Get a default configuration value
        
        Args:
            key: Configuration key
            
        Returns:
            Default value for the key, or None if not found
        """
        return self.DEFAULT_CONFIG.get(key)
    
    def is_available(self) -> bool:
        """
        Check if the provider is available and properly configured
        
        Returns:
            bool: True if provider is ready to use
        """
        return self.llm is not None
    
    def invoke(self, prompt: str, system_prompt: str = None) -> str:
        """
        Invoke the LLM with a prompt
        
        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            
        Returns:
            str: LLM response
        """
        if not self.is_available():
            raise ValueError(f"{self.provider_name} provider is not properly initialized")
        
        try:
            if self.provider_name in ["ollama", "huggingface"]:
                # These providers use simple string invocation
                if system_prompt:
                    full_prompt = f"System: {system_prompt}\n\nUser: {prompt}"
                else:
                    full_prompt = prompt
                response = self.llm.invoke(full_prompt)
                return response
            else:
                # Chat-based providers use message format
                messages = []
                if system_prompt:
                    messages.append(SystemMessage(content=system_prompt))
                messages.append(HumanMessage(content=prompt))
                
                response = self.llm.invoke(messages)
                return response.content
                
        except Exception as e:
            logging.error(f"Error invoking {self.provider_name}: {str(e)}")
            raise
    
    def get_config_value(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value
        
        Args:
            key: Configuration key
            default: Default value if key not found
            
        Returns:
            Configuration value, falling back to centralized defaults
        """
        # First check provider config, then fall back to centralized defaults, then provided default
        if key in self.config:
            return self.config[key]
        elif key in self.DEFAULT_CONFIG:
            return self.DEFAULT_CONFIG[key]
        else:
            return default
    
    def requires_api_key(self) -> bool:
        """
        Check if this provider requires an API key
        
        Returns:
            bool: True if API key is required
        """
        return self.provider_name not in ["ollama"]  # Only Ollama doesn't require API key
