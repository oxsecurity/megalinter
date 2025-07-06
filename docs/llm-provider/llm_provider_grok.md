# Grok Provider

Grok is xAI's conversational AI model, designed for real-time information and engaging interactions. It uses the OpenAI-compatible API format.

## Setup

1. **Get API Key**: Sign up at [xAI Console](https://console.x.ai/)

2. **Set Environment Variable**:

   ```bash
   export GROK_API_KEY=your-grok-api-key
   ```

3. **Configure MegaLinter**:

   ```yaml
   LLM_ADVISOR_ENABLED: true
   LLM_PROVIDER: grok
   LLM_MODEL_NAME: grok-beta
   LLM_MAX_TOKENS: 1000
   LLM_TEMPERATURE: 0.1
   ```

## Official Model List

For the most up-to-date list of Grok models and their capabilities, see the official xAI documentation:

- [xAI Grok Model List](https://docs.x.ai/docs/models)

## Configuration Options

### Basic Configuration

```yaml
LLM_PROVIDER: grok
LLM_MODEL_NAME: grok-beta
```

### Advanced Configuration

```yaml
# Custom API endpoint (if needed)
GROK_BASE_URL: https://api.x.ai/v1
```

## Troubleshooting

### Common Issues

1. **"Invalid API key"**
   - Verify API key is correct
   - Check account status and access
   - Ensure Grok API access is enabled

2. **"Rate limit exceeded"**
   - Check your plan's rate limits
   - Implement exponential backoff
   - Contact xAI support for higher limits

3. **"Model not available"**
   - Verify model name: `grok-beta`
   - Check regional availability
   - Ensure you have access to the model

### Debug Mode

```yaml
LOG_LEVEL: DEBUG
```
