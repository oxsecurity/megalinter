#!/usr/bin/env python3
"""
Mistral AI LLM Provider for MegaLinter
"""

from typing import Any, Dict, Optional

from megalinter import config

from .llm_provider_openai_compatible import OpenAICompatibleProvider


class MistralProvider(OpenAICompatibleProvider):

    DISPLAY_NAME = "Mistral"
    API_KEY_VAR_NAME = "MISTRAL_API_KEY"
    DEFAULT_BASE_URL = "https://api.mistral.ai/v1"
    MAX_TOKENS_FIELD = "max_tokens"
    USE_DEVELOPER_ROLE_FOR_O_SERIES = False
    OMIT_TEMPERATURE_FOR_GPT5_REASONING = False
    EXTRA_PAYLOAD: Dict[str, Any] = {"top_p": 1}

    def get_default_model(self) -> str:
        return "mistral-large-latest"

    def load_config(self, request_id: Optional[str] = None) -> Dict[str, Any]:
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
