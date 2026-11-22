<div align="center">
  <img src="https://openai.com/favicon.ico" alt="OpenAI Logo" height="64" />
</div>

# OpenAI Provider

OpenAI provides state-of-the-art language models offering excellent code analysis and fix suggestions.

## Setup

1. **Get API Key**: Sign up at [OpenAI Platform](https://platform.openai.com/)

2. **Set Environment Variable**:

Set **OPENAI_API_KEY=sk-your-api-key-here** in your CI/CD secret variables.

> Make sure the secret variable is sent to MegaLinter from your CI/CD workflow. Example in GitHub Action: `OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}`

3. **Configure MegaLinter**:

```yaml
LLM_ADVISOR_ENABLED: true
LLM_PROVIDER: openai
LLM_MODEL_NAME: gpt-4.1-mini
LLM_MAX_TOKENS: 1000
LLM_TEMPERATURE: 0.1
```

## Official Model List

For the most up-to-date list of OpenAI models and their capabilities, see the official OpenAI documentation:

- [OpenAI Model List](https://platform.openai.com/docs/models)

## Configuration Options

### Basic Configuration

```yaml
LLM_PROVIDER: openai
LLM_MODEL_NAME: gpt-4.1-mini      # or gpt-4o-mini, gpt-4o
```

### Advanced Configuration

```yaml
# Custom API endpoint (proxy, gateway or self-hosted OpenAI-compatible server)
OPENAI_BASE_URL: https://api.openai.com/v1

# Organization ID (optional)
OPENAI_ORGANIZATION: org-your-org-id
```

### Using an OpenAI-compatible gateway

Any service exposing an OpenAI-compatible `/chat/completions` API (LLM gateways, routers, proxies, self-hosted servers like vLLM or LiteLLM) works with this provider, without a dedicated MegaLinter provider.

Keep `LLM_PROVIDER: openai`, send the gateway's API key as `OPENAI_API_KEY`, and set `OPENAI_BASE_URL` to the gateway URL, including its version segment (usually `/v1`):

```yaml
LLM_ADVISOR_ENABLED: true
LLM_PROVIDER: openai
LLM_MODEL_NAME: gpt-5.6-sol    # any model name exposed by the gateway
OPENAI_BASE_URL: https://global.api-route.com/v1
```

Notes:

- `OPENAI_API_KEY` must contain the **gateway's** key, not an OpenAI key
- `LLM_MODEL_NAME` must be the model identifier expected by the gateway
- The request is sent to `OPENAI_BASE_URL` + `/chat/completions`
- See [API Endpoint Configuration](../llm-advisor.md#api-endpoint-configuration) for the base URL variables of the other providers

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
