#!/usr/bin/env python3
"""
Google Gemini LLM Provider for MegaLinter
"""

import logging
from typing import Any, Dict, Optional

from langchain_google_genai import ChatGoogleGenerativeAI
from megalinter import config

from .llm_provider import LLMProvider


class GoogleProvider(LLMProvider):

    def get_default_model(self) -> str:
        return "gemini-2.5-flash"

    def load_config(self, request_id: Optional[str] = None) -> Dict[str, Any]:
        return {
            "api_key": config.get(request_id, "GOOGLE_API_KEY", ""),
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
                raise ValueError("GOOGLE_API_KEY is required")

            model_name = self.get_config_value("model_name") or self.get_default_model()
            temperature = self.get_config_value("temperature")
            max_tokens = self.get_config_value("max_tokens")

            self.llm = ChatGoogleGenerativeAI(
                model=model_name,
                temperature=temperature,
                max_output_tokens=max_tokens,
                google_api_key=api_key,
            )

            logging.debug(f"Google provider initialized with model {model_name}")
            return True

        except Exception as e:
            logging.error(f"Failed to initialize Google provider: {str(e)}")
            return False
