#!/usr/bin/env python3
"""
Anthropic Claude LLM Provider for MegaLinter
"""

import logging
import re
from typing import Any, Dict, Optional

from megalinter import config

from .llm_provider import LLMProvider, LLMProviderError


class AnthropicProvider(LLMProvider):

    DEFAULT_BASE_URL = "https://api.anthropic.com"
    API_VERSION = "2023-06-01"
    # API version removing temperature, top_p and top_k for every model
    NO_SAMPLING_PARAMETERS_API_VERSION = "2026-10-21"
    # Claude 4.7 and later models reject a temperature other than the default one
    NO_TEMPERATURE_MIN_MODEL_VERSION = (4, 7)
    # claude-opus-4-7, claude-sonnet-4-5-20250929, claude-3-7-sonnet-latest...
    MODEL_VERSION_REGEX = re.compile(r"^claude-(?:[a-z]+-)?(\d+)(?:-(\d{1,2}))?(?=-|$)")

    def get_default_model(self) -> str:
        return "claude-sonnet-5-5"

    def load_config(self, request_id: Optional[str] = None) -> Dict[str, Any]:
        return {
            "api_key": config.get(request_id, "ANTHROPIC_API_KEY", ""),
            # Base URL variables also honored by the Anthropic SDKs
            "base_url": config.get(request_id, "ANTHROPIC_BASE_URL", None)
            or config.get(request_id, "ANTHROPIC_API_URL", None),
            "api_version": config.get(
                request_id, "ANTHROPIC_API_VERSION", "2023-06-01"
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
            if not self.get_config_value("api_key"):
                raise ValueError("ANTHROPIC_API_KEY is required")
            self.llm = self.create_http_session()
            logging.debug(
                f"Anthropic provider initialized with model {self.get_model_name()}"
            )
            return True

        except Exception as e:
            logging.error(f"Failed to initialize Anthropic provider: {str(e)}")
            return False

    def build_payload(
        self, prompt: str, system_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        model_name = self.get_model_name()
        payload: Dict[str, Any] = {
            "model": model_name,
            "max_tokens": self.get_config_value("max_tokens"),
            "messages": [{"role": "user", "content": prompt}],
        }
        if system_prompt:
            payload["system"] = system_prompt
        temperature = self.get_config_value("temperature")
        if temperature is not None and self.accepts_temperature(model_name):
            payload["temperature"] = temperature
        return payload

    def get_api_version(self) -> str:
        return str(self.get_config_value("api_version") or self.API_VERSION)

    def accepts_temperature(self, model_name: str) -> bool:
        # API versions are dates: string comparison works
        if self.get_api_version() >= self.NO_SAMPLING_PARAMETERS_API_VERSION:
            return False
        if "mythos" in model_name:
            return False
        match = self.MODEL_VERSION_REGEX.match(model_name)
        if match is None:
            return True
        model_version = (int(match.group(1)), int(match.group(2) or 0))
        return model_version < self.NO_TEMPERATURE_MIN_MODEL_VERSION

    # Base URL without the version segment, as the Anthropic SDKs expect it.
    # A trailing /v1 (or full /v1/messages endpoint) is accepted
    def get_base_url(self) -> str:
        base_url = (self.get_config_value("base_url") or self.DEFAULT_BASE_URL).rstrip(
            "/"
        )
        for suffix in ["/messages", "/v1"]:
            if base_url.endswith(suffix):
                base_url = base_url[: -len(suffix)]
        return base_url

    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        response = self.post_json(
            f"{self.get_base_url()}/v1/messages",
            self.build_payload(prompt, system_prompt),
            headers={
                "x-api-key": self.get_config_value("api_key"),
                "anthropic-version": self.get_api_version(),
            },
        )
        data = self.parse_json_response(response)
        content = data.get("content")
        if not isinstance(content, list):
            raise LLMProviderError(
                f"anthropic API response contains no content "
                f"(keys: {list(data.keys())})"
            )
        return "".join(
            block.get("text") or ""
            for block in content
            if isinstance(block, dict) and block.get("type") == "text"
        )
