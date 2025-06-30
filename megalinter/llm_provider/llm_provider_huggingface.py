#!/usr/bin/env python3
"""
Hugging Face LLM Provider for MegaLinter
"""

import logging
from typing import Any, Dict

from megalinter import config

from .llm_provider import LLMProvider


class HuggingFaceProvider(LLMProvider):

    def get_default_model(self) -> str:
        return "microsoft/DialoGPT-medium"

    def load_config(self, request_id: str = None) -> Dict[str, Any]:
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
            # Check for required optional dependencies
            try:
                from langchain_huggingface import HuggingFacePipeline
                from transformers import pipeline
            except ImportError as e:
                logging.error(
                    f"Hugging Face dependencies not found: {str(e)}. "
                    f"Install in PRE_COMMANDS with: pip install langchain-huggingface transformers torch"
                )
                return False

            model_name = self.get_config_value("model_name") or self.get_default_model()
            task = self.get_config_value("task", "text-generation")
            device = self.get_config_value("device", -1)
            api_key = self.get_config_value("api_key")
            temperature = self.get_config_value("temperature")
            max_tokens = self.get_config_value("max_tokens")

            # Create Hugging Face pipeline
            hf_pipeline = pipeline(
                task=task,
                model=model_name,
                device=device,
                token=api_key if api_key else None,
            )

            self.llm = HuggingFacePipeline(
                pipeline=hf_pipeline,
                model_kwargs={"temperature": temperature, "max_length": max_tokens},
            )

            logging.info(f"Hugging Face provider initialized with model {model_name}")
            return True

        except ImportError:
            logging.error(
                "transformers library is required for Hugging Face integration. Install with: pip install megalinter[huggingface]"
            )
            return False
        except Exception as e:
            logging.error(f"Failed to initialize Hugging Face provider: {str(e)}")
            return False
