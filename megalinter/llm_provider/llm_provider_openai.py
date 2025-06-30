#!/usr/bin/env python3
"""
OpenAI LLM Provider for MegaLinter
"""

import logging
from typing import Any, Dict

from langchain_openai import ChatOpenAI
from megalinter import config

from .llm_provider import LLMProvider


class OpenAIProvider(LLMProvider):

    def get_default_model(self) -> str:
        return "gpt-4o-mini"

    def load_config(self, request_id: str = None) -> Dict[str, Any]:
        return {
            "api_key": config.get(request_id, "OPENAI_API_KEY", ""),
            "base_url": config.get(request_id, "OPENAI_BASE_URL", None),
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
                raise ValueError("OpenAI API key is required")

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
                kwargs["base_url"] = base_url

            self.llm = ChatOpenAI(**kwargs)
            logging.info(f"OpenAI provider initialized with model {model_name}")
            return True

        except Exception as e:
            logging.error(f"Failed to initialize OpenAI provider: {str(e)}")
            return False
