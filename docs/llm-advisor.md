# AI-Powered Fix Suggestions (LLM Advisor)

MegaLinter now includes an AI-powered advisor that provides intelligent fix suggestions for linter errors using various Large Language Models (LLMs) through LangChain.

## Features

- **Multi-Provider Support**: Works with OpenAI, Anthropic, Google Gemini, and local Ollama models
- **Context-Aware Suggestions**: Analyzes code context around errors for better recommendations
- **Integrated Reporting**: AI suggestions appear directly in MegaLinter reports
- **Configurable**: Control which models to use and how many errors to analyze

## Supported LLM Providers

| Provider | Models | API Key Required | Local/Cloud |
|----------|---------|------------------|-------------|
| OpenAI | GPT-3.5, GPT-4, GPT-4o | Yes | Cloud |
| Anthropic | Claude 3 (Haiku, Sonnet, Opus) | Yes | Cloud |
| Google | Gemini Pro, Gemini Pro Vision | Yes | Cloud |
| Ollama | Llama 2, CodeLlama, Mistral, etc. | No | Local |

## Installation

### 1. Install LangChain Dependencies

```bash
pip install 'megalinter[llm]'
```

Or install individual packages:
```bash
pip install langchain-core langchain-openai langchain-anthropic langchain-google-genai langchain-community
```

### 2. Configure Your LLM Provider

Add to your `.mega-linter.yml`:

```yaml
# Enable AI-powered fix suggestions
LLM_ADVISOR_ENABLED: true

# Choose your provider and model
LLM_PROVIDER: openai
LLM_MODEL_NAME: gpt-3.5-turbo
LLM_MAX_TOKENS: 1000
LLM_TEMPERATURE: 0.1
```

### 3. Set API Credentials

Set environment variables for your chosen provider:

```bash
# For OpenAI
export OPENAI_API_KEY="sk-your-api-key"

# For Anthropic
export ANTHROPIC_API_KEY="sk-ant-your-api-key"

# For Google
export GOOGLE_API_KEY="AIza-your-api-key"

# Ollama doesn't require API keys (local)
```

## Configuration Options

### Basic Configuration

```yaml
LLM_ADVISOR_ENABLED: true          # Enable/disable AI advisor
LLM_PROVIDER: openai               # Provider: openai, anthropic, google, ollama
LLM_MODEL_NAME: gpt-3.5-turbo      # Model name
LLM_MAX_TOKENS: 1000               # Maximum tokens for response
LLM_TEMPERATURE: 0.1               # Temperature for generation (0.0-1.0)
```

### Provider-Specific Examples

#### OpenAI Configuration
```yaml
LLM_PROVIDER: openai
LLM_MODEL_NAME: gpt-4o-mini        # or gpt-3.5-turbo, gpt-4
# Set OPENAI_API_KEY environment variable
```

#### Anthropic Configuration  
```yaml
LLM_PROVIDER: anthropic
LLM_MODEL_NAME: claude-3-haiku-20240307  # or claude-3-sonnet-20240229
# Set ANTHROPIC_API_KEY environment variable
```

#### Google Gemini Configuration
```yaml
LLM_PROVIDER: google
LLM_MODEL_NAME: gemini-pro         # or gemini-pro-vision
# Set GOOGLE_API_KEY environment variable
```

#### Local Ollama Configuration
```yaml
LLM_PROVIDER: ollama
LLM_MODEL_NAME: llama2             # or codellama, mistral, etc.
OLLAMA_BASE_URL: http://localhost:11434  # Optional: custom Ollama URL
```

### Advanced Configuration

```yaml
# Custom API endpoints
OPENAI_BASE_URL: https://api.openai.com/v1  # For OpenAI-compatible APIs
OLLAMA_BASE_URL: http://localhost:11434     # For custom Ollama instances
```

## How It Works

1. **Error Collection**: MegaLinter collects errors from active linters
2. **Context Analysis**: The AI advisor analyzes code context around each error
3. **AI Processing**: Errors are sent to the configured LLM with structured prompts
4. **Suggestion Generation**: The LLM provides explanations and fix recommendations
5. **Report Integration**: Suggestions are added to the markdown summary report

## Example Output

When AI advisor is enabled, you'll see a new section in your MegaLinter reports:

```markdown
## 🤖 AI-Powered Fix Suggestions (openai - gpt-3.5-turbo)

Analyzed 3 out of 5 errors:

### 1. src/example.py
**Line 15** - flake8 (F401)

**Error:** 'os' imported but unused

**AI Suggestion:**
This error occurs because you've imported the `os` module but haven't used it anywhere in your code. To fix this:

1. Remove the unused import: Delete the line `import os`
2. Or if you plan to use it later, add a comment: `import os  # TODO: will be used for file operations`
3. Alternatively, if it's used in a way the linter doesn't detect, you can disable the warning: `import os  # noqa: F401`

**Best Practice:** Only import modules that you actually use to keep your code clean and improve performance.

---

### 2. styles/main.css
**Line 23** - stylelint (block-no-empty)

**Error:** Unexpected empty block

**AI Suggestion:**
Empty CSS blocks serve no purpose and should be removed. To fix this:

1. **Remove the empty block entirely** if it's not needed
2. **Add CSS properties** if the selector should style something
3. **Add a comment** if you're planning to add styles later

Example fix:
```css
/* Remove this: */
.empty-class {
}

/* Or add content: */
.empty-class {
  /* Styles will be added later */
}
```

---
```

## Benefits

- **Learning Tool**: Helps developers understand why errors occur
- **Faster Fixes**: Provides immediate, actionable suggestions
- **Code Quality**: Explains best practices to prevent similar issues
- **Time Saving**: Reduces time spent researching error meanings
- **Context-Aware**: Analyzes actual code for better recommendations

## Limitations

- **API Costs**: Cloud providers charge for API usage
- **Rate Limits**: Providers may have request limits
- **Token Limits**: Large files may be truncated for analysis
- **Accuracy**: AI suggestions should be reviewed before applying
- **Dependencies**: Requires additional Python packages

## Privacy and Security

- **Code Analysis**: Code snippets are sent to the LLM provider for analysis
- **Data Handling**: Follows each provider's data usage policies
- **Local Option**: Use Ollama for completely local processing
- **Configurable**: Can be disabled entirely if not desired

## Troubleshooting

### Common Issues

1. **"LLM Advisor not available"**
   - Check that `LLM_ADVISOR_ENABLED: true`
   - Verify LangChain dependencies are installed
   - Ensure API keys are set correctly

2. **"Failed to initialize LLM"**
   - Verify API key is valid and has sufficient credits
   - Check internet connection for cloud providers
   - For Ollama, ensure the service is running locally

3. **No suggestions generated**
   - Check if errors were detected by linters
   - Verify the linter output format is parseable
   - Review logs for parsing errors

### Debug Mode

Enable debug logging to troubleshoot issues:

```yaml
LOG_LEVEL: DEBUG
```

This will show detailed information about LLM requests and responses.

## Contributing

The LLM advisor is designed to be extensible:

- **Custom Providers**: Add support for new LLM providers
- **Better Parsing**: Improve linter output parsing for specific tools
- **Enhanced Prompts**: Refine prompts for better suggestions
- **Additional Context**: Include more code context for analysis

See the `megalinter/llm_advisor.py` file for implementation details.
