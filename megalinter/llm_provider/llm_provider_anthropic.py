#!/usr/bin/env python3
"""
Anthropic Claude LLM Provider for MegaLinter
"""

import logging
from typing import Any, Dict

from langchain_anthropic import ChatAnthropic
from megalinter import config

from .llm_provider import LLMProvider


class AnthropicProvider(LLMProvider):

    def get_default_model(self) -> str:
        return "claude-3-5-haiku-20241022"

    def load_config(self, request_id: str = None) -> Dict[str, Any]:
        return {
            "api_key": config.get(request_id, "ANTHROPIC_API_KEY", ""),
            "model_name": config.get(request_id, "LLM_MODEL_NAME", ""),
            "temperature": float(
                config.get(
                    request_id,
                    "LLM_TEMPERATURE",
                    str(self.get_default_config_value("temperature")),
                )
            ),
            "max_tokens": int(
                config.get(
                    request_id,
                    "LLM_MAX_TOKENS",
                    str(self.get_default_config_value("max_tokens")),
                )
            ),
        }

    def initialize(self) -> bool:
        try:
            api_key = self.get_config_value("api_key")
            if not api_key:
                raise ValueError("Anthropic API key is required")

            model_name = self.get_config_value("model_name") or self.get_default_model()
            temperature = self.get_config_value("temperature")
            max_tokens = self.get_config_value("max_tokens")

            self.llm = ChatAnthropic(
                model=model_name,
                temperature=temperature,
                max_tokens=max_tokens,
                api_key=api_key,
            )

            logging.debug(f"Anthropic provider initialized with model {model_name}")
            return True

        except Exception as e:
            logging.error(f"Failed to initialize Anthropic provider: {str(e)}")
            return False
