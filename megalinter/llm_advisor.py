#!/usr/bin/env python3
"""
LLM Advisor for MegaLinter
Provides AI-powered hints for fixing linter errors using various LLM providers through LangChain
"""

import logging
from typing import Any, Dict

from megalinter import config
from megalinter.llm_provider.llm_provider_factory import LLMProviderFactory


class LLMAdvisor:
    """
    AI-powered advisor for providing linter error fix suggestions using various LLM providers
    """

    def __init__(self, request_id: str = None):
        """Initialize LLM Advisor with configuration"""
        self.request_id = request_id
        self.enabled = False
        self.provider = None
        self.provider_name = None
        self.model_name = None

        # Load configuration
        self._load_config()

        # Initialize LLM provider if enabled
        if self.enabled:
            self._initialize_provider()

    def _load_config(self):
        """Load LLM configuration from environment/config"""
        self.enabled = (
            config.get(self.request_id, "LLM_ADVISOR_ENABLED", "false").lower()
            == "true"
        )

        if not self.enabled:
            return

        self.provider_name = config.get(
            self.request_id, "LLM_PROVIDER", "openai"
        ).lower()

    def _initialize_provider(self):
        """Initialize the LLM provider"""
        try:
            self.provider = LLMProviderFactory.create_provider(
                self.provider_name, self.request_id
            )

            if self.provider:
                self.model_name = (
                    self.provider.get_config_value("model_name")
                    or self.provider.get_default_model()
                )
                logging.info(
                    f"LLM Advisor initialized with {self.provider_name} ({self.model_name})"
                )
            else:
                self.enabled = False
                logging.error(f"Failed to create provider: {self.provider_name}")

        except Exception as e:
            logging.error(
                f"Failed to initialize LLM provider ({self.provider_name}): {str(e)}"
            )
            self.enabled = False
            self.provider = None

    def is_available(self) -> bool:
        """Check if LLM advisor is available and properly configured"""
        return (
            self.enabled and self.provider is not None and self.provider.is_available()
        )

    def get_supported_providers(self) -> Dict[str, str]:
        """Get list of supported providers"""
        return LLMProviderFactory.get_supported_providers()

    @property
    def SUPPORTED_PROVIDERS(self) -> Dict[str, str]:
        """Backwards compatibility property for supported providers"""
        return self.get_supported_providers()

    def get_fix_suggestions(
        self, linter_name: str, linter_output: str
    ) -> Dict[str, Any]:
        """
        Get AI-powered fix suggestions for linter errors

        Args:
            linter_name: Name of the linter
            linter_output: Full raw output from the linter

        Returns:
            Dictionary containing a single fix suggestion and metadata
        """
        if not self.is_available():
            return {"enabled": False, "suggestion": None}

        return self._get_suggestion_from_raw_output(linter_name, linter_output)

    def _get_suggestion_from_raw_output(
        self, linter_name: str, linter_output: str
    ) -> Dict[str, Any]:
        """
        Get AI suggestion directly from raw linter output

        Args:
            linter_name: Name of the linter
            linter_output: Full raw output from the linter

        Returns:
            Dictionary containing a single fix suggestion and metadata
        """
        try:
            # Build a prompt for analyzing the raw output
            prompt = self._build_raw_output_prompt(linter_name, linter_output)
            system_prompt = self._get_system_prompt()

            # Get response from LLM provider
            suggestion_text = self.provider.invoke(prompt, system_prompt)

            # Return as a single suggestion for the raw output
            suggestion = {"linter": linter_name, "suggestion": suggestion_text.strip()}

            return {
                "enabled": True,
                "provider": self.provider_name,
                "model": self.model_name,
                "suggestion": suggestion,
            }

        except Exception as e:
            logging.warning(f"Failed to get suggestion from raw output: {str(e)}")
            return {
                "enabled": True,
                "provider": self.provider_name,
                "model": self.model_name,
                "suggestion": None,
            }

    def _get_system_prompt(self) -> str:
        """Get the system prompt for the LLM"""
        return """You are an expert code reviewer and linter error analyst. Your job is to help developers understand and fix linting errors in their code.

For each linter error, provide:
1. A clear explanation of what the error means
2. Why this error occurs
3. Specific, actionable steps to fix it
4. If applicable, a code example showing the fix
5. Best practices to prevent similar errors

Keep your responses concise but comprehensive. Focus on practical solutions that developers can immediately apply.

Your response must not exceed 1000 characters, so prioritize the most critical issues and solutions. If there are multiple errors, focus on the most common or critical ones first."""

    def _build_raw_output_prompt(self, linter_name: str, linter_output: str) -> str:
        """Build a prompt for analyzing raw linter output"""
        # Truncate long output to avoid token limits
        max_output_length = 10000
        if len(linter_output) > max_output_length:
            linter_output = (
                linter_output[:max_output_length] + "\n\n(Output truncated...)"
            )

        prompt_parts = [
            f"Linter: {linter_name}",
            "",
            "Raw linter output:",
            "```",
            linter_output.strip(),
            "```",
            "",
            "Please analyze this linter output and provide:",
            "1. A summary of the main issues found",
            "2. General advice on how to fix the most common/critical issues",
            "3. Best practices to prevent these types of errors",
            "",
            "Focus on the most actionable and important suggestions.",
        ]

        return "\n".join(prompt_parts)

    def format_suggestions_for_output(self, suggestions_data: Dict[str, Any]) -> str:
        """Format suggestion for display in reports"""
        if not suggestions_data.get("enabled", False):
            return ""

        suggestion = suggestions_data.get("suggestion")
        if not suggestion:
            return "No AI suggestions available for the detected errors."

        output_lines = [
            f"## 🤖 AI-Powered Fix Suggestions ({suggestions_data['provider']} - {suggestions_data['model']})",
            "",
            f"**{suggestion['linter']} - AI Analysis:**",
            "",
            suggestion["suggestion"],
            "",
            "---",
            "",
        ]

        return "\n".join(output_lines)
