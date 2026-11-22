#!/usr/bin/env python3
"""
Ollama LLM Provider for MegaLinter
"""

import json
import logging
from typing import Any, Dict, Optional

import requests
from megalinter import config

from .llm_provider import LLMProvider, LLMProviderError


class OllamaProvider(LLMProvider):

    def get_default_model(self) -> str:
        return "llama3.2"

    def load_config(self, request_id: Optional[str] = None) -> Dict[str, Any]:
        return {
            "base_url": config.get(
                request_id, "OLLAMA_BASE_URL", "http://localhost:11434"
            ),
            # Only needed for Ollama cloud (https://ollama.com), not for a local server
            "api_key": config.get(request_id, "OLLAMA_API_KEY", ""),
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
            self.llm = self.create_http_session()
            logging.debug(
                f"Ollama provider initialized with model {self.get_model_name()} "
                f"at {self.get_base_url()}"
            )
            return True

        except Exception as e:
            logging.error(f"Failed to initialize Ollama provider: {str(e)}")
            return False

    # Server URL, with or without the /api segment
    def get_base_url(self) -> str:
        base_url = (
            self.get_config_value("base_url", "http://localhost:11434")
            or "http://localhost:11434"
        ).rstrip("/")
        for suffix in ["/generate", "/api"]:
            if base_url.endswith(suffix):
                base_url = base_url[: -len(suffix)]
        return base_url

    def get_http_error_hint(self, response: requests.Response) -> str:
        if response.status_code == 404:
            return (
                "maybe the model is not found: pull it with "
                f"`ollama pull {self.get_model_name()}`"
            )
        return ""

    def build_payload(
        self, prompt: str, system_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "model": self.get_model_name(),
            "prompt": self.build_text_prompt(prompt, system_prompt),
            "options": {},
        }
        temperature = self.get_config_value("temperature")
        if temperature is not None:
            payload["options"]["temperature"] = temperature
        return payload

    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        # Streamed response (Ollama default): the read timeout applies between
        # chunks, so slow local models are not interrupted while generating
        response = self.post_json(
            f"{self.get_base_url()}/api/generate",
            self.build_payload(prompt, system_prompt),
            headers=(
                {"Authorization": f"Bearer {self.get_config_value('api_key')}"}
                if self.get_config_value("api_key")
                else None
            ),
            stream=True,
        )
        response.encoding = "utf-8"
        texts = []
        try:
            for line in response.iter_lines(decode_unicode=True):
                if not line:
                    continue
                try:
                    chunk = json.loads(line)
                except json.JSONDecodeError as e:
                    raise LLMProviderError(
                        f"ollama API returned an invalid stream line: "
                        f"{self.truncate(line)}"
                    ) from e
                if chunk.get("error"):
                    raise LLMProviderError(
                        f"ollama API returned an error: {self.truncate(str(chunk['error']))}"
                    )
                texts.append(chunk.get("response") or "")
                if chunk.get("done") is True:
                    break
        finally:
            response.close()
        if not texts:
            raise LLMProviderError("No data received from Ollama stream.")
        return "".join(texts)
