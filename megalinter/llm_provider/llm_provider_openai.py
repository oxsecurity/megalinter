#!/usr/bin/env python3
"""
OpenAI LLM Provider for MegaLinter
"""

from typing import Any, Dict, Optional

from megalinter import config

from .llm_provider_openai_compatible import OpenAICompatibleProvider


class OpenAIProvider(OpenAICompatibleProvider):

    DISPLAY_NAME = "OpenAI"
    API_KEY_VAR_NAME = "OPENAI_API_KEY"
    DEFAULT_BASE_URL = "https://api.openai.com/v1"

    def get_default_model(self) -> str:
        return "gpt-4.1-mini"

    def load_config(self, request_id: Optional[str] = None) -> Dict[str, Any]:
        return {
            "api_key": config.get(request_id, "OPENAI_API_KEY", ""),
            # OPENAI_API_BASE: legacy variable name also honored by the OpenAI SDKs
            "base_url": config.get(request_id, "OPENAI_BASE_URL", None)
            or config.get(request_id, "OPENAI_API_BASE", None),
            "organization": config.get(request_id, "OPENAI_ORG_ID", None)
            or config.get(request_id, "OPENAI_ORGANIZATION", None),
            "project": config.get(request_id, "OPENAI_PROJECT_ID", None),
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

    def get_extra_headers(self) -> Dict[str, str]:
        headers = {}
        if self.get_config_value("organization"):
            headers["OpenAI-Organization"] = self.get_config_value("organization")
        if self.get_config_value("project"):
            headers["OpenAI-Project"] = self.get_config_value("project")
        return headers
