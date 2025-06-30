#!/usr/bin/env python3
"""
Mistral AI LLM Provider for MegaLinter
"""

import logging
from typing import Any, Dict

from langchain_mistralai import ChatMistralAI
from megalinter import config

from .llm_provider import LLMProvider


class MistralProvider(LLMProvider):

    def get_default_model(self) -> str:
        return "mistral-large-latest"

    def load_config(self, request_id: str = None) -> Dict[str, Any]:
        return {
            "api_key": config.get(request_id, "MISTRAL_API_KEY", ""),
            "base_url": config.get(request_id, "MISTRAL_BASE_URL", None),
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
                raise ValueError("Mistral API key is required")

            model_name = self.get_config_value("model_name") or self.get_default_model()
            base_url = self.get_config_value("base_url")
            temperature = self.get_config_value("temperature")
            max_tokens = self.get_config_value("max_tokens")

            kwargs = {
                "model": model_name,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "api_key": api_key,
            }

            if base_url:
                kwargs["endpoint"] = base_url

            self.llm = ChatMistralAI(**kwargs)

            logging.info(f"Mistral provider initialized with model {model_name}")
            return True

        except Exception as e:
            logging.error(f"Failed to initialize Mistral provider: {str(e)}")
            return False
