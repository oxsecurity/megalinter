#!/usr/bin/env python3
"""
Integration test for LLM Advisor with MegaLinter reporting
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import os
import sys

# Add megalinter to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from megalinter.llm_advisor import LLMAdvisor
from megalinter import utils_reporter


class TestLLMAdvisorIntegration(unittest.TestCase):
    """Test LLM Advisor integration with MegaLinter"""

    def setUp(self):
        """Set up test fixtures"""
        pass

    @patch('megalinter.config.get')
    def test_llm_advisor_initialization(self, mock_config):
        """Test LLM advisor initialization"""
        # Mock configuration
        mock_config.side_effect = lambda req_id, key, default: {
            "LLM_ADVISOR_ENABLED": "true",
            "LLM_PROVIDER": "openai",
            "LLM_MODEL_NAME": "gpt-3.5-turbo",
            "LLM_MAX_TOKENS": "1000",
            "LLM_TEMPERATURE": "0.1",
            "OPENAI_API_KEY": "test-key"
        }.get(key, default)
        
        with patch('megalinter.llm_advisor.ChatOpenAI') as mock_openai:
            mock_openai.return_value = Mock()
            
            advisor = LLMAdvisor("test-request")
            
            self.assertTrue(advisor.enabled)
            self.assertEqual(advisor.provider, "openai")
            self.assertEqual(advisor.model_name, "gpt-3.5-turbo")

    @patch('megalinter.utils_reporter.LLM_ADVISOR_AVAILABLE', True)
    @patch('megalinter.llm_advisor.LLMAdvisor')
    def test_ai_suggestions_integration(self, mock_llm_advisor_class):
        """Test AI suggestions integration in reporting"""
        # Mock LLM advisor
        mock_advisor = Mock()
        mock_advisor.is_available.return_value = True
        mock_advisor.provider = "openai"
        mock_advisor.model_name = "gpt-3.5-turbo"
        mock_advisor.get_fix_suggestions.return_value = {
            "enabled": True,
            "provider": "openai",
            "model": "gpt-3.5-turbo",
            "total_errors": 1,
            "processed_errors": 1,
            "suggestions": [{
                "file_path": "test.py",
                "line_number": 10,
                "error_message": "F401 'os' imported but unused",
                "suggestion": "Remove the unused import statement",
                "linter": "flake8"
            }]
        }
        mock_advisor.format_suggestions_for_output.return_value = "## AI Suggestions\nRemove unused imports"
        mock_llm_advisor_class.return_value = mock_advisor
        
        # Mock reporter and linter
        mock_reporter = Mock()
        mock_reporter.master.request_id = "test-request"
        mock_reporter.report_folder = "/tmp/test"
        
        mock_linter = Mock()
        mock_linter.number_errors = 1
        mock_linter.total_number_warnings = 0
        mock_linter.linter_name = "flake8"
        mock_linter.name = "PYTHON_FLAKE8"
        mock_linter.status = "error"
        mock_linter.files = []  # Empty files list
        
        # Mock file system
        with patch('os.path.isfile', return_value=True), \
             patch('builtins.open', create=True) as mock_open:
            
            mock_open.return_value.__enter__.return_value.read.return_value = "test.py:10:5: F401 'os' imported but unused"
            
            # Test AI suggestions function
            result = utils_reporter.get_ai_fix_suggestions(mock_reporter, [mock_linter])
            
            self.assertIsNotNone(result)
            self.assertIn("AI Suggestions", result)
            
            # Verify the advisor was called with correct parameters
            mock_advisor.get_fix_suggestions.assert_called_once()
            call_args = mock_advisor.get_fix_suggestions.call_args
            self.assertEqual(call_args[0][0], "flake8")  # linter_name
            self.assertIn("F401", call_args[0][1])  # linter_output contains the error

    def test_raw_output_processing(self):
        """Test raw linter output processing"""
        linter_output = """test.py:10:5: F401 'os' imported but unused
style.css:23:12: block-no-empty Unexpected empty block
script.js:8:1: no-undef 'console' is not defined"""
        
        # Test that the advisor can process raw output
        with patch('megalinter.config.get') as mock_config:
            mock_config.side_effect = lambda req_id, key, default: {
                "LLM_ADVISOR_ENABLED": "false",  # Disabled for this test
            }.get(key, default)
            
            advisor = LLMAdvisor()
            
            # Should return disabled result
            result = advisor.get_fix_suggestions("test_linter", "test_linter", linter_output)
            self.assertFalse(result["enabled"])

    def test_disabled_when_advisor_disabled(self):
        """Test that LLM advisor is disabled when configuration is disabled"""
        with patch('megalinter.config.get') as mock_config:
            mock_config.side_effect = lambda req_id, key, default: {
                "LLM_ADVISOR_ENABLED": "false",
            }.get(key, default)
            
            advisor = LLMAdvisor()
            self.assertFalse(advisor.is_available())

    def test_no_suggestions_when_unavailable(self):
        """Test that no AI suggestions are generated when LLM advisor is unavailable"""
        mock_reporter = Mock()
        with patch.object(LLMAdvisor, 'is_available', return_value=False):
            result = utils_reporter.get_ai_fix_suggestions(mock_reporter, [])
            self.assertIsNone(result)


if __name__ == '__main__':
    unittest.main()
