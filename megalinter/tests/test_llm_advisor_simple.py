#!/usr/bin/env python3
"""
Test script for LLM Advisor functionality
"""

import os
import sys
import logging

# Add megalinter to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from megalinter.llm_advisor import LLMAdvisor

# Configure logging
logging.basicConfig(level=logging.INFO)

def test_llm_advisor():
    """Test LLM Advisor with sample linter output"""
    
    # Sample raw linter outputs
    sample_outputs = {
        "flake8": "example.py:15:4: F401 'os' imported but unused\nexample.py:23:1: E302 expected 2 blank lines, found 1",
        "stylelint": "style.css:23:12: block-no-empty Unexpected empty block\nstyle.css:45:5: color-no-invalid-hex Invalid hex color",
        "eslint": "script.js:8:5: 'console' is not defined (no-undef)\nscript.js:12:3: Missing semicolon (semi)"
    }
    
    print("Supported LLM providers:")
    print("- openai: OpenAI GPT models")
    print("- anthropic: Anthropic Claude models")
    print("- google: Google Gemini models")
    print("- huggingface: Hugging Face models")
    print("- mistral: Mistral AI models")
    print("- deepseek: DeepSeek models")
    print("- grok: Grok (xAI) models")
    print("- ollama: Local Ollama models")
    print()
    
    # Test LLM Advisor (will only work if properly configured)
    print("Testing LLM Advisor...")
    advisor = LLMAdvisor()
    
    print(f"LLM Advisor available: {advisor.is_available()}")
    
    if advisor.is_available():
        print(f"Provider: {advisor.provider}")
        print(f"Model: {advisor.model_name}")
        
        # Test getting suggestions for each linter output
        for linter_name, output in sample_outputs.items():
            print(f"\nTesting suggestions for {linter_name}...")
            
            suggestions = advisor.get_fix_suggestions(linter_name, linter_name, output)
            
            if suggestions.get("suggestions"):
                print(f"Got {len(suggestions['suggestions'])} suggestions")
                formatted_output = advisor.format_suggestions_for_output(suggestions)
                print("Formatted output:")
                print(formatted_output[:200] + "..." if len(formatted_output) > 200 else formatted_output)
            else:
                print("No suggestions received")
                
    else:
        print("LLM Advisor not available (missing config or dependencies)")
        print("Raw output analysis would work like this:")
        
        # Show how it would work without actually calling LLM
        for linter_name, output in sample_outputs.items():
            print(f"\n{linter_name} output:")
            print(output)
            print("-> Would be sent to LLM for analysis")

if __name__ == "__main__":
    test_llm_advisor()
