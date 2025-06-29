#!/usr/bin/env python3
"""
LLM Advisor for MegaLinter
Provides AI-powered hints for fixing linter errors using various LLM providers through LangChain
"""

import logging
import os
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.llms import Ollama
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate

from megalinter import config


class LLMAdvisor:
    """
    AI-powered advisor for providing linter error fix suggestions using various LLM providers
    """
    
    SUPPORTED_PROVIDERS = {
        "openai": "OpenAI GPT models",
        "anthropic": "Anthropic Claude models", 
        "google": "Google Gemini models",
        "ollama": "Local Ollama models"
    }
    
    def __init__(self, request_id: str = None):
        """Initialize LLM Advisor with configuration"""
        self.request_id = request_id
        self.enabled = False
        self.llm = None
        self.provider = None
        self.model_name = None
            
        # Load configuration
        self._load_config()
        
        # Initialize LLM if enabled
        if self.enabled:
            self._initialize_llm()
    
    def _load_config(self):
        """Load LLM configuration from environment/config"""
        self.enabled = config.get(self.request_id, "LLM_ADVISOR_ENABLED", "false").lower() == "true"
        
        if not self.enabled:
            return
            
        self.provider = config.get(self.request_id, "LLM_PROVIDER", "openai").lower()
        self.model_name = config.get(self.request_id, "LLM_MODEL_NAME", self._get_default_model())
        self.max_tokens = int(config.get(self.request_id, "LLM_MAX_TOKENS", "1000"))
        self.temperature = float(config.get(self.request_id, "LLM_TEMPERATURE", "0.1"))
        
        # Provider-specific settings
        if self.provider == "openai":
            self.api_key = config.get(self.request_id, "OPENAI_API_KEY", "")
            self.base_url = config.get(self.request_id, "OPENAI_BASE_URL", None)
        elif self.provider == "anthropic":
            self.api_key = config.get(self.request_id, "ANTHROPIC_API_KEY", "")
        elif self.provider == "google":
            self.api_key = config.get(self.request_id, "GOOGLE_API_KEY", "")
        elif self.provider == "ollama":
            self.base_url = config.get(self.request_id, "OLLAMA_BASE_URL", "http://localhost:11434")
            self.api_key = None  # Ollama doesn't require API key
    
    def _get_default_model(self) -> str:
        """Get default model name for the provider"""
        defaults = {
            "openai": "gpt-4o-mini",
            "anthropic": "claude-3-5-haiku-20241022",
            "google": "gemini-1.5-flash",
            "ollama": "llama3.2"
        }
        return defaults.get(self.provider, "gpt-3.5-turbo")
    
    def _initialize_llm(self):
        """Initialize the LLM based on provider configuration"""
        try:
            if self.provider == "openai":
                kwargs = {
                    "model": self.model_name,
                    "temperature": self.temperature,
                    "max_tokens": self.max_tokens,
                }
                if self.api_key:
                    kwargs["api_key"] = self.api_key
                if self.base_url:
                    kwargs["base_url"] = self.base_url
                self.llm = ChatOpenAI(**kwargs)
                
            elif self.provider == "anthropic":
                if not self.api_key:
                    raise ValueError("Anthropic API key is required")
                self.llm = ChatAnthropic(
                    model=self.model_name,
                    temperature=self.temperature,
                    max_tokens=self.max_tokens,
                    api_key=self.api_key
                )
                
            elif self.provider == "google":
                if not self.api_key:
                    raise ValueError("Google API key is required")
                self.llm = ChatGoogleGenerativeAI(
                    model=self.model_name,
                    temperature=self.temperature,
                    max_output_tokens=self.max_tokens,
                    google_api_key=self.api_key
                )
                
            elif self.provider == "ollama":
                self.llm = Ollama(
                    model=self.model_name,
                    base_url=self.base_url,
                    temperature=self.temperature
                )
                
            else:
                raise ValueError(f"Unsupported LLM provider: {self.provider}")
                
            logging.info(f"LLM Advisor initialized with {self.provider} ({self.model_name})")
            
        except Exception as e:
            logging.error(f"Failed to initialize LLM ({self.provider}): {str(e)}")
            self.enabled = False
            self.llm = None
    
    def is_available(self) -> bool:
        """Check if LLM advisor is available and properly configured"""
        return self.enabled and self.llm is not None
    
    def get_fix_suggestions(self, linter_name: str, linter_output: str, max_errors: int = 5) -> Dict[str, Any]:
        """
        Get AI-powered fix suggestions for linter errors
        
        Args:
            linter_name: Name of the linter
            linter_output: Raw output from the linter
            max_errors: Maximum number of errors to process (to avoid token limits)
            
        Returns:
            Dictionary containing fix suggestions and metadata
        """
        if not self.is_available():
            return {"enabled": False, "suggestions": []}
        
        # Work directly with raw output - much more reliable than trying to parse
        return self._get_suggestions_from_raw_output(linter_name, linter_output, max_errors)
    
    def _get_suggestions_from_raw_output(self, linter_name: str, linter_output: str, max_errors: int = 5) -> Dict[str, Any]:
        """
        Get AI suggestions directly from raw linter output
        
        Args:
            linter_name: Name of the linter
            linter_output: Raw output from the linter
            max_errors: Maximum number of suggestions to generate
            
        Returns:
            Dictionary containing fix suggestions and metadata
        """
        try:
            # Build a prompt for analyzing the raw output
            prompt = self._build_raw_output_prompt(linter_name, linter_output)
            
            # Get response from LLM
            if self.provider == "ollama":
                response = self.llm.invoke(prompt)
                suggestion_text = response
            else:
                messages = [
                    SystemMessage(content=self._get_system_prompt()),
                    HumanMessage(content=prompt)
                ]
                response = self.llm.invoke(messages)
                suggestion_text = response.content
            
            # Return as a single suggestion for the raw output
            suggestions = [{
                "file_path": "Multiple files",
                "line_number": None,
                "error_message": f"{linter_name} issues detected",
                "rule_id": None,
                "linter": linter_name,
                "suggestion": suggestion_text.strip(),
                "severity": "mixed"
            }]
            
            return {
                "enabled": True,
                "provider": self.provider,
                "model": self.model_name,
                "total_errors": 1,
                "processed_errors": 1,
                "suggestions": suggestions
            }
            
        except Exception as e:
            logging.warning(f"Failed to get suggestions from raw output: {str(e)}")
            return {
                "enabled": True,
                "provider": self.provider,
                "model": self.model_name,
                "total_errors": 0,
                "processed_errors": 0,
                "suggestions": []
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
            linter_output = linter_output[:max_output_length] + "\n\n(Output truncated...)"
        
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
            "Focus on the most actionable and important suggestions."
        ]
        
        return "\n".join(prompt_parts)

    def format_suggestions_for_output(self, suggestions_data: Dict[str, Any]) -> str:
        """Format suggestions for display in reports"""
        if not suggestions_data.get("enabled", False):
            return ""
        
        if not suggestions_data.get("suggestions"):
            return "No AI suggestions available for the detected errors."
        
        output_lines = [
            f"## 🤖 AI-Powered Fix Suggestions ({suggestions_data['provider']} - {suggestions_data['model']})",
            "",
            f"Analyzed {suggestions_data['processed_errors']} out of {suggestions_data['total_errors']} errors:",
            ""
        ]
        
        for i, suggestion in enumerate(suggestions_data["suggestions"], 1):
            output_lines.extend([
                f"### {i}. {suggestion['linter']} Issues",
                "",
                f"**AI Suggestion:**",
                suggestion['suggestion'],
                "",
                "---",
                ""
            ])
        
        return "\n".join(output_lines)
