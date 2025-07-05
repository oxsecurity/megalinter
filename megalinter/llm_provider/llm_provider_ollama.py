#!/usr/bin/env python3
"""
Ollama LLM Provider for MegaLinter
"""

import logging
from typing import Any, Dict

from langchain_community.llms import Ollama
from megalinter import config

from .llm_provider import LLMProvider


class OllamaProvider(LLMProvider):

    def get_default_model(self) -> str:
        return "llama3.2"

    def load_config(self, request_id: str = None) -> Dict[str, Any]:
        return {
            "base_url": config.get(
                request_id, "OLLAMA_BASE_URL", "http://localhost:11434"
            ),
            "model_name": config.get(request_id, "LLM_MODEL_NAME", ""),
            "temperature": float(
                config.get(
                    request_id,
                    "LLM_TEMPERATURE",
                    str(self.get_default_config_value("temperature")),
                )
            ),
        }

    def initialize(self) -> bool:
        try:
            model_name = self.get_config_value("model_name") or self.get_default_model()
            base_url = self.get_config_value("base_url", "http://localhost:11434")
            temperature = self.get_config_value("temperature")

            self.llm = Ollama(
                model=model_name, base_url=base_url, temperature=temperature
            )

            logging.debug(
                f"Ollama provider initialized with model {model_name} at {base_url}"
            )
            return True

        except Exception as e:
            logging.error(f"Failed to initialize Ollama provider: {str(e)}")
            return False
