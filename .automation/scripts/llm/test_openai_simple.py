#!/usr/bin/env python3
"""
Simple test script for OpenAI connector without external dependencies
Set environment variables manually or source a .env file before running
"""

import os
import sys
import logging
from pathlib import Path

# Add megalinter to path
script_dir = Path(__file__).parent
megalinter_root = script_dir.parent.parent.parent  # Go up 3 levels to reach root
sys.path.insert(0, str(megalinter_root))

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

from megalinter.llm_advisor import LLMAdvisor
from megalinter import config


def simple_load_env(env_file=".env"):
    """Simple .env file loader without external dependencies"""
    if not os.path.exists(env_file):
        return False
        
    try:
        with open(env_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip().strip('"').strip("'")
                    os.environ[key] = value
        return True
    except Exception as e:
        print(f"Error loading .env file: {e}")
        return False


def test_openai_simple():
    """Simple OpenAI connector test"""
    
    print("🤖 Simple OpenAI Connector Test")
    print("=" * 40)
    
    # Try to load .env file
    if os.path.exists(".env"):
        print("📄 Loading .env file...")
        simple_load_env()
    
    # Check for API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or api_key == "your_openai_api_key_here":
        print("❌ OpenAI API key not set!")
        print("\n💡 Set your API key:")
        print("   export OPENAI_API_KEY='your-api-key-here'")
        print("   or create a .env file with OPENAI_API_KEY=your-api-key-here")
        return False
    
    print(f"🔑 API key: {api_key[:8]}...{api_key[-4:]}")
    
    # Configure
    request_id = "simple_test"
    config.set_config(request_id, {
        "LLM_ADVISOR_ENABLED": "true",
        "LLM_PROVIDER": "openai",
        "LLM_MODEL_NAME": os.getenv("LLM_MODEL_NAME", "gpt-4o-mini"),
        "LLM_TEMPERATURE": os.getenv("LLM_TEMPERATURE", "0.1"),
        "LLM_MAX_TOKENS": os.getenv("LLM_MAX_TOKENS", "500"),
        "OPENAI_API_KEY": api_key
    })
    
    try:
        print("\n🚀 Testing LLM Advisor...")
        advisor = LLMAdvisor(request_id)
        
        if not advisor.is_available():
            print("❌ LLM Advisor not available")
            return False
            
        print(f"✅ Provider: {advisor.provider_name}")
        print(f"✅ Model: {advisor.model_name}")
        
        # Quick test
        print("\n🧪 Testing with sample error...")
        result = advisor.get_fix_suggestions(
            "flake8", 
            "test.py:1:1: F401 'sys' imported but unused"
        )
        
        if result.get("enabled") and result.get("suggestion"):
            suggestion = result["suggestion"]["suggestion"]
            print(f"✅ Got suggestion: {suggestion[:60]}...")
            return True
        else:
            print("❌ No suggestion received")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


if __name__ == "__main__":
    success = test_openai_simple()
    print("\n" + "=" * 40)
    if success:
        print("🎉 Test successful!")
    else:
        print("💥 Test failed!")
    sys.exit(0 if success else 1)
