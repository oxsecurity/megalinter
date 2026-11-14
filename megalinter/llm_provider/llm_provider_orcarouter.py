#!/usr/bin/env python3
"""
OrcaRouter LLM Provider for MegaLinter
"""

from typing import Any, Dict, Optional

from megalinter import config

from .llm_provider_openai_compatible import OpenAICompatibleProvider


class OrcaRouterProvider(OpenAICompatibleProvider):

    DISPLAY_NAME = "OrcaRouter"
    API_KEY_VAR_NAME = "ORCAROUTER_API_KEY"
    DEFAULT_BASE_URL = "https://api.orcarouter.ai/v1"

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
