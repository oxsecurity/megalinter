#!/usr/bin/env python3
"""
Hugging Face LLM Provider for MegaLinter
"""

import logging
from typing import Any, Dict, Optional

from megalinter import config

from .llm_provider import LLMProvider, LLMProviderError


class HuggingFaceProvider(LLMProvider):

    # Response key holding the generated text, by pipeline task
    TASK_TEXT_KEYS = {
        "text-generation": "generated_text",
        "text2text-generation": "generated_text",
        "image-text-to-text": "generated_text",
        "summarization": "summary_text",
        "translation": "translation_text",
    }

    def get_default_model(self) -> str:
        return "microsoft/DialoGPT-medium"

    def load_config(self, request_id: Optional[str] = None) -> Dict[str, Any]:
        return {
            "api_key": config.get(request_id, "HUGGINGFACE_API_TOKEN", ""),
            "task": config.get(request_id, "HUGGINGFACE_TASK", "text-generation"),
            "device": config.get(
                request_id, "HUGGINGFACE_DEVICE", -1
            ),  # -1 for CPU, 0+ for GPU
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
            # Optional dependencies, not installed in MegaLinter images (local inference)
            try:
                from transformers import pipeline
            except ImportError as e:
                logging.error(
                    f"Hugging Face dependencies not found: {str(e)}. "
                    f"Install in PRE_COMMANDS with: pip install transformers torch"
                )
                return False

            model_name = self.get_model_name()
            task = self.get_config_value("task", "text-generation")
            device = self.get_config_value("device", -1)
            api_key = self.get_config_value("api_key")

            self.llm = pipeline(
                task=task,
                model=model_name,
                device=device,
                token=api_key if api_key else None,
            )

            logging.debug(f"Hugging Face provider initialized with model {model_name}")
            return True

        except Exception as e:
            logging.error(f"Failed to initialize Hugging Face provider: {str(e)}")
            return False

    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        responses = self.llm([self.build_text_prompt(prompt, system_prompt)])
        if not responses:
            raise LLMProviderError("Hugging Face pipeline returned no result")
        response = responses[0]
        # The pipeline returns a list when the model produces several generations
        if isinstance(response, list):
            response = response[0]
        task = getattr(self.llm, "task", None) or self.get_config_value(
            "task", "text-generation"
        )
        if task not in self.TASK_TEXT_KEYS:
            raise LLMProviderError(
                f"Unsupported Hugging Face task {task}, supported tasks: "
                f"{', '.join(self.TASK_TEXT_KEYS.keys())}"
            )
        return response[self.TASK_TEXT_KEYS[task]]
