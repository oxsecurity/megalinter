#!/usr/bin/env python3
"""
DeepSeek LLM Provider for MegaLinter
"""

import logging
from typing import Dict, Any
from langchain_deepseek import ChatDeepSeek
from megalinter import config
from .llm_provider import LLMProvider


class DeepSeekProvider(LLMProvider):
    """DeepSeek provider implementation"""
    
    def get_default_model(self) -> str:
        """Get default DeepSeek model"""
        return "deepseek-chat"
    
    def load_config(self, request_id: str = None) -> Dict[str, Any]:
        """Load DeepSeek-specific configuration"""
        return {
            "api_key": config.get(request_id, "DEEPSEEK_API_KEY", ""),
            "base_url": config.get(request_id, "DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1"),
            "model_name": config.get(request_id, "LLM_MODEL_NAME", ""),
            "temperature": float(config.get(request_id, "LLM_TEMPERATURE", str(self.get_default_config_value("temperature")))),
            "max_tokens": int(config.get(request_id, "LLM_MAX_TOKENS", str(self.get_default_config_value("max_tokens"))))
        }
    
    def initialize(self) -> bool:
        """Initialize DeepSeek provider"""
        try:
            api_key = self.get_config_value("api_key")
            if not api_key:
                raise ValueError("DeepSeek API key is required")
                
            model_name = self.get_config_value("model_name") or self.get_default_model()
            base_url = self.get_config_value("base_url", "https://api.deepseek.com/v1")
            temperature = self.get_config_value("temperature")
            max_tokens = self.get_config_value("max_tokens")
                
            self.llm = ChatDeepSeek(
                model=model_name,
                temperature=temperature,
                max_tokens=max_tokens,
                api_key=api_key,
                base_url=base_url
            )
            
            logging.info(f"DeepSeek provider initialized with model {model_name}")
            return True
            
        except Exception as e:
            logging.error(f"Failed to initialize DeepSeek provider: {str(e)}")
            return False
