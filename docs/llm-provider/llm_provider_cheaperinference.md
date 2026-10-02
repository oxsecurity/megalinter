<div align="center">
  <img src="https://www.cheaperinference.com/icon.svg" alt="Cheaper Inference Logo" height="64" />
</div>

# Cheaper Inference Provider

[Cheaper Inference](https://cheaperinference.com) is an OpenAI-compatible LLM gateway. One API key gives access to models from several labs, such as GPT, Claude, Gemini, DeepSeek and GLM. It uses the OpenAI-compatible API format.

## Setup

1. **Get API Key**: Sign up at [Cheaper Inference](https://cheaperinference.com/signup)

2. **Set Environment Variable**:

Set **CHEAPER_INFERENCE_API_KEY=ci_live_your-api-key** in your CI/CD secret variables.

> Make sure the secret variable is sent to MegaLinter from your CI/CD workflow. Example in GitHub Action: `CHEAPER_INFERENCE_API_KEY: ${{ secrets.CHEAPER_INFERENCE_API_KEY }}`

3. **Configure MegaLinter**:

```yaml
LLM_ADVISOR_ENABLED: true
LLM_PROVIDER: cheaperinference
LLM_MODEL_NAME: gpt-5.4-mini
LLM_MAX_TOKENS: 1000
LLM_TEMPERATURE: 0.1
```

## Official Model List

For the most up-to-date list of Cheaper Inference models and their capabilities, see the official Cheaper Inference documentation:

- [Cheaper Inference Models](https://cheaperinference.com/markets)
- [Cheaper Inference Docs](https://cheaperinference.com/docs)

## Configuration Options

### Basic Configuration

```yaml
LLM_PROVIDER: cheaperinference
LLM_MODEL_NAME: gpt-5.4-mini
```

### Advanced Configuration

```yaml
# Custom API endpoint (if needed)
CHEAPER_INFERENCE_BASE_URL: https://api.cheaperinference.com/v1
```

## Troubleshooting

### Common Issues

1. **"Invalid API key"**

   - Verify API key is correct
   - Check account status and access
   - Ensure your wallet has a positive balance

2. **"Rate limit exceeded"**

   - Check your account rate limits
   - Implement exponential backoff
   - Contact Cheaper Inference support for higher limits

3. **"Model not available"**

   - Verify model name: `gpt-5.4-mini`
   - Check the model list at [Cheaper Inference Models](https://cheaperinference.com/markets)
   - Ensure you have access to the model

### Debug Mode

```yaml
LOG_LEVEL: DEBUG
```
