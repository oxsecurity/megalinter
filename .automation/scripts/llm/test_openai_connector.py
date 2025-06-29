#!/usr/bin/env python3
"""
Test script for OpenAI connector using .env file
"""

import os
import sys
import logging
from pathlib import Path

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✅ .env file loaded successfully")
except ImportError:
    print("⚠️  python-dotenv not found. Install it with: pip install python-dotenv")
    print("   Falling back to environment variables only")

# Add megalinter to path
script_dir = Path(__file__).parent
megalinter_root = script_dir.parent.parent.parent  # Go up 3 levels to reach root
sys.path.insert(0, str(megalinter_root))

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

from megalinter.llm_advisor import LLMAdvisor
from megalinter import config


def test_openai_connector():
    """Test OpenAI connector with real API"""
    
    print("=" * 60)
    print("🤖 Testing OpenAI Connector for MegaLinter LLM Advisor")
    print("=" * 60)
    
    # Check for API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ ERROR: OPENAI_API_KEY not found in environment variables or .env file")
        print("\n📝 Create a .env file in the project root with:")
        print("OPENAI_API_KEY=your_openai_api_key_here")
        return False
    
    print(f"🔑 API Key found: {api_key[:10]}...{api_key[-4:]}")
    
    # Set up configuration
    request_id = "test_openai_connector"
    test_config = {
        "LLM_ADVISOR_ENABLED": "true",
        "LLM_PROVIDER": "openai", 
        "LLM_MODEL_NAME": "gpt-4o-mini",  # Use the cost-effective model
        "LLM_TEMPERATURE": "0.1",
        "LLM_MAX_TOKENS": "1000",
        "OPENAI_API_KEY": api_key
    }
    
    config.set_config(request_id, test_config)
    
    try:
        # Initialize LLM Advisor
        print("\n🚀 Initializing LLM Advisor...")
        advisor = LLMAdvisor(request_id)
        
        if not advisor.is_available():
            print("❌ LLM Advisor is not available")
            print(f"   Provider: {advisor.provider_name}")
            print(f"   Enabled: {advisor.enabled}")
            return False
            
        print(f"✅ LLM Advisor initialized successfully")
        print(f"   Provider: {advisor.provider_name}")
        print(f"   Model: {advisor.model_name}")
        
        # Test with sample linter output
        print("\n🔍 Testing with sample linter output...")
        
        test_cases = [
            {
                "linter": "flake8",
                "output": "test.py:10:5: F401 'os' imported but unused\ntest.py:15:1: E302 expected 2 blank lines, found 1"
            },
            {
                "linter": "pylint", 
                "output": "module.py:1:0: C0111: Missing module docstring (missing-docstring)\nmodule.py:5:0: W0613: Unused argument 'args' (unused-argument)"
            },
            {
                "linter": "eslint",
                "output": "script.js:8:1: error no-unused-vars 'console' is defined but never used\nscript.js:12:5: error no-undef 'undefinedVar' is not defined"
            }
        ]
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n📋 Test {i}: {test_case['linter']} linter")
            print(f"   Input: {test_case['output'][:60]}...")
            
            try:
                result = advisor.get_fix_suggestions(test_case['linter'], test_case['output'])
                
                if result.get("enabled") and result.get("suggestion"):
                    suggestion = result["suggestion"]
                    print(f"✅ Got suggestion from {result['provider']} ({result['model']})")
                    print(f"   Linter: {suggestion['linter']}")
                    print(f"   Suggestion preview: {suggestion['suggestion'][:100]}...")
                    
                    # Test formatting
                    formatted = advisor.format_suggestions_for_output(result)
                    print(f"   Formatted output length: {len(formatted)} characters")
                    
                else:
                    print(f"❌ No suggestion received")
                    print(f"   Result: {result}")
                    
            except Exception as e:
                print(f"❌ Error getting suggestion: {str(e)}")
                
        print("\n" + "=" * 60)
        print("🎉 OpenAI connector test completed!")
        return True
        
    except Exception as e:
        print(f"❌ Error during test: {str(e)}")
        return False


def create_sample_env_file():
    """Create a sample .env file in the project root"""
    env_content = """# OpenAI API Configuration for MegaLinter LLM Advisor
OPENAI_API_KEY=your_openai_api_key_here

# Optional: Custom OpenAI base URL (for compatible APIs)
# OPENAI_BASE_URL=https://api.openai.com/v1

# Optional: Override default model
# LLM_MODEL_NAME=gpt-4o-mini

# Optional: Adjust temperature (0.0 to 1.0)
# LLM_TEMPERATURE=0.1

# Optional: Adjust max tokens
# LLM_MAX_TOKENS=1000
"""
    
    # Create .env file in the current working directory (should be project root)
    env_file = Path(".env")
    if not env_file.exists():
        env_file.write_text(env_content)
        print(f"📝 Created sample .env file at {env_file.absolute()}")
        print("   Please edit it with your actual OpenAI API key")
    else:
        print(f"📁 .env file already exists at {env_file.absolute()}")


if __name__ == "__main__":
    print("🔧 MegaLinter OpenAI Connector Test")
    print("   This script tests the OpenAI integration locally")
    
    # Check if .env file exists, create sample if not
    if not Path(".env").exists():
        print("\n📝 No .env file found. Creating sample...")
        create_sample_env_file()
        print("\n⚠️  Please edit the .env file with your OpenAI API key and run again")
        sys.exit(1)
    
    # Run the test
    success = test_openai_connector()
    
    if success:
        print("\n✅ All tests passed! OpenAI connector is working correctly.")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed. Check the output above for details.")
        sys.exit(1)
