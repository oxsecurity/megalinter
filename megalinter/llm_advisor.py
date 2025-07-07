#!/usr/bin/env python3
# flake8: noqa: E501
"""
LLM Advisor for MegaLinter
Provides AI-powered hints for fixing linter errors using various LLM providers through LangChain
"""

import logging
from typing import Any, Dict, Optional

from megalinter import config
from megalinter.llm_provider.llm_provider_factory import LLMProviderFactory


class LLMAdvisor:

    def __init__(self, request_id: Optional[str] = None):
        self.request_id = request_id
        self.enabled = False
        self.provider = None
        self.provider_name = None
        self.model_name = None
        self.advisor_level = "ERROR"  # Always set, even if disabled
        self.enable_linters: list[str] = []
        self.disable_linters: list[str] = []

        # Load configuration
        self._load_config()

        # Initialize LLM provider if enabled
        if self.enabled:
            self._initialize_provider()

    def _load_config(self):
        self.advisor_level = config.get(
            self.request_id, "LLM_ADVISOR_LEVEL", "ERROR"
        ).upper()
        self.enable_linters = []
        self.disable_linters = []
        self.enabled = (
            config.get(self.request_id, "LLM_ADVISOR_ENABLED", "false").lower()
            == "true"
        )

        if not self.enabled:
            return

        self.provider_name = config.get(
            self.request_id, "LLM_PROVIDER", "openai"
        ).lower()

        # Allow test override for API key check
        if (
            config.get(self.request_id, "LLM_TEST_API_KEY_PRESENT", "false").lower()
            == "true"
        ):
            api_key_present = True
        else:
            supported_providers_api_keys = (
                LLMProviderFactory.get_supported_providers_api_key_var_names()
            )
            api_key_present = any(
                config.get(self.request_id, key, None)
                for key in supported_providers_api_keys
            )
        if not api_key_present:
            self.enabled = False
            return

        # Validate advisor level
        if self.advisor_level not in ["ERROR", "WARNING"]:
            logging.warning(
                f"Invalid LLM_ADVISOR_LEVEL '{self.advisor_level}'. Using 'ERROR' as default."
            )
            self.advisor_level = "ERROR"

        # Load linter-specific enable/disable lists
        self.enable_linters = config.get_list(
            self.request_id, "LLM_ADVISOR_ENABLE_LINTERS", []
        )
        self.disable_linters = config.get_list(
            self.request_id, "LLM_ADVISOR_DISABLE_LINTERS", []
        )

    def _initialize_provider(self):
        try:
            self.provider = LLMProviderFactory.create_provider(
                self.provider_name, self.request_id
            )

            if self.provider:
                self.model_name = (
                    self.provider.get_config_value("model_name")
                    or self.provider.get_default_model()
                )
                logging.debug(
                    f"[LLM Advisor] LLM Advisor initialized with {self.provider_name} ("
                    f"{self.model_name})"
                )
            else:
                self.enabled = False
                logging.error(
                    f"[LLM Advisor] Failed to create provider: {self.provider_name}"
                )

        except Exception as e:
            logging.error(
                f"[LLM Advisor] Failed to initialize LLM provider ({self.provider_name}): {str(e)}"
            )
            self.enabled = False
            self.provider = None

    def is_available(self) -> bool:
        return (
            self.enabled and self.provider is not None and self.provider.is_available()
        )

    def get_supported_providers(self) -> Dict[str, str]:
        return LLMProviderFactory.get_supported_providers()

    def get_fix_suggestions(
        self, linter: Any, linter_output: str
    ) -> Optional[dict[str, Any]]:
        if not self.is_available():
            return None
        return self._get_suggestion_from_raw_output(linter, linter_output)

    def _get_suggestion_from_raw_output(
        self, linter: Any, linter_output: str
    ) -> Optional[dict[str, Any]]:
        try:
            # Build a prompt for analyzing the raw output
            prompt = self._build_raw_output_prompt(linter, linter_output)
            system_prompt = self._get_system_prompt()

            # Get response from LLM provider
            if self.provider is None:
                return None
            suggestion_text = self.provider.invoke(prompt, system_prompt)

            return {
                "provider": self.provider_name,
                "model": self.model_name,
                "linter": linter.name,
                "text": suggestion_text.strip(),
            }

        except Exception as e:
            logging.warning(f"Failed to get suggestion from raw output: {str(e)}")
            return None

    def _get_system_prompt(self) -> str:
        return """You are an expert code reviewer and linter error analyst. Your job is to help developers understand and fix linting errors in their code. Linters have been run by MegaLinter.

For each error, provide:
1. A clear explanation of what the error means
2. Why this error occurs
3. Specific, actionable steps to fix it
4. If applicable, a code example showing the fix

Keep your responses concise but comprehensive. Focus on practical solutions that developers can immediately apply.

Your response must not exceed 1000 characters, so prioritize the most critical issues and solutions. If there are multiple errors, focus on the most common or critical ones first."""

    def _build_raw_output_prompt(self, linter: Any, linter_output: str) -> str:
        # Truncate long output to avoid token limits
        max_output_length = 10000
        if len(linter_output) > max_output_length:
            linter_output = (
                linter_output[:max_output_length] + "\n\n(Output truncated...)"
            )
        commands_part = []
        if hasattr(linter, "lint_command_log") and len(linter.lint_command_log) == 1:
            end = "" if len(linter.lint_command_log[0]) < 250 else "...(truncated)"
            commands_part += [
                "Command used to run the linter:",
                f"`{linter.lint_command_log[0][:250]}{end}`",
            ]
        elif hasattr(linter, "lint_command_log") and len(linter.lint_command_log) > 1:
            commands_part += ["Commands used to run the linter:"]
            for command_log in linter.lint_command_log:
                end = "" if len(command_log) < 250 else "...(truncated)"
                commands_part += [f"`{command_log[:250]}{end}`"]
        prompt_parts = [f"Linter: {linter.linter_name}", ""]
        prompt_parts += commands_part
        prompt_parts += [
            "",
            "Raw linter output:",
            "```",
            linter_output.strip(),
            "```",
            "",
            "Please analyze this linter output and provide:",
            "1. A summary of the main issues found",
            "2. General advice on how to fix the most common/critical issues",
            "",
            "Stay concise, and focus on the most actionable and important suggestions.",
        ]

        return "\n".join(prompt_parts)

    def should_analyze_linter(self, linter) -> bool:
        if not self.is_available():
            return False

        # Check linter-specific enable/disable lists first
        # If both are set, enable list wins
        if len(self.enable_linters) > 0:
            if linter.name not in self.enable_linters:
                return False
        elif len(self.disable_linters) > 0:
            if linter.name in self.disable_linters:
                return False

        # Check if linter has any issues to analyze
        has_errors_or_warnings = (
            linter.number_errors > 0 or linter.total_number_warnings > 0
        )

        if not has_errors_or_warnings:
            return False

        # Determine if this is an error linter (blocking) or warning linter (non-blocking)
        is_error_linter = linter.return_code != 0
        is_warning_linter = linter.return_code == 0 and has_errors_or_warnings

        # Always analyze error linters (blocking linters)
        if is_error_linter:
            return True

        # Only analyze warning linters (non-blocking) if level is set to WARNING
        if self.advisor_level == "WARNING" and is_warning_linter:
            return True

        return False
