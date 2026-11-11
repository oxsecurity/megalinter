#!/usr/bin/env python3
"""
Base LLM Provider class for MegaLinter
"""

import email.utils
import json
import logging
import os
import time
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Any, Dict, Optional, Union

import requests
from megalinter import config


class LLMProviderError(Exception):
    pass


class LLMProvider(ABC):

    # Centralized default configuration values
    # timeout: connection timeout, read_timeout: max wait between two received bytes,
    # long enough for slow models (reasoning models, local Ollama on CPU)
    DEFAULT_CONFIG = {
        "temperature": 0.1,
        "max_tokens": 1000,
        "timeout": 30,
        "read_timeout": 600,
        "retry_attempts": 3,
    }

    RETRY_BACKOFF_BASE_SECONDS = 0.5
    RETRY_BACKOFF_MAX_SECONDS = 8.0
    RETRY_AFTER_MAX_SECONDS = 30.0
    ERROR_BODY_MAX_LENGTH = 500

    def __init__(self):
        self.llm: Any = None
        self.provider_name = self.__class__.__name__.replace("Provider", "").lower()
        self.config: Dict[str, Any] = {}
        self.request_id: Optional[str] = None

    @abstractmethod
    def initialize(self) -> bool:
        pass

    @abstractmethod
    def get_default_model(self) -> str:
        pass

    @abstractmethod
    def load_config(self, request_id: Optional[str] = None) -> Dict[str, Any]:
        pass

    @abstractmethod
    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        pass

    def get_default_config_value(self, key: str) -> Any:
        return self.DEFAULT_CONFIG.get(key)

    def is_available(self) -> bool:
        return self.llm is not None

    def get_model_name(self) -> str:
        return self.get_config_value("model_name") or self.get_default_model()

    def invoke(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        if not self.is_available():
            raise ValueError(
                f"{self.provider_name} provider is not properly initialized"
            )

        try:
            return self._invoke_with_logging_suppression(prompt, system_prompt)
        except Exception as e:
            logging.error(f"Error invoking {self.provider_name}: {str(e)}")
            raise

    def _invoke_with_logging_suppression(
        self, prompt: str, system_prompt: Optional[str] = None
    ) -> str:
        original_level = logging.getLogger().level
        logging.getLogger().setLevel(logging.WARNING)
        try:
            return self.generate(prompt, system_prompt)
        except Exception as e:
            logging.error(f"Error during LLM invocation: {str(e)}")
            raise
        finally:
            logging.getLogger().setLevel(original_level)

    # Prompt format of the text-completion providers (Ollama, Hugging Face)
    @staticmethod
    def build_text_prompt(prompt: str, system_prompt: Optional[str] = None) -> str:
        if system_prompt:
            return f"System: {system_prompt}\n\nUser: {prompt}"
        return prompt

    def get_config_value(self, key: str, default: Any = None) -> Any:
        # First check provider config, then fall back to centralized defaults, then provided default
        if key in self.config:
            return self.config[key]
        elif key in self.DEFAULT_CONFIG:
            return self.DEFAULT_CONFIG[key]
        else:
            return default

    def requires_api_key(self) -> bool:
        return self.provider_name not in [
            "ollama"
        ]  # Only Ollama doesn't require API key

    def create_http_session(self) -> requests.Session:
        session = requests.Session()
        session.headers.update({"User-Agent": "MegaLinter-LLM-Advisor"})
        return session

    # requests honors REQUESTS_CA_BUNDLE / CURL_CA_BUNDLE but not SSL_CERT_FILE /
    # SSL_CERT_DIR, that the previous httpx-based SDKs honored
    def get_ssl_verify(self) -> Union[bool, str]:
        for var_name in ["REQUESTS_CA_BUNDLE", "CURL_CA_BUNDLE"]:
            value = config.get(self.request_id, var_name, "")
            if value:
                return value
        for var_name in ["SSL_CERT_FILE", "SSL_CERT_DIR"]:
            value = config.get(self.request_id, var_name, "")
            if value and os.path.exists(value):
                return value
        return True

    def get_http_timeout(self) -> tuple[float, float]:
        return (
            float(self.get_config_value("timeout")),
            float(self.get_config_value("read_timeout")),
        )

    def is_retryable_status(self, status_code: int) -> bool:
        return status_code == 429 or status_code >= 500

    def get_retry_delay(self, attempt: int, retry_after: Optional[str] = None) -> float:
        if retry_after:
            retry_after_seconds = self.parse_retry_after(retry_after)
            if retry_after_seconds is not None:
                return min(max(retry_after_seconds, 0.0), self.RETRY_AFTER_MAX_SECONDS)
        return min(
            self.RETRY_BACKOFF_BASE_SECONDS * (2 ** (attempt - 1)),
            self.RETRY_BACKOFF_MAX_SECONDS,
        )

    @staticmethod
    def parse_retry_after(retry_after: str) -> Optional[float]:
        try:
            return float(retry_after)
        except ValueError:
            pass
        try:
            retry_date = email.utils.parsedate_to_datetime(retry_after)
        except (TypeError, ValueError):
            return None
        if retry_date.tzinfo is None:
            retry_date = retry_date.replace(tzinfo=timezone.utc)
        return (retry_date - datetime.now(timezone.utc)).total_seconds()

    def redact(self, text: str) -> str:
        api_key = self.get_config_value("api_key")
        if isinstance(api_key, str) and len(api_key) >= 4:
            text = text.replace(api_key, "***")
        return text

    def truncate(self, text: str) -> str:
        text = " ".join(text.split())
        if len(text) > self.ERROR_BODY_MAX_LENGTH:
            text = text[: self.ERROR_BODY_MAX_LENGTH] + "...(truncated)"
        return text

    def get_http_error_hint(self, response: requests.Response) -> str:
        return ""

    def format_http_error(self, response: requests.Response) -> str:
        message = f"{self.provider_name} API returned HTTP {response.status_code}"
        if response.reason:
            message += f" {response.reason}"
        body = self.truncate(response.text or "")
        if body:
            message += f": {body}"
        hint = self.get_http_error_hint(response)
        if hint:
            message += f" ({hint})"
        return self.redact(message)

    def post_json(
        self,
        url: str,
        payload: Dict[str, Any],
        headers: Optional[Dict[str, str]] = None,
        stream: bool = False,
    ) -> requests.Response:
        request_headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        if headers:
            request_headers.update(headers)
        attempts = max(1, int(self.get_config_value("retry_attempts")))
        timeout = self.get_http_timeout()
        verify = self.get_ssl_verify()
        attempt = 1
        while True:
            try:
                response = self.llm.post(
                    url,
                    headers=request_headers,
                    json=payload,
                    timeout=timeout,
                    verify=verify,
                    stream=stream,
                )
            except requests.exceptions.ConnectionError as e:
                # Includes ConnectTimeout: the request never reached the server
                if attempt >= attempts:
                    raise LLMProviderError(
                        self.redact(
                            f"{self.provider_name} API request failed after "
                            f"{attempt} attempt(s): {str(e)}"
                        )
                    ) from e
                reason = type(e).__name__
                delay = self.get_retry_delay(attempt)
            except requests.exceptions.Timeout as e:
                raise LLMProviderError(
                    self.redact(
                        f"{self.provider_name} API request timed out "
                        f"(no response within {timeout[1]}s): {str(e)}"
                    )
                ) from e
            else:
                if response.status_code < 400:
                    return response
                if attempt >= attempts or not self.is_retryable_status(
                    response.status_code
                ):
                    raise LLMProviderError(self.format_http_error(response))
                reason = f"HTTP {response.status_code}"
                delay = self.get_retry_delay(
                    attempt, response.headers.get("Retry-After")
                )
                response.close()
            logging.warning(
                f"[LLM Advisor] {self.provider_name} API request failed ({reason}), "
                f"retrying in {delay:.1f}s (attempt {attempt + 1}/{attempts})"
            )
            time.sleep(delay)
            attempt += 1

    def parse_json_response(self, response: requests.Response) -> Dict[str, Any]:
        try:
            data = response.json()
        except (ValueError, json.JSONDecodeError) as e:
            raise LLMProviderError(
                self.redact(
                    f"{self.provider_name} API returned a non-JSON response: "
                    f"{self.truncate(response.text or '')}"
                )
            ) from e
        if not isinstance(data, dict):
            raise LLMProviderError(
                f"{self.provider_name} API returned an unexpected response type: "
                f"{type(data).__name__}"
            )
        if data.get("error"):
            raise LLMProviderError(
                self.redact(
                    f"{self.provider_name} API returned an error: "
                    f"{self.truncate(json.dumps(data['error']))}"
                )
            )
        return data
