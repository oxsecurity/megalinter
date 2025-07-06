# Anthropic Provider

Anthropic's Claude models excel at code analysis with a strong focus on safety and helpful responses.

## Setup

1. **Get API Key**: Sign up at [Anthropic Console](https://console.anthropic.com/)

2. **Set Environment Variable**:

   ```bash
   export ANTHROPIC_API_KEY=sk-ant-your-api-key
   ```

3. **Configure MegaLinter**:

   ```yaml
   LLM_ADVISOR_ENABLED: true
   LLM_PROVIDER: anthropic
   LLM_MODEL_NAME: claude-3-haiku-20240307
   LLM_MAX_TOKENS: 1000
   LLM_TEMPERATURE: 0.1
   ```

## Configuration Options

### Basic Configuration

```yaml
LLM_PROVIDER: anthropic
LLM_MODEL_NAME: claude-3-haiku-20240307
```

### Advanced Configuration

```yaml
# Custom API endpoint (if using proxy)
ANTHROPIC_BASE_URL: https://api.anthropic.com

# Custom API version
ANTHROPIC_API_VERSION: 2023-06-01
```

## Troubleshooting

### Common Issues

1. **"Invalid API key"**
   - Verify API key format: `sk-ant-...`
   - Check account status and credits
   - Ensure API access is enabled

2. **"Rate limit exceeded"**
   - Anthropic has generous rate limits
   - Implement exponential backoff
   - Contact support for higher limits

3. **"Context too long"**
   - Claude handles very large contexts well
   - Consider reducing file context if needed
   - Use appropriate model for your needs

