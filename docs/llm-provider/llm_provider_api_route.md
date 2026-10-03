<div align="center">
  <img src="https://www.api-route.com/favicon.ico" alt="API Route Logo" height="64" />
</div>

# API Route Provider

[API Route](https://www.api-route.com) is an OpenAI-compatible multi-model AI API gateway. It provides one base URL and API key for accessing models from multiple providers, including GPT, Claude, Gemini, Kimi, and Qwen.

## Setup

1. **Get API Key**: Sign in to [API Route](https://www.api-route.com) and create an API key.

2. **Set Environment Variable**:

Set **API_ROUTE_API_KEY=your-api-key** in your CI/CD secret variables.

> Make sure the secret variable is sent to MegaLinter from your CI/CD workflow. Example in GitHub Action: `API_ROUTE_API_KEY: ${{ secrets.API_ROUTE_API_KEY }}`

3. **Configure MegaLinter**:

```yaml
LLM_ADVISOR_ENABLED: true
LLM_PROVIDER: api-route
LLM_MODEL_NAME: gpt-5.6-sol
LLM_MAX_TOKENS: 1000
LLM_TEMPERATURE: 0.1
```

## Model List

For the current list of models available through API Route, see:

- [API Route Pricing and Models](https://www.api-route.com/pricing)

## Configuration Options

### Basic Configuration

```yaml
LLM_PROVIDER: api-route
LLM_MODEL_NAME: gpt-5.6-sol
```

### Advanced Configuration

```yaml
# Custom API endpoint (if needed)
API_ROUTE_BASE_URL: https://global.api-route.com/v1
```

## Troubleshooting

### Common Issues

1. **"Invalid API key"**

   - Verify `API_ROUTE_API_KEY` is correct
   - Check that the key is active and has available balance

2. **"Rate limit exceeded"**

   - Check your API Route usage and rate limits
   - Retry with appropriate backoff

3. **"Model not available"**

   - Verify the value of `LLM_MODEL_NAME`
   - Check the current model list on the [API Route pricing page](https://www.api-route.com/pricing)

### Debug Mode

```yaml
LOG_LEVEL: DEBUG
```
