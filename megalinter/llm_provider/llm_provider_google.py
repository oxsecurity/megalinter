#!/usr/bin/env python3
"""
Google Gemini LLM Provider for MegaLinter
"""

import logging
import re
from typing import Any, Dict, Optional

from megalinter import config

from .llm_provider import LLMProvider, LLMProviderError


class GoogleProvider(LLMProvider):

    DEFAULT_BASE_URL = "https://generativelanguage.googleapis.com"
    API_VERSION = "v1beta"
    VERSION_SEGMENT_REGEX = re.compile(r"/v\d+(?:alpha|beta)?\d*$")

    def get_default_model(self) -> str:
        return "gemini-2.5-flash"

    def load_config(self, request_id: Optional[str] = None) -> Dict[str, Any]:
        return {
            "api_key": config.get(request_id, "GOOGLE_API_KEY", ""),
            "base_url": config.get(request_id, "GOOGLE_BASE_URL", None),
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
                raise ValueError("GOOGLE_API_KEY is required")
            self.llm = self.create_http_session()
            logging.debug(
                f"Google provider initialized with model {self.get_model_name()}"
            )
            return True

        except Exception as e:
            logging.error(f"Failed to initialize Google provider: {str(e)}")
            return False

    # Host URL, with or without an API version segment (v1beta added when missing)
    def get_base_url(self) -> str:
        base_url = (self.get_config_value("base_url") or self.DEFAULT_BASE_URL).rstrip(
            "/"
        )
        if not self.VERSION_SEGMENT_REGEX.search(base_url):
            base_url = f"{base_url}/{self.API_VERSION}"
        return base_url

    def build_payload(
        self, prompt: str, system_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        generation_config: Dict[str, Any] = {"candidateCount": 1}
        temperature = self.get_config_value("temperature")
        if temperature is not None:
            generation_config["temperature"] = temperature
        max_tokens = self.get_config_value("max_tokens")
        if max_tokens is not None:
            generation_config["maxOutputTokens"] = max_tokens
        payload: Dict[str, Any] = {
            "contents": [{"role": "user", "parts": [{"text": prompt}]}],
            "generationConfig": generation_config,
        }
        if system_prompt:
            payload["systemInstruction"] = {"parts": [{"text": system_prompt}]}
        return payload

    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        model_name = self.get_model_name()
        if model_name.startswith("models/"):
            model_name = model_name.removeprefix("models/")
        response = self.post_json(
            f"{self.get_base_url()}/models/{model_name}:generateContent",
            self.build_payload(prompt, system_prompt),
            headers={"x-goog-api-key": self.get_config_value("api_key")},
        )
        data = self.parse_json_response(response)
        candidates = data.get("candidates") or []
        if not candidates:
            block_reason = (data.get("promptFeedback") or {}).get("blockReason")
            raise LLMProviderError(
                "google API returned no candidate"
                + (f" (prompt blocked: {block_reason})" if block_reason else "")
            )
        candidate = candidates[0]
        parts = (candidate.get("content") or {}).get("parts") or []
        # Thought parts are internal reasoning, not part of the answer
        texts = [
            part.get("text") or ""
            for part in parts
            if isinstance(part, dict) and not part.get("thought")
        ]
        text = "".join(texts)
        if not text:
            raise LLMProviderError(
                "google API returned no text "
                f"(finishReason: {candidate.get('finishReason', 'unknown')})"
            )
        return text
