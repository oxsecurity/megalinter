<div align="center">
  <img src="https://mistral.ai/favicon.ico" alt="Mistral AI Logo" style="max-width: 120px; margin-bottom: 1em;" />
</div>

# Mistral AI Provider

Mistral AI provides high-quality language models with European data residency and competitive pricing.

## Setup

1. **Get API Key**: Sign up at [Mistral AI Console](https://console.mistral.ai/)

2. **Set Environment Variable**:

Set **MISTRAL_API_KEY=your-mistral-api-key** in your CI/CD secret variables.

> Make sure the secret variable is sent to MegaLinter from your CI/CD workflow. Example in GitHub Action: `MISTRAL_API_KEY: ${{ secrets.MISTRAL_API_KEY }}`

1. **Configure MegaLinter**:

```yaml
LLM_ADVISOR_ENABLED: true
LLM_PROVIDER: mistral
LLM_MODEL_NAME: mistral-small-latest
LLM_MAX_TOKENS: 1000
LLM_TEMPERATURE: 0.1
```

## Official Model List

For the most up-to-date list of Mistral models and their capabilities, see the official Mistral AI documentation:

- [Mistral AI Model List](https://docs.mistral.ai/platform/endpoints/)

## Configuration Options

### Basic Configuration

```yaml
LLM_PROVIDER: mistral
LLM_MODEL_NAME: mistral-small-latest
```

### Advanced Configuration

```yaml
# Custom API endpoint (rarely needed)
MISTRAL_BASE_URL: https://api.mistral.ai
```

## Troubleshooting

### Common Issues

1. **"Authentication failed"**

   - Verify your API key is correct
   - Check account status and credits
   - Ensure proper permissions

2. **"Rate limit exceeded"**

   - Check your plan's limits
   - Implement exponential backoff
   - Contact support for higher limits

3. **"Model not found"**

   - Use latest model names
   - Check availability in your region
   - Verify spelling and format

