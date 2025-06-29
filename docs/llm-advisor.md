# AI-Powered Fix Suggestions (LLM Advisor)

MegaLinter includes an AI-powered advisor that provides intelligent fix suggestions for linter errors using various Large Language Models (LLMs) through LangChain.

## Features

- **Multi-Provider Support**: Works with OpenAI, Anthropic, Google Gemini, Hugging Face, Mistral AI, DeepSeek, Grok, and local Ollama models
- **Context-Aware Suggestions**: Analyzes code context around errors for better recommendations
- **Integrated Reporting**: AI suggestions appear directly in MegaLinter reports
- **Configurable**: Control which models to use and how many errors to analyze

## Supported LLM Providers

| Provider                                                  | Models                                | API Key Required | Local/Cloud | Documentation                                            |
|-----------------------------------------------------------|---------------------------------------|------------------|-------------|----------------------------------------------------------|
| [OpenAI](llm-provider/llm_provider_openai.md)             | GPT-3.5, GPT-4, GPT-4o                | Yes              | Cloud       | [Setup Guide](llm-provider/llm_provider_openai.md)       |
| [Anthropic](llm-provider/llm_provider_anthropic.md)       | Claude 3 (Haiku, Sonnet, Opus)        | Yes              | Cloud       | [Setup Guide](llm-provider/llm_provider_anthropic.md)    |
| [Google GenAI](llm-provider/llm_provider_google_genai.md) | Gemini Pro, Gemini Pro Vision         | Yes              | Cloud       | [Setup Guide](llm-provider/llm_provider_google_genai.md) |
| [Mistral AI](llm-provider/llm_provider_mistralai.md)      | Mistral Small, Medium, Large          | Yes              | Cloud       | [Setup Guide](llm-provider/llm_provider_mistralai.md)    |
| [DeepSeek](llm-provider/llm_provider_deepseek.md)         | DeepSeek Chat, DeepSeek Coder         | Yes              | Cloud       | [Setup Guide](llm-provider/llm_provider_deepseek.md)     |
| [Grok](llm-provider/llm_provider_grok.md)                 | Grok Beta                             | Yes              | Cloud       | [Setup Guide](llm-provider/llm_provider_grok.md)         |
| [Ollama](llm-provider/llm_provider_ollama.md)             | Llama 2, CodeLlama, Mistral, etc.     | No               | Local       | [Setup Guide](llm-provider/llm_provider_ollama.md)       |
| [Hugging Face](llm-provider/llm_provider_huggingface.md)  | Any HF model (DialoGPT, CodeT5, etc.) | Optional         | Local/Cloud | [Setup Guide](llm-provider/llm_provider_huggingface.md)  |

See [All LLM Providers](llm-providers.md) for a complete comparison and setup instructions.

## Quick Start

1. **Choose your provider** from the [supported providers](llm-providers.md)
2. **Set your API key** as an environment variable
3. **Configure MegaLinter** in your `.mega-linter.yml`:

```yaml
# Enable AI-powered fix suggestions
LLM_ADVISOR_ENABLED: true

# Choose your provider and model
LLM_PROVIDER: openai  # openai, anthropic, google, huggingface, mistral, deepseek, grok, ollama
LLM_MODEL_NAME: gpt-3.5-turbo
LLM_MAX_TOKENS: 1000
LLM_TEMPERATURE: 0.1
```

4. **Run MegaLinter** - AI suggestions will appear in your reports

## Basic Configuration

```yaml
LLM_ADVISOR_ENABLED: true          # Enable/disable AI advisor
LLM_PROVIDER: openai               # Provider: see supported providers above
LLM_MODEL_NAME: gpt-3.5-turbo      # Model name (provider-specific)
LLM_MAX_TOKENS: 1000               # Maximum tokens for response
LLM_TEMPERATURE: 0.1               # Temperature for generation (0.0-1.0)
```

## Security Considerations

⚠️ **Important**: Set API credentials as environment variables in your CI/CD system, not in `.mega-linter.yml` files.

```bash
# Examples (choose your provider)
OPENAI_API_KEY=sk-your-api-key
ANTHROPIC_API_KEY=sk-ant-your-api-key
GOOGLE_API_KEY=AIza-your-api-key
```

For detailed provider setup instructions, see the individual provider documentation pages linked above.

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

## Benefits & Use Cases

- **Learning Tool**: Helps developers understand why errors occur and how to fix them
- **Faster Development**: Provides immediate, actionable suggestions without context switching
- **Code Quality**: Explains best practices to prevent similar issues in the future
- **Time Saving**: Reduces time spent researching error meanings and solutions
- **Context-Aware**: Analyzes actual code context for better, more relevant recommendations

## Limitations & Considerations

- **API Costs**: Cloud providers charge for API usage
- **Rate Limits**: Providers may have request limits
- **Token Limits**: Large files may be truncated for analysis
- **Accuracy**: AI suggestions should be reviewed before applying
- **Privacy**: Code snippets are sent to the LLM provider for analysis (use local Ollama for private code)

## Getting Started

1. **[Choose a Provider](llm-providers.md)** - Compare all available LLM providers
2. **Set up credentials** - Follow the provider-specific setup guide
3. **Configure MegaLinter** - Add configuration to your `.mega-linter.yml`
4. **Run and review** - Check the AI suggestions in your MegaLinter reports

For detailed setup instructions, see the documentation for your chosen provider.

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
