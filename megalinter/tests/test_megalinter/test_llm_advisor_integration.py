#!/usr/bin/env python3
"""
Integration test for LLM Advisor with MegaLinter reporting
"""

import os
import sys
import unittest
from unittest.mock import Mock, patch

from megalinter.llm_advisor import LLMAdvisor

# Add megalinter to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))


class TestLLMAdvisorIntegration(unittest.TestCase):
    def setUp(self):
        pass

    @patch("megalinter.config.get")
    @patch(
        "megalinter.llm_provider.llm_provider_factory.LLMProviderFactory.create_provider"
    )
    def test_llm_advisor_initialization(self, mock_create_provider, mock_config):

        # Mock configuration
        mock_config.side_effect = lambda req_id, key, default: {
            "LLM_ADVISOR_ENABLED": "true",
            "LLM_PROVIDER": "openai",
            "LLM_MODEL_NAME": "gpt-3.5-turbo",
            "LLM_MAX_TOKENS": "1000",
            "LLM_TEMPERATURE": "0.1",
            "OPENAI_API_KEY": "test-key",
            "LLM_TEST_API_KEY_PRESENT": "true",
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

        # Mock configuration
        mock_config.side_effect = lambda req_id, key, default: {
            "LLM_ADVISOR_ENABLED": "true",
            "LLM_PROVIDER": "openai",
            "LLM_TEST_API_KEY_PRESENT": "true",
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

        # Create mock linter object
        mock_linter = Mock()
        mock_linter.name = "PYTHON_FLAKE8"
        mock_linter.linter_name = "flake8"
        mock_linter.lint_command_log = ["flake8 test.py"]

        # Test with real linter output
        linter_output = "test.py:10:5: F401 'os' imported but unused\nfile.py:20:1: E302 expected 2 blank lines"
        result = advisor.get_fix_suggestions(mock_linter, linter_output)

        # Verify result structure
        self.assertIsNotNone(result)
        self.assertEqual(result["provider"], "openai")
        self.assertEqual(result["model"], "gpt-3.5-turbo")
        self.assertEqual(result["linter"], "PYTHON_FLAKE8")
        self.assertIn("Remove the unused import", result["text"])

        # Verify provider was called correctly
        mock_provider.invoke.assert_called_once()
        call_args = mock_provider.invoke.call_args
        self.assertIn("flake8", call_args[0][0])  # prompt contains linter name
        self.assertIn("F401", call_args[0][0])  # prompt contains the error

    def test_raw_output_processing(self):

        linter_output = """test.py:10:5: F401 'os' imported but unused
style.css:23:12: block-no-empty Unexpected empty block
script.js:8:1: no-undef 'console' is not defined"""

        # Test that the advisor can process raw output
        with patch("megalinter.config.get") as mock_config:
            mock_config.side_effect = lambda req_id, key, default: {
                "LLM_ADVISOR_ENABLED": "false",  # Disabled for this test
            }.get(key, default)

            advisor = LLMAdvisor()

            # Create mock linter object
            mock_linter = Mock()
            mock_linter.name = "TEST_LINTER"
            mock_linter.linter_name = "test_linter"
            mock_linter.lint_command_log = ["test_linter input.py"]

            # Should return None when disabled
            result = advisor.get_fix_suggestions(mock_linter, linter_output)
            self.assertIsNone(result)

    def test_disabled_when_advisor_disabled(self):

        with patch("megalinter.config.get") as mock_config:
            mock_config.side_effect = lambda req_id, key, default: {
                "LLM_ADVISOR_ENABLED": "false",
            }.get(key, default)

            advisor = LLMAdvisor()
            self.assertFalse(advisor.is_available())

    @patch("megalinter.config.get")
    def test_ai_suggestions_not_available_when_disabled(self, mock_config):

        mock_config.side_effect = lambda req_id, key, default: {
            "LLM_ADVISOR_ENABLED": "false"
        }.get(key, default)

        advisor = LLMAdvisor()

        # Create mock linter object
        mock_linter = Mock()
        mock_linter.name = "PYTHON_FLAKE8"
        mock_linter.linter_name = "flake8"
        mock_linter.lint_command_log = ["flake8 test.py"]

        # Test with linter output
        linter_output = "test.py:10:5: F401 'os' imported but unused"
        result = advisor.get_fix_suggestions(mock_linter, linter_output)

        # Should return None when disabled
        self.assertIsNone(result)

    @patch("megalinter.config.get")
    @patch(
        "megalinter.llm_provider.llm_provider_factory.LLMProviderFactory.create_provider"
    )
    def test_get_fix_suggestions_data_structure(
        self, mock_create_provider, mock_config
    ):

        # Mock configuration
        mock_config.side_effect = lambda req_id, key, default: {
            "LLM_ADVISOR_ENABLED": "true",
            "LLM_PROVIDER": "openai",
            "LLM_TEST_API_KEY_PRESENT": "true",
        }.get(key, default)

        # Mock provider
        mock_provider = Mock()
        mock_provider.get_config_value.return_value = "gpt-3.5-turbo"
        mock_provider.get_default_model.return_value = "gpt-3.5-turbo"
        mock_provider.is_available.return_value = True
        mock_provider.invoke.return_value = (
            "Remove unused imports to clean up your code"
        )
        mock_create_provider.return_value = mock_provider

        advisor = LLMAdvisor("test-request")

        # Create mock linter object
        mock_linter = Mock()
        mock_linter.name = "PYTHON_FLAKE8"
        mock_linter.linter_name = "flake8"
        mock_linter.lint_command_log = ["flake8 test.py"]

        # Test getting suggestions
        result = advisor.get_fix_suggestions(
            mock_linter, "test.py:1:1: F401 'os' imported but unused"
        )

        # Verify data structure
        self.assertIsNotNone(result)
        self.assertEqual(result["provider"], "openai")
        self.assertEqual(result["model"], "gpt-3.5-turbo")
        self.assertEqual(result["linter"], "PYTHON_FLAKE8")
        self.assertIn("Remove unused imports", result["text"])

    @patch("megalinter.config.get")
    def test_disabled_advisor_returns_proper_structure(self, mock_config):

        mock_config.side_effect = lambda req_id, key, default: {
            "LLM_ADVISOR_ENABLED": "false"
        }.get(key, default)

        advisor = LLMAdvisor()

        # Create mock linter object
        mock_linter = Mock()
        mock_linter.name = "PYTHON_FLAKE8"
        mock_linter.linter_name = "flake8"
        mock_linter.lint_command_log = ["flake8 test.py"]

        result = advisor.get_fix_suggestions(
            mock_linter, "test.py:1:1: F401 'os' imported but unused"
        )

        self.assertIsNone(result)

    @patch("megalinter.config.get")
    @patch(
        "megalinter.llm_provider.llm_provider_factory.LLMProviderFactory.create_provider"
    )
    def test_prompt_building_with_various_linter_outputs(
        self, mock_create_provider, mock_config
    ):

        # Mock configuration
        mock_config.side_effect = lambda req_id, key, default: {
            "LLM_ADVISOR_ENABLED": "true",
            "LLM_PROVIDER": "openai",
            "LLM_TEST_API_KEY_PRESENT": "true",
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
                "PYTHON_PYLINT",
                "pylint",
                "module.py:1:0: C0111: Missing module docstring (missing-docstring)",
            ),
            ("PYTHON_FLAKE8", "flake8", "test.py:10:5: F401 'os' imported but unused"),
            (
                "JAVASCRIPT_ESLINT",
                "eslint",
                "file.js:15:1: error no-unused-vars 'variable' is defined but never used",
            ),
        ]

        for linter_key, linter_name, linter_output in test_cases:
            with self.subTest(linter=linter_name):
                # Create mock linter object
                mock_linter = Mock()
                mock_linter.name = linter_key
                mock_linter.linter_name = linter_name
                mock_linter.lint_command_log = [f"{linter_name} input.py"]

                result = advisor.get_fix_suggestions(mock_linter, linter_output)

                # Verify the provider was called
                mock_provider.invoke.assert_called()
                call_args = mock_provider.invoke.call_args
                prompt = call_args[0][0]

                # Verify prompt contains expected elements
                self.assertIn(linter_name, prompt)
                self.assertIn(linter_output, prompt)
                self.assertIn("Raw linter output:", prompt)

                # Verify result structure
                self.assertIsNotNone(result)
                self.assertEqual(result["linter"], linter_key)
                self.assertEqual(result["provider"], "openai")
                self.assertEqual(result["model"], "gpt-3.5-turbo")
                self.assertEqual(result["text"], "Test suggestion")

        # Verify the provider was called for each test case
        self.assertEqual(mock_provider.invoke.call_count, len(test_cases))

    @patch("megalinter.config.get")
    @patch(
        "megalinter.llm_provider.llm_provider_factory.LLMProviderFactory.create_provider"
    )
    def test_llm_advisor_level_error_default(self, mock_create_provider, mock_config):

        # Mock configuration - no LLM_ADVISOR_LEVEL specified
        mock_config.side_effect = lambda req_id, key, default: {
            "LLM_ADVISOR_ENABLED": "true",
            "LLM_PROVIDER": "openai",
            "LLM_TEST_API_KEY_PRESENT": "true",
        }.get(key, default)

        # Mock provider
        mock_provider = Mock()
        mock_provider.get_config_value.return_value = "gpt-3.5-turbo"
        mock_provider.get_default_model.return_value = "gpt-3.5-turbo"
        mock_provider.is_available.return_value = True
        mock_create_provider.return_value = mock_provider

        advisor = LLMAdvisor("test-request")

        self.assertEqual(advisor.advisor_level, "ERROR")

    @patch("megalinter.config.get")
    @patch(
        "megalinter.llm_provider.llm_provider_factory.LLMProviderFactory.create_provider"
    )
    def test_llm_advisor_level_warning(self, mock_create_provider, mock_config):

        # Mock configuration with WARNING level
        mock_config.side_effect = lambda req_id, key, default: {
            "LLM_ADVISOR_ENABLED": "true",
            "LLM_PROVIDER": "openai",
            "LLM_ADVISOR_LEVEL": "WARNING",
            "LLM_TEST_API_KEY_PRESENT": "true",
        }.get(key, default)

        # Mock provider
        mock_provider = Mock()
        mock_provider.get_config_value.return_value = "gpt-3.5-turbo"
        mock_provider.get_default_model.return_value = "gpt-3.5-turbo"
        mock_provider.is_available.return_value = True
        mock_create_provider.return_value = mock_provider

        advisor = LLMAdvisor("test-request")

        self.assertEqual(advisor.advisor_level, "WARNING")

    @patch("megalinter.config.get")
    @patch(
        "megalinter.llm_provider.llm_provider_factory.LLMProviderFactory.create_provider"
    )
    def test_llm_advisor_level_invalid_fallback(
        self, mock_create_provider, mock_config
    ):

        # Mock configuration with invalid level
        mock_config.side_effect = lambda req_id, key, default: {
            "LLM_ADVISOR_ENABLED": "true",
            "LLM_PROVIDER": "openai",
            "LLM_ADVISOR_LEVEL": "INVALID",
            "LLM_TEST_API_KEY_PRESENT": "true",
        }.get(key, default)

        # Mock provider
        mock_provider = Mock()
        mock_provider.get_config_value.return_value = "gpt-3.5-turbo"
        mock_provider.get_default_model.return_value = "gpt-3.5-turbo"
        mock_provider.is_available.return_value = True
        mock_create_provider.return_value = mock_provider

        advisor = LLMAdvisor("test-request")

        self.assertEqual(advisor.advisor_level, "ERROR")

    @patch("megalinter.config.get_list")
    @patch("megalinter.config.get")
    @patch(
        "megalinter.llm_provider.llm_provider_factory.LLMProviderFactory.create_provider"
    )
    def test_should_analyze_linter_error_level(
        self, mock_create_provider, mock_config, mock_config_list
    ):

        mock_config_list.side_effect = lambda req_id, key, default: []

        # Mock linter with errors (blocking - return_code != 0)
        mock_linter_errors = Mock()
        mock_linter_errors.number_errors = 2
        mock_linter_errors.total_number_warnings = 0
        mock_linter_errors.return_code = 1  # Blocking

        # Mock linter with warnings only (non-blocking - return_code == 0)
        mock_linter_warnings = Mock()
        mock_linter_warnings.number_errors = 0
        mock_linter_warnings.total_number_warnings = 3
        mock_linter_warnings.return_code = 0  # Non-blocking

        # Mock linter with both errors and warnings (blocking)
        mock_linter_both = Mock()
        mock_linter_both.number_errors = 1
        mock_linter_both.total_number_warnings = 2
        mock_linter_both.return_code = 1  # Blocking

        # Mock linter with ignored/non-blocking errors
        mock_linter_ignored_errors = Mock()
        mock_linter_ignored_errors.number_errors = 2
        mock_linter_ignored_errors.total_number_warnings = 0
        mock_linter_ignored_errors.return_code = 0  # Non-blocking (ignored errors)

        with patch("megalinter.config.get") as mock_config:
            mock_config.side_effect = lambda req_id, key, default: {
                "LLM_ADVISOR_ENABLED": "false",  # Disabled for this test
                "LLM_ADVISOR_LEVEL": "ERROR",
            }.get(key, default)

            advisor = LLMAdvisor()
            advisor.advisor_level = "ERROR"  # Set manually since provider is disabled

            # Should not analyze any linters when disabled
            self.assertFalse(advisor.should_analyze_linter(mock_linter_errors))
            self.assertFalse(advisor.should_analyze_linter(mock_linter_warnings))
            self.assertFalse(advisor.should_analyze_linter(mock_linter_both))
            self.assertFalse(advisor.should_analyze_linter(mock_linter_ignored_errors))

        # Test with enabled advisor
        with (
            patch("megalinter.config.get") as mock_config,
            patch(
                "megalinter.llm_provider.llm_provider_factory.LLMProviderFactory.create_provider"
            ) as mock_create_provider,
        ):

            mock_config.side_effect = lambda req_id, key, default: {
                "LLM_ADVISOR_ENABLED": "true",
                "LLM_PROVIDER": "openai",
                "LLM_ADVISOR_LEVEL": "ERROR",
                "LLM_TEST_API_KEY_PRESENT": "true",
            }.get(key, default)

            # Mock provider
            mock_provider = Mock()
            mock_provider.get_config_value.return_value = "gpt-3.5-turbo"
            mock_provider.get_default_model.return_value = "gpt-3.5-turbo"
            mock_provider.is_available.return_value = True
            mock_create_provider.return_value = mock_provider

            advisor = LLMAdvisor("test-request")

            # Should analyze only blocking linters (return_code != 0)
            self.assertTrue(
                advisor.should_analyze_linter(mock_linter_errors)
            )  # Blocking errors
            self.assertFalse(
                advisor.should_analyze_linter(mock_linter_warnings)
            )  # Non-blocking warnings
            self.assertTrue(
                advisor.should_analyze_linter(mock_linter_both)
            )  # Blocking errors+warnings
            self.assertFalse(
                advisor.should_analyze_linter(mock_linter_ignored_errors)
            )  # Non-blocking ignored errors

    @patch("megalinter.config.get_list")
    @patch("megalinter.config.get")
    @patch(
        "megalinter.llm_provider.llm_provider_factory.LLMProviderFactory.create_provider"
    )
    def test_should_analyze_linter_warning_level(
        self, mock_create_provider, mock_config, mock_config_list
    ):

        mock_config_list.side_effect = lambda req_id, key, default: []
        mock_config.side_effect = lambda req_id, key, default: {
            "LLM_ADVISOR_ENABLED": "true",
            "LLM_PROVIDER": "openai",
            "LLM_ADVISOR_LEVEL": "WARNING",
            "LLM_TEST_API_KEY_PRESENT": "true",
        }.get(key, default)

        # Mock linter with errors (blocking)
        mock_linter_errors = Mock()
        mock_linter_errors.number_errors = 2
        mock_linter_errors.total_number_warnings = 0
        mock_linter_errors.return_code = 1  # Blocking

        # Mock linter with warnings only (non-blocking)
        mock_linter_warnings = Mock()
        mock_linter_warnings.number_errors = 0
        mock_linter_warnings.total_number_warnings = 3
        mock_linter_warnings.return_code = 0  # Non-blocking

        # Mock linter with both errors and warnings (blocking)
        mock_linter_both = Mock()
        mock_linter_both.number_errors = 1
        mock_linter_both.total_number_warnings = 2
        mock_linter_both.return_code = 1  # Blocking

        # Mock linter with ignored/non-blocking errors
        mock_linter_ignored_errors = Mock()
        mock_linter_ignored_errors.number_errors = 2
        mock_linter_ignored_errors.total_number_warnings = 0
        mock_linter_ignored_errors.return_code = 0  # Non-blocking (ignored errors)

        # Mock linter with no issues
        mock_linter_clean = Mock()
        mock_linter_clean.number_errors = 0
        mock_linter_clean.total_number_warnings = 0
        mock_linter_clean.return_code = 0

        with (
            patch("megalinter.config.get") as mock_config,
            patch(
                "megalinter.llm_provider.llm_provider_factory.LLMProviderFactory.create_provider"
            ) as mock_create_provider,
        ):

            mock_config.side_effect = lambda req_id, key, default: {
                "LLM_ADVISOR_ENABLED": "true",
                "LLM_PROVIDER": "openai",
                "LLM_ADVISOR_LEVEL": "WARNING",
                "LLM_TEST_API_KEY_PRESENT": "true",
            }.get(key, default)

            # Mock provider
            mock_provider = Mock()
            mock_provider.get_config_value.return_value = "gpt-3.5-turbo"
            mock_provider.get_default_model.return_value = "gpt-3.5-turbo"
            mock_provider.is_available.return_value = True
            mock_create_provider.return_value = mock_provider

            advisor = LLMAdvisor("test-request")

            # Should analyze both blocking and non-blocking linters
            self.assertTrue(
                advisor.should_analyze_linter(mock_linter_errors)
            )  # Blocking errors
            self.assertTrue(
                advisor.should_analyze_linter(mock_linter_warnings)
            )  # Non-blocking warnings
            self.assertTrue(
                advisor.should_analyze_linter(mock_linter_both)
            )  # Blocking errors+warnings
            self.assertTrue(
                advisor.should_analyze_linter(mock_linter_ignored_errors)
            )  # Non-blocking ignored errors
            self.assertFalse(
                advisor.should_analyze_linter(mock_linter_clean)
            )  # No issues

    @patch("megalinter.config.get_list")
    @patch("megalinter.config.get")
    @patch(
        "megalinter.llm_provider.llm_provider_factory.LLMProviderFactory.create_provider"
    )
    def test_should_analyze_linter_blocking_vs_nonblocking(
        self, mock_create_provider, mock_config, mock_config_list
    ):
        mock_config_list.side_effect = lambda req_id, key, default: []
        mock_config.side_effect = lambda req_id, key, default: {
            "LLM_ADVISOR_ENABLED": "true",
            "LLM_PROVIDER": "openai",
            "LLM_ADVISOR_LEVEL": "ERROR",
            "LLM_TEST_API_KEY_PRESENT": "true",
        }.get(key, default)

        # Mock a linter with errors that are blocking the build
        mock_blocking_linter = Mock()
        mock_blocking_linter.number_errors = 5
        mock_blocking_linter.total_number_warnings = 2
        mock_blocking_linter.return_code = 1  # Blocking (build fails)

        # Mock a linter with errors that are ignored/non-blocking
        mock_nonblocking_linter = Mock()
        mock_nonblocking_linter.number_errors = 3
        mock_nonblocking_linter.total_number_warnings = 1
        mock_nonblocking_linter.return_code = 0  # Non-blocking (errors ignored)

        # Mock a linter with only warnings (non-blocking)
        mock_warning_linter = Mock()
        mock_warning_linter.number_errors = 0
        mock_warning_linter.total_number_warnings = 4
        mock_warning_linter.return_code = 0  # Non-blocking

        with (
            patch("megalinter.config.get") as mock_config,
            patch(
                "megalinter.llm_provider.llm_provider_factory.LLMProviderFactory.create_provider"
            ) as mock_create_provider,
        ):

            # Test ERROR level
            mock_config.side_effect = lambda req_id, key, default: {
                "LLM_ADVISOR_ENABLED": "true",
                "LLM_PROVIDER": "openai",
                "LLM_ADVISOR_LEVEL": "ERROR",
                "LLM_TEST_API_KEY_PRESENT": "true",
            }.get(key, default)

            # Mock provider
            mock_provider = Mock()
            mock_provider.get_config_value.return_value = "gpt-3.5-turbo"
            mock_provider.get_default_model.return_value = "gpt-3.5-turbo"
            mock_provider.is_available.return_value = True
            mock_create_provider.return_value = mock_provider

            advisor = LLMAdvisor("test-request")

            # ERROR level: Only blocking linters should be analyzed
            self.assertTrue(advisor.should_analyze_linter(mock_blocking_linter))
            self.assertFalse(advisor.should_analyze_linter(mock_nonblocking_linter))
            self.assertFalse(advisor.should_analyze_linter(mock_warning_linter))

        with (
            patch("megalinter.config.get") as mock_config,
            patch(
                "megalinter.llm_provider.llm_provider_factory.LLMProviderFactory.create_provider"
            ) as mock_create_provider,
        ):

            # Test WARNING level
            mock_config.side_effect = lambda req_id, key, default: {
                "LLM_ADVISOR_ENABLED": "true",
                "LLM_PROVIDER": "openai",
                "LLM_ADVISOR_LEVEL": "WARNING",
                "LLM_TEST_API_KEY_PRESENT": "true",
            }.get(key, default)

            # Mock provider
            mock_provider = Mock()
            mock_provider.get_config_value.return_value = "gpt-3.5-turbo"
            mock_provider.get_default_model.return_value = "gpt-3.5-turbo"
            mock_provider.is_available.return_value = True
            mock_create_provider.return_value = mock_provider

            advisor = LLMAdvisor("test-request")

            # WARNING level: Both blocking and non-blocking linters should be analyzed
            self.assertTrue(advisor.should_analyze_linter(mock_blocking_linter))
            self.assertTrue(advisor.should_analyze_linter(mock_nonblocking_linter))
            self.assertTrue(advisor.should_analyze_linter(mock_warning_linter))

    def test_linter_enable_disable_lists_with_no_issues(self):

        # Mock linter with no issues
        mock_linter_clean = Mock()
        mock_linter_clean.name = "JAVASCRIPT_ESLINT"
        mock_linter_clean.number_errors = 0
        mock_linter_clean.total_number_warnings = 0
        mock_linter_clean.return_code = 0

        with (
            patch("megalinter.config.get") as mock_config,
            patch("megalinter.config.get_list") as mock_config_list,
            patch(
                "megalinter.llm_provider.llm_provider_factory.LLMProviderFactory.create_provider"
            ) as mock_create_provider,
        ):

            mock_config.side_effect = lambda req_id, key, default: {
                "LLM_ADVISOR_ENABLED": "true",
                "LLM_PROVIDER": "openai",
                "LLM_ADVISOR_LEVEL": "ERROR",
            }.get(key, default)

            mock_config_list.side_effect = lambda req_id, key, default: {
                "LLM_ADVISOR_ENABLE_LINTERS": ["JAVASCRIPT_ESLINT"],
                "LLM_ADVISOR_DISABLE_LINTERS": [],
            }.get(key, default)

            # Mock provider
            mock_provider = Mock()
            mock_provider.get_config_value.return_value = "gpt-3.5-turbo"
            mock_provider.get_default_model.return_value = "gpt-3.5-turbo"
            mock_provider.is_available.return_value = True
            mock_create_provider.return_value = mock_provider

            advisor = LLMAdvisor("test-request")

            # Should not analyze linter with no issues, even if enabled
            self.assertFalse(advisor.should_analyze_linter(mock_linter_clean))


if __name__ == "__main__":
    unittest.main()
