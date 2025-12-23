<div align="center">
  <img src="https://avatars.githubusercontent.com/u/148330874?s=200&v=4" alt="DeepSeek Logo" height="64" />
</div>

# DeepSeek Provider

DeepSeek offers specialized code-focused models at competitive prices, optimized for programming tasks.

## Setup

1. **Get API Key**: Sign up at [DeepSeek Platform](https://platform.deepseek.com/)

2. **Set Environment Variable**:

Set **DEEPSEEK_API_KEY=your-deepseek-api-key** in your CI/CD secret variables.

> Make sure the secret variable is sent to MegaLinter from your CI/CD workflow. Example in GitHub Action: `DEEPSEEK_API_KEY: ${{ secrets.DEEPSEEK_API_KEY }}`

1. **Configure MegaLinter**:

```yaml
LLM_ADVISOR_ENABLED: true
LLM_PROVIDER: deepseek
LLM_MODEL_NAME: deepseek-chat
LLM_MAX_TOKENS: 1000
LLM_TEMPERATURE: 0.1
```

## Official Model List

For the most up-to-date list of DeepSeek models and their capabilities, see the official DeepSeek documentation:

- [DeepSeek Model List](https://platform.deepseek.com/docs/model)

## Configuration Options

### Basic Configuration

```yaml
LLM_PROVIDER: deepseek
LLM_MODEL_NAME: deepseek-chat       # or deepseek-coder
```

### Advanced Configuration

```yaml
# Custom API endpoint (if needed)
DEEPSEEK_BASE_URL: https://api.deepseek.com/v1
```

## Troubleshooting

### Common Issues

1. **"Invalid API key"**

   - Verify your API key is correct
   - Check account status and credits
   - Ensure API access is enabled

2. **"Rate limit exceeded"**

   - Check your plan's rate limits
   - Implement rate limiting in your requests
   - Consider upgrading your plan

3. **"Model not available"**

   - Verify model name is correct
   - Check if model is available in your region
   - Some models may require special access

