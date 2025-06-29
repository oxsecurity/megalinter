# OpenAI Provider

OpenAI provides state-of-the-art language models including GPT-3.5, GPT-4, and GPT-4o, offering excellent code analysis and fix suggestions.

## Supported Models

| Model | Context Length | Cost | Best For |
|-------|---------------|------|----------|
| `gpt-3.5-turbo` | 16K tokens | $ | General use, fast responses |
| `gpt-4o-mini` | 128K tokens | $$ | Better analysis, longer context |
| `gpt-4o` | 128K tokens | $$$ | Highest quality, complex code |
| `gpt-4-turbo` | 128K tokens | $$$ | Advanced reasoning |

## Setup

1. **Get API Key**: Sign up at [OpenAI Platform](https://platform.openai.com/)
2. **Set Environment Variable**:
   ```bash
   export OPENAI_API_KEY=sk-your-api-key-here
   ```
3. **Configure MegaLinter**:
   ```yaml
   LLM_ADVISOR_ENABLED: true
   LLM_PROVIDER: openai
   LLM_MODEL_NAME: gpt-3.5-turbo
   LLM_MAX_TOKENS: 1000
   LLM_TEMPERATURE: 0.1
   ```

## Configuration Options

### Basic Configuration

```yaml
LLM_PROVIDER: openai
LLM_MODEL_NAME: gpt-3.5-turbo      # or gpt-4o-mini, gpt-4o
```

### Advanced Configuration

```yaml
# Custom API endpoint (for Azure OpenAI or compatible APIs)
OPENAI_BASE_URL: https://api.openai.com/v1

# Organization ID (optional)
OPENAI_ORGANIZATION: org-your-org-id
```

## Model Recommendations

- **Development/Testing**: `gpt-3.5-turbo` - Fast and cost-effective
- **Production**: `gpt-4o-mini` - Better analysis with reasonable cost
- **Complex Codebases**: `gpt-4o` - Highest quality for challenging issues

## Cost Considerations

- **Input tokens**: Code context sent to the model
- **Output tokens**: AI suggestions generated
- **Typical cost**: $0.01-0.10 per linter error analyzed

Monitor usage on your [OpenAI dashboard](https://platform.openai.com/usage).

## Troubleshooting

### Common Issues

1. **"Invalid API key"**
   - Verify your API key is correct
   - Check that your account has available credits
   - Ensure the key has proper permissions

2. **"Rate limit exceeded"**
   - Reduce concurrent requests
   - Upgrade to a higher tier plan
   - Implement retry logic

3. **"Model not found"**
   - Verify the model name is correct
   - Check if you have access to the model
   - Some models require special access

### Debug Mode

```yaml
LOG_LEVEL: DEBUG
```

This will show the exact requests and responses for troubleshooting.

## Best Practices

- Use `gpt-3.5-turbo` for development and testing
- Monitor token usage to control costs
- Set reasonable `LLM_MAX_TOKENS` limits
- Use lower temperature (0.1-0.3) for consistent suggestions
