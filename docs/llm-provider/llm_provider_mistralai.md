# Mistral AI Provider

Mistral AI provides high-quality language models with European data residency and competitive pricing.

## Supported Models

| Model                   | Context Length | Cost | Best For                |
|-------------------------|----------------|------|-------------------------|
| `mistral-small-latest`  | 32K tokens     | $    | Cost-effective analysis |
| `mistral-medium-latest` | 32K tokens     | $$   | Balanced performance    |
| `mistral-large-latest`  | 32K tokens     | $$$  | Highest quality         |

## Setup

1. **Get API Key**: Sign up at [Mistral AI Console](https://console.mistral.ai/)
2. **Set Environment Variable**:
   ```bash
   export MISTRAL_API_KEY=your-mistral-api-key
   ```
3. **Configure MegaLinter**:
   ```yaml
   LLM_ADVISOR_ENABLED: true
   LLM_PROVIDER: mistral
   LLM_MODEL_NAME: mistral-small-latest
   LLM_MAX_TOKENS: 1000
   LLM_TEMPERATURE: 0.1
   ```

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

## Model Recommendations

- **Development**: `mistral-small-latest` - Cost-effective for testing
- **Production**: `mistral-medium-latest` - Good balance of quality and cost
- **Complex Analysis**: `mistral-large-latest` - Best quality for difficult issues

## Advantages

- **European Provider**: Data residency in Europe
- **Competitive Pricing**: Good value for performance
- **Fast Responses**: Quick analysis and suggestions
- **Open Source Heritage**: Based on open research

## Cost Considerations

Mistral offers transparent, competitive pricing:
- Clear per-token pricing
- No hidden fees
- Monitor usage in Mistral console

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

## Best Practices

- Start with `mistral-small-latest` for development
- Use `mistral-medium-latest` for production workloads
- Monitor usage to optimize costs
- Set temperature between 0.1-0.3 for technical tasks
