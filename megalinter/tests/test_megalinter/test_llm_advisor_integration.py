#!/usr/bin/env python3
"""
Integration test for LLM Advisor with MegaLinter reporting
"""

import os
import sys
import unittest
from unittest.mock import Mock, patch

# Add megalinter to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from megalinter.llm_advisor import LLMAdvisor


class TestLLMAdvisorIntegration(unittest.TestCase):
    """Test LLM Advisor integration with MegaLinter"""

    def setUp(self):
        """Set up test fixtures"""
        pass

    @patch("megalinter.config.get")
    @patch(
        "megalinter.llm_provider.llm_provider_factory.LLMProviderFactory.create_provider"
    )
    def test_llm_advisor_initialization(self, mock_create_provider, mock_config):
        """Test LLM advisor initialization"""
        # Mock configuration
        mock_config.side_effect = lambda req_id, key, default: {
            "LLM_ADVISOR_ENABLED": "true",
            "LLM_PROVIDER": "openai",
            "LLM_MODEL_NAME": "gpt-3.5-turbo",
            "LLM_MAX_TOKENS": "1000",
            "LLM_TEMPERATURE": "0.1",
            "OPENAI_API_KEY": "test-key",
        }.get(key, default)

        # Mock provider
        mock_provider = Mock()
        mock_provider.get_config_value.return_value = "gpt-3.5-turbo"
        mock_provider.get_default_model.return_value = "gpt-3.5-turbo"
        mock_provider.is_available.return_value = True
        mock_create_provider.return_value = mock_provider

        advisor = LLMAdvisor("test-request")

        self.assertTrue(advisor.enabled)
        self.assertEqual(advisor.provider_name, "openai")
        self.assertEqual(advisor.model_name, "gpt-3.5-turbo")
        self.assertIsNotNone(advisor.provider)

    @patch("megalinter.config.get")
    @patch(
        "megalinter.llm_provider.llm_provider_factory.LLMProviderFactory.create_provider"
    )
    def test_ai_suggestions_with_linter_output(self, mock_create_provider, mock_config):
        """Test AI suggestions generation with real linter output"""
        # Mock configuration
        mock_config.side_effect = lambda req_id, key, default: {
            "LLM_ADVISOR_ENABLED": "true",
            "LLM_PROVIDER": "openai",
        }.get(key, default)

        # Mock provider
        mock_provider = Mock()
        mock_provider.get_config_value.return_value = "gpt-3.5-turbo"
        mock_provider.get_default_model.return_value = "gpt-3.5-turbo"
        mock_provider.is_available.return_value = True
        mock_provider.invoke.return_value = (
            "Remove the unused import statement to clean up your code"
        )
        mock_create_provider.return_value = mock_provider

        advisor = LLMAdvisor("test-request")

        # Test with real linter output
        linter_output = "test.py:10:5: F401 'os' imported but unused\nfile.py:20:1: E302 expected 2 blank lines"
        result = advisor.get_fix_suggestions("flake8", linter_output)

        # Verify result structure
        self.assertTrue(result["enabled"])
        self.assertEqual(result["provider"], "openai")
        self.assertEqual(result["model"], "gpt-3.5-turbo")
        self.assertIsNotNone(result["suggestion"])
        self.assertEqual(result["suggestion"]["linter"], "flake8")
        self.assertIn("Remove the unused import", result["suggestion"]["suggestion"])

        # Verify provider was called correctly
        mock_provider.invoke.assert_called_once()
        call_args = mock_provider.invoke.call_args
        self.assertIn("flake8", call_args[0][0])  # prompt contains linter name
        self.assertIn("F401", call_args[0][0])  # prompt contains the error

    def test_raw_output_processing(self):
        """Test raw linter output processing"""
        linter_output = """test.py:10:5: F401 'os' imported but unused
style.css:23:12: block-no-empty Unexpected empty block
script.js:8:1: no-undef 'console' is not defined"""

        # Test that the advisor can process raw output
        with patch("megalinter.config.get") as mock_config:
            mock_config.side_effect = lambda req_id, key, default: {
                "LLM_ADVISOR_ENABLED": "false",  # Disabled for this test
            }.get(key, default)

            advisor = LLMAdvisor()

            # Should return disabled result
            result = advisor.get_fix_suggestions("test_linter", linter_output)
            self.assertFalse(result["enabled"])
            self.assertIsNone(result["suggestion"])

    def test_disabled_when_advisor_disabled(self):
        """Test that LLM advisor is disabled when configuration is disabled"""
        with patch("megalinter.config.get") as mock_config:
            mock_config.side_effect = lambda req_id, key, default: {
                "LLM_ADVISOR_ENABLED": "false",
            }.get(key, default)

            advisor = LLMAdvisor()
            self.assertFalse(advisor.is_available())

    @patch("megalinter.config.get")
    def test_ai_suggestions_not_available_when_disabled(self, mock_config):
        """Test that AI suggestions are not available when LLM advisor is disabled"""
        mock_config.side_effect = lambda req_id, key, default: {
            "LLM_ADVISOR_ENABLED": "false"
        }.get(key, default)

        advisor = LLMAdvisor()

        # Test with linter output
        linter_output = "test.py:10:5: F401 'os' imported but unused"
        result = advisor.get_fix_suggestions("flake8", linter_output)

        # Should return disabled result
        self.assertFalse(result["enabled"])
        self.assertIsNone(result["suggestion"])

    @patch("megalinter.config.get")
    @patch(
        "megalinter.llm_provider.llm_provider_factory.LLMProviderFactory.create_provider"
    )
    def test_format_suggestions_for_output(self, mock_create_provider, mock_config):
        """Test formatting suggestions for output"""
        # Mock configuration
        mock_config.side_effect = lambda req_id, key, default: {
            "LLM_ADVISOR_ENABLED": "true",
            "LLM_PROVIDER": "openai",
        }.get(key, default)

        # Mock provider
        mock_provider = Mock()
        mock_provider.get_config_value.return_value = "gpt-3.5-turbo"
        mock_provider.get_default_model.return_value = "gpt-3.5-turbo"
        mock_provider.is_available.return_value = True
        mock_create_provider.return_value = mock_provider

        advisor = LLMAdvisor("test-request")

        # Test formatting
        suggestions_data = {
            "enabled": True,
            "provider": "openai",
            "model": "gpt-3.5-turbo",
            "suggestion": {
                "linter": "flake8",
                "suggestion": "Remove unused imports to clean up your code",
            },
        }

        formatted = advisor.format_suggestions_for_output(suggestions_data)

        self.assertIn("AI-Powered Fix Suggestions", formatted)
        self.assertIn("openai - gpt-3.5-turbo", formatted)
        self.assertIn("flake8 - AI Analysis", formatted)
        self.assertIn("Remove unused imports", formatted)

    @patch("megalinter.config.get")
    def test_disabled_formatting(self, mock_config):
        """Test formatting when advisor is disabled"""
        mock_config.side_effect = lambda req_id, key, default: {
            "LLM_ADVISOR_ENABLED": "false"
        }.get(key, default)

        advisor = LLMAdvisor()

        suggestions_data = {"enabled": False, "suggestion": None}
        formatted = advisor.format_suggestions_for_output(suggestions_data)

        self.assertEqual(formatted, "")

    @patch("megalinter.config.get")
    @patch(
        "megalinter.llm_provider.llm_provider_factory.LLMProviderFactory.create_provider"
    )
    def test_prompt_building_with_various_linter_outputs(
        self, mock_create_provider, mock_config
    ):
        """Test that prompts are built correctly for different linter outputs"""
        # Mock configuration
        mock_config.side_effect = lambda req_id, key, default: {
            "LLM_ADVISOR_ENABLED": "true",
            "LLM_PROVIDER": "openai",
        }.get(key, default)

        # Mock provider
        mock_provider = Mock()
        mock_provider.get_config_value.return_value = "gpt-3.5-turbo"
        mock_provider.get_default_model.return_value = "gpt-3.5-turbo"
        mock_provider.is_available.return_value = True
        mock_provider.invoke.return_value = "Test suggestion"
        mock_create_provider.return_value = mock_provider

        advisor = LLMAdvisor("test-request")

        # Test with different linter outputs
        test_cases = [
            (
                "pylint",
                "module.py:1:0: C0111: Missing module docstring (missing-docstring)",
            ),
            ("flake8", "test.py:10:5: F401 'os' imported but unused"),
            (
                "eslint",
                "file.js:15:1: error no-unused-vars 'variable' is defined but never used",
            ),
        ]

        for linter_name, linter_output in test_cases:
            with self.subTest(linter=linter_name):
                result = advisor.get_fix_suggestions(linter_name, linter_output)

                # Verify the provider was called
                mock_provider.invoke.assert_called()
                call_args = mock_provider.invoke.call_args
                prompt = call_args[0][0]

                # Verify prompt contains expected elements
                self.assertIn(linter_name, prompt)
                self.assertIn(linter_output, prompt)
                self.assertIn("Raw linter output:", prompt)

                # Verify result structure
                self.assertTrue(result["enabled"])
                self.assertEqual(result["suggestion"]["linter"], linter_name)

        # Verify the provider was called for each test case
        self.assertEqual(mock_provider.invoke.call_count, len(test_cases))


if __name__ == "__main__":
    unittest.main()
