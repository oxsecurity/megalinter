#!/usr/bin/env python3
"""
OrcaRouter LLM Provider for MegaLinter
"""

import logging
from typing import Any, Dict, Optional

from langchain_openai import ChatOpenAI
from megalinter import config

from .llm_provider import LLMProvider


class OrcaRouterProvider(LLMProvider):

    def get_default_model(self) -> str:
        return "orcarouter/fusion-mini"

    def load_config(self, request_id: Optional[str] = None) -> Dict[str, Any]:
        return {
            "api_key": config.get(request_id, "ORCAROUTER_API_KEY", ""),
            "base_url": config.get(
                request_id, "ORCAROUTER_BASE_URL", "https://api.orcarouter.ai/v1"
            ),
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
                raise ValueError("ORCAROUTER_API_KEY is required")

            model_name = self.get_config_value("model_name") or self.get_default_model()
            base_url = self.get_config_value("base_url", "https://api.orcarouter.ai/v1")
            temperature = self.get_config_value("temperature")
            max_tokens = self.get_config_value("max_tokens")

            # OrcaRouter exposes an OpenAI-compatible API
            self.llm = ChatOpenAI(
                model=model_name,
                temperature=temperature,
                max_tokens=max_tokens,
                api_key=api_key,
                base_url=base_url,
            )

            logging.debug(f"OrcaRouter provider initialized with model {model_name}")
            return True

        except Exception as e:
            logging.error(f"Failed to initialize OrcaRouter provider: {str(e)}")
            return False
