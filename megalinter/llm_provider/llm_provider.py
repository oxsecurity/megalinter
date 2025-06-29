#!/usr/bin/env python3
"""
Base LLM Provider class for MegaLinter
"""

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict

from langchain_core.messages import HumanMessage, SystemMessage


class LLMProvider(ABC):

    # Centralized default configuration values
    DEFAULT_CONFIG = {
        "temperature": 0.1,
        "max_tokens": 1000,
        "timeout": 30,
        "retry_attempts": 3,
    }

    def __init__(self):
        self.llm = None
        self.provider_name = self.__class__.__name__.replace("Provider", "").lower()
        self.config = {}

    @abstractmethod
    def initialize(self) -> bool:
        pass

    @abstractmethod
    def get_default_model(self) -> str:
        pass

    @abstractmethod
    def load_config(self, request_id: str = None) -> Dict[str, Any]:
        pass

    def get_default_config_value(self, key: str) -> Any:
        return self.DEFAULT_CONFIG.get(key)

    def is_available(self) -> bool:
        return self.llm is not None

    def invoke(self, prompt: str, system_prompt: str = None) -> str:
        if not self.is_available():
            raise ValueError(
                f"{self.provider_name} provider is not properly initialized"
            )

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
        # First check provider config, then fall back to centralized defaults, then provided default
        if key in self.config:
            return self.config[key]
        elif key in self.DEFAULT_CONFIG:
            return self.DEFAULT_CONFIG[key]
        else:
            return default

    def requires_api_key(self) -> bool:
        return self.provider_name not in [
            "ollama"
        ]  # Only Ollama doesn't require API key
