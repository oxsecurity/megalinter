#!/usr/bin/env python3
"""
Base class for LLM providers exposing an OpenAI-compatible chat completions API
"""

import logging
import re
from typing import Any, Dict, Optional
from urllib.parse import urlparse

from .llm_provider import LLMProvider, LLMProviderError


class OpenAICompatibleProvider(LLMProvider):

    DISPLAY_NAME = "OpenAI-compatible"
    API_KEY_VAR_NAME = ""
    DEFAULT_BASE_URL = "https://api.openai.com/v1"
    # OpenAI deprecated max_tokens in favor of max_completion_tokens (reasoning models)
    MAX_TOKENS_FIELD = "max_completion_tokens"
    # o-series models expect the system prompt with the developer role
    USE_DEVELOPER_ROLE_FOR_O_SERIES = True
    # gpt-5 reasoning models (except gpt-5-chat) reject a temperature other than 1
    OMIT_TEMPERATURE_FOR_GPT5_REASONING = True
    EXTRA_PAYLOAD: Dict[str, Any] = {}

    def initialize(self) -> bool:
        try:
            if not self.get_config_value("api_key"):
                raise ValueError(f"{self.API_KEY_VAR_NAME} is required")
            self.llm = self.create_http_session()
            logging.debug(
                f"{self.DISPLAY_NAME} provider initialized with model "
                f"{self.get_model_name()}"
            )
            return True

        except Exception as e:
            logging.error(
                f"Failed to initialize {self.DISPLAY_NAME} provider: {str(e)}"
            )
            return False

    # Base URL including the version segment (ex: https://api.openai.com/v1), as the
    # OpenAI SDKs expect it. A full endpoint URL ending with /chat/completions is accepted
    def get_base_url(self) -> str:
        base_url = (self.get_config_value("base_url") or self.DEFAULT_BASE_URL).rstrip(
            "/"
        )
        if base_url.endswith("/chat/completions"):
            base_url = base_url[: -len("/chat/completions")]
        # The provider's own host without path (ex: https://api.mistral.ai) gets the
        # default version segment. Other hosts are used as-is
        parsed_url = urlparse(base_url)
        if (
            parsed_url.path == ""
            and parsed_url.netloc == urlparse(self.DEFAULT_BASE_URL).netloc
        ):
            base_url = self.DEFAULT_BASE_URL
        return base_url

    def get_extra_headers(self) -> Dict[str, str]:
        return {}

    def get_headers(self) -> Dict[str, str]:
        headers = {"Authorization": f"Bearer {self.get_config_value('api_key')}"}
        headers.update(self.get_extra_headers())
        return headers

    def accepts_temperature(self, model_name: str, temperature: float) -> bool:
        model_lower = model_name.lower()
        return not (
            self.OMIT_TEMPERATURE_FOR_GPT5_REASONING
            and model_lower.startswith("gpt-5")
            and "chat" not in model_lower
            and temperature != 1
        )

    def build_payload(
        self, prompt: str, system_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        model_name = self.get_model_name()
        messages = []
        if system_prompt:
            system_role = (
                "developer"
                if self.USE_DEVELOPER_ROLE_FOR_O_SERIES
                and re.match(r"^o\d", model_name)
                else "system"
            )
            messages.append({"role": system_role, "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        payload: Dict[str, Any] = {
            "model": model_name,
            "messages": messages,
            "stream": False,
        }
        temperature = self.get_config_value("temperature")
        if temperature is not None and self.accepts_temperature(
            model_name, temperature
        ):
            payload["temperature"] = temperature
        max_tokens = self.get_config_value("max_tokens")
        if max_tokens is not None:
            payload[self.MAX_TOKENS_FIELD] = max_tokens
        payload.update(self.EXTRA_PAYLOAD)
        return payload

    @staticmethod
    def extract_text(content: Any) -> str:
        if content is None:
            return ""
        if isinstance(content, str):
            return content
        # Content chunks list (Mistral reasoning models): keep text chunks only
        if isinstance(content, list):
            texts = []
            for chunk in content:
                if isinstance(chunk, str):
                    texts.append(chunk)
                elif isinstance(chunk, dict) and chunk.get("type") == "text":
                    texts.append(chunk.get("text") or "")
            return "".join(texts)
        return str(content)

    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        response = self.post_json(
            f"{self.get_base_url()}/chat/completions",
            self.build_payload(prompt, system_prompt),
            headers=self.get_headers(),
        )
        data = self.parse_json_response(response)
        choices = data.get("choices")
        if not choices:
            raise LLMProviderError(
                f"{self.provider_name} API response contains no choices "
                f"(keys: {list(data.keys())})"
            )
        message = choices[0].get("message") or {}
        return self.extract_text(message.get("content"))
