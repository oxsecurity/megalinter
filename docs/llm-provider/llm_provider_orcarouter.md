<div align="center">
  <img src="https://www.orcarouter.ai/favicon.ico" alt="OrcaRouter Logo" height="64" />
</div>

# OrcaRouter Provider

[OrcaRouter](https://www.orcarouter.ai) is an OpenAI-compatible AI gateway built for both models and agents. Like OpenRouter, it exposes a provider/model namespace across many models — but it also combines adaptive routing, automatic failover, zero-markup inference, observability, guardrails, and agent-tool governance behind the same endpoint. It uses the OpenAI-compatible API format.

## Setup

1. **Get API Key**: Sign up at [OrcaRouter](https://www.orcarouter.ai)

2. **Set Environment Variable**:

Set **ORCAROUTER_API_KEY=sk-orca-your-api-key** in your CI/CD secret variables.

> Make sure the secret variable is sent to MegaLinter from your CI/CD workflow. Example in GitHub Action: `ORCAROUTER_API_KEY: ${{ secrets.ORCAROUTER_API_KEY }}`

3. **Configure MegaLinter**:

```yaml
LLM_ADVISOR_ENABLED: true
LLM_PROVIDER: orcarouter
LLM_MODEL_NAME: orcarouter/fusion-mini
LLM_MAX_TOKENS: 1000
LLM_TEMPERATURE: 0.1
```

## Official Model List

For the most up-to-date list of OrcaRouter models and their capabilities, see the official OrcaRouter documentation:

- [OrcaRouter Models](https://www.orcarouter.ai/models)

## Configuration Options

### Basic Configuration

```yaml
LLM_PROVIDER: orcarouter
LLM_MODEL_NAME: orcarouter/fusion-mini
```

### Advanced Configuration

```yaml
# Custom API endpoint (if needed)
ORCAROUTER_BASE_URL: https://api.orcarouter.ai/v1
```

## Troubleshooting

### Common Issues

1. **"Invalid API key"**

   - Verify API key is correct
   - Check account status and access
   - Ensure OrcaRouter API access is enabled

2. **"Rate limit exceeded"**

   - Check your plan's rate limits
   - Implement exponential backoff
   - Contact OrcaRouter support for higher limits

3. **"Model not available"**

   - Verify model name: `orcarouter/fusion-mini`
   - Check the model list at [OrcaRouter Models](https://www.orcarouter.ai/models)
   - Ensure you have access to the model

### Debug Mode

```yaml
LOG_LEVEL: DEBUG
```
