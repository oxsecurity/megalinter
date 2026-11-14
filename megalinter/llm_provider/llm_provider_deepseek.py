#!/usr/bin/env python3
"""
DeepSeek LLM Provider for MegaLinter
"""

from typing import Any, Dict, Optional

from megalinter import config

from .llm_provider_openai_compatible import OpenAICompatibleProvider


class DeepSeekProvider(OpenAICompatibleProvider):

    DISPLAY_NAME = "DeepSeek"
    API_KEY_VAR_NAME = "DEEPSEEK_API_KEY"
    DEFAULT_BASE_URL = "https://api.deepseek.com/v1"
    MAX_TOKENS_FIELD = "max_tokens"
    USE_DEVELOPER_ROLE_FOR_O_SERIES = False

    def get_default_model(self) -> str:
        return "deepseek-chat"

    def load_config(self, request_id: Optional[str] = None) -> Dict[str, Any]:
        return {
            "api_key": config.get(request_id, "DEEPSEEK_API_KEY", ""),
            "base_url": config.get(
                request_id, "DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1"
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
