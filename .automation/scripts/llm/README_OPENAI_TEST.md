# OpenAI Connector Test Scripts

This directory contains test scripts to verify the OpenAI integration for MegaLinter's LLM Advisor locally.

**Location**: `.automation/scripts/llm/`

## Files

- `test_openai_connector.py` - Full-featured test script with detailed output
- `test_openai_simple.py` - Simple test script with minimal dependencies
- `README_OPENAI_TEST.md` - This documentation file

## Setup

### 1. Get an OpenAI API Key

1. Go to [OpenAI Platform](https://platform.openai.com/api-keys)
2. Create a new API key
3. Copy the key (starts with `sk-`)

### 2. Configure Environment

**Option A: Using .env file (recommended)**

```bash
# From the MegaLinter root directory, copy the example file
cp .env.example .env

# Edit .env and replace 'your_openai_api_key_here' with your actual API key
# Example:
# OPENAI_API_KEY=sk-1234567890abcdef...
```

**Option B: Using environment variables**

```bash
# Windows (Command Prompt)
set OPENAI_API_KEY=sk-1234567890abcdef...

# Windows (PowerShell)
$env:OPENAI_API_KEY="sk-1234567890abcdef..."

# Linux/Mac
export OPENAI_API_KEY="sk-1234567890abcdef..."
```

## Running Tests

**Important**: Run these commands from the MegaLinter root directory, not from the scripts directory.

### Full Test (Recommended)

```bash
# Activate the virtual environment
.\.venv\Scripts\activate  # Windows
# or
source .venv/bin/activate  # Linux/Mac

# Run the comprehensive test from the root directory
python .automation/scripts/llm/test_openai_connector.py
```

### Simple Test

```bash
# Activate the virtual environment
.\.venv\Scripts\activate  # Windows

# Run the simple test from the root directory
python .automation/scripts/llm/test_openai_simple.py
```

## What the Tests Do

1. **Load Configuration**: Read API key from .env file or environment
2. **Initialize LLM Advisor**: Create and configure the OpenAI provider
3. **Test with Sample Data**: Send sample linter outputs to OpenAI
4. **Verify Responses**: Check that AI suggestions are received and formatted correctly

## Sample Output

```
🤖 Testing OpenAI Connector for MegaLinter LLM Advisor
============================================================
🔑 API Key found: sk-1234567...abcd
🚀 Initializing LLM Advisor...
✅ LLM Advisor initialized successfully
   Provider: openai
   Model: gpt-4o-mini

📋 Test 1: flake8 linter
   Input: test.py:10:5: F401 'os' imported but unused...
✅ Got suggestion from openai (gpt-4o-mini)
   Linter: flake8
   Suggestion preview: To fix the F401 'os' imported but unused error, you need to remove the import...

🎉 OpenAI connector test completed!
```

## Configuration Options

You can customize the test by setting these environment variables in your `.env` file:

```bash
# Required
OPENAI_API_KEY=your_openai_api_key_here

# Optional
LLM_MODEL_NAME=gpt-4o-mini          # Model to use (default: gpt-4o-mini)
LLM_TEMPERATURE=0.1                 # Response creativity (0.0-1.0)
LLM_MAX_TOKENS=1000                 # Maximum response length
OPENAI_BASE_URL=https://api.openai.com/v1  # Custom API endpoint
```

## Troubleshooting

### Common Issues

1. **"API key not found"**: Make sure your `.env` file contains `OPENAI_API_KEY=sk-...`
2. **"LLM Advisor not available"**: Check your API key is valid and has credits
3. **"Module not found"**: Make sure you've activated the virtual environment
4. **Rate limiting**: If you hit rate limits, wait a minute and try again

### Debug Mode

For more detailed logging, run with debug mode:

```bash
# Set debug logging
export MEGALINTER_LOG_LEVEL=DEBUG  # Linux/Mac
set MEGALINTER_LOG_LEVEL=DEBUG     # Windows

python .automation/scripts/llm/test_openai_connector.py
```

## Cost Considerations

- The test uses `gpt-4o-mini` by default (most cost-effective)
- Each test typically costs less than $0.01
- The tests send small amounts of text (~100-200 tokens)

## Integration with MegaLinter

Once the tests pass, you can use the LLM Advisor in MegaLinter by setting:

```bash
# In your CI/CD environment or local .mega-linter.yml
LLM_ADVISOR_ENABLED=true
LLM_PROVIDER=openai
OPENAI_API_KEY=your_key_here
```
